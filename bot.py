import os
import logging
import asyncio
import mysql.connector
from mysql.connector import Error
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from tabulate import tabulate
from telegram.constants import ParseMode
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()

# Настройка логирования (вывод в консоль)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Получаем секретные данные из переменных окружения
TOKEN = os.getenv('TOKEN')
DB_CONFIG = {
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'osint_bd'),
    'port': int(os.getenv('DB_PORT', 3306))
}

# Получаем список разрешенных пользователей из переменных окружения
allowed_users_str = os.getenv('ALLOWED_USERS', '')
ALLOWED_USERS = set()
if allowed_users_str:
    # Преобразуем строку вида "123456789,987654321" в множество чисел
    ALLOWED_USERS = {int(x.strip()) for x in allowed_users_str.split(',') if x.strip()}


# Функция для подключения к базе данных
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            port=DB_CONFIG['port'],
            charset='utf8'
        )
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SET NAMES 'utf8';")
            return connection
    except Error as e:
        logger.error(f"Ошибка подключения к базе данных: {e}")
    return None


# Функция проверки прав пользователя
def is_authorized(user_id: int) -> bool:
    return user_id in ALLOWED_USERS


# Обработчик команды /start – вывод меню
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if not is_authorized(user_id):
        await update.message.reply_text(
            "Извините, у вас нет доступа к боту. Обратитесь к администратору."
        )
        return

    menu_keyboard = [
        ['Общий поиск', 'Поиск по номеру телефона'],
        ['Инструкция']
    ]
    reply_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        "Добро пожаловать в OSINT-бот!\nВыберите действие:",
        reply_markup=reply_markup
    )
    # Сбрасываем ранее установленный режим поиска
    context.user_data.pop('search_mode', None)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    # Проверка авторизации
    if not is_authorized(user_id):
        await update.message.reply_text("Извините, у вас нет доступа к боту.")
        return

    text = update.message.text.strip().lower()

    # Обработка команд меню
    if text == "общий поиск":
        context.user_data['search_mode'] = 'general'
        await update.message.reply_text("Введите поисковый запрос для общего поиска:")
        return

    if text == "поиск по номеру телефона":
        context.user_data['search_mode'] = 'phone'
        await update.message.reply_text("Введите номер телефона для поиска:")
        return

    if text == "инструкция":
        instruction = (
            "Инструкция по использованию бота:\n"
            "1. Выберите режим поиска:\n"
            "   • 'Общий поиск' – поиск по текстовым столбцам во всех таблицах базы данных.\n"
            "   • 'Поиск по номеру телефона' – поиск осуществляется только по столбцу phone_number.\n"
            "2. Введите поисковый запрос.\n"
            "3. Бот выполнит поиск и вернет найденные результаты (ограничено 10 записями из каждой таблицы).\n"
            "Если возникнут вопросы, свяжитесь с администратором."
        )
        await update.message.reply_text(instruction)
        return

    # Если пользователь уже выбрал режим поиска, обрабатываем его запрос
    if context.user_data.get('search_mode'):
        query_text = update.message.text.strip()
        mode = context.user_data.get('search_mode')

        # Отправляем сообщение-заглушку для отображения прогресса
        loading_msg = await update.message.reply_text("Идет поиск, пожалуйста, подождите...")
        try:
            # Обновляем прогресс: Подготовка запроса
            progress_msg = "Подготовка запроса..."
            logger.info(progress_msg)
            await loading_msg.edit_text(progress_msg)
            await asyncio.sleep(0.5)

            # Обновляем прогресс: Выполнение запроса в базе данных
            progress_msg = "Выполняется поиск в базе данных..."
            logger.info(progress_msg)
            await loading_msg.edit_text(progress_msg)

            # Запускаем поиск в отдельном потоке
            if mode == 'phone':
                results = await asyncio.to_thread(perform_phone_search, query_text)
            else:  # mode == 'general'
                results = await asyncio.to_thread(perform_general_search, query_text)

            # Обновляем прогресс: Обработка результатов
            progress_msg = "Обработка результатов..."
            logger.info(progress_msg)
            await loading_msg.edit_text(progress_msg)
            await asyncio.sleep(0.5)

            # По завершении поиска удаляем сообщение с индикатором загрузки
            await loading_msg.delete()

            if results:
                # Формирование текстового ответа
                response = "<b>Результаты поиска:</b>\n"
                for row in results:
                    table_name = row.get('table_name', 'unknown')
                    row_data = " | ".join(f"{key}: {value}" for key, value in row.items() if key != 'table_name')
                    response += f"<i>[{table_name}]</i> {row_data}\n"

                # Если текст достаточно компактный – отправляем обычным сообщением
                if len(response) < 3500:
                    await send_results_message(update, response)
                else:
                    # Если результат слишком длинный, сохраняем его как HTML и отправляем файл
                    file_path = await asyncio.to_thread(save_results_as_html, results)
                    with open(file_path, "rb") as file:
                        await update.message.reply_document(
                            document=file,
                            filename="results.html",
                            caption="Результаты поиска слишком длинные, поэтому отправлены в виде HTML-файла."
                        )
            else:
                await update.message.reply_text("Ничего не найдено по вашему запросу.")

        except Exception as e:
            logger.exception("Ошибка при выполнении поиска")
            # При ошибке тоже удаляем сообщение-заглушку
            await loading_msg.delete()
            await update.message.reply_text("Произошла ошибка при выполнении поиска, повторите попытку позже.")

        # Сбрасываем режим поиска после обработки запроса
        context.user_data.pop('search_mode', None)
    else:
        await update.message.reply_text(
            "Пожалуйста, выберите команду из меню или используйте /start для повторного вызова меню."
        )


def perform_general_search(search_query: str):
    connection = get_db_connection()
    if connection is None:
        return None
    results = []
    try:
        cursor = connection.cursor(dictionary=True)
        # Получаем список таблиц в указанной базе данных.
        cursor.execute(
            "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = %s",
            (DB_CONFIG['database'],)
        )
        tables = cursor.fetchall()

        for table in tables:
            table_name = table['TABLE_NAME']
            # Получаем имена текстовых столбцов для текущей таблицы.
            cursor.execute(
                "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s "
                "AND DATA_TYPE IN ('char','varchar','text')",
                (DB_CONFIG['database'], table_name)
            )
            columns_data = cursor.fetchall()
            columns = [row['COLUMN_NAME'] for row in columns_data]
            if not columns:
                continue  # В этой таблице нет текстовых столбцов

            # Формируем условие для поиска по каждому столбцу через LIKE.
            conditions = " OR ".join([f"{col} LIKE %s" for col in columns])
            query = f"SELECT * FROM {table_name} WHERE {conditions} LIMIT 10"
            params = tuple([f"%{search_query}%"] * len(columns))
            try:
                cursor.execute(query, params)
                table_results = cursor.fetchall()
                for row in table_results:
                    row['table_name'] = table_name  # Добавляем информацию, из какой таблицы найден результат
                    results.append(row)
            except Exception as e:
                logger.error(f"Ошибка поиска в таблице {table_name}: {e}")
    except Exception as e:
        logger.error(f"Ошибка выполнения общего поиска: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    return results


# Функция для поиска по номеру телефона
def perform_phone_search(search_query: str):
    logger.info("Начато выполнение поиска по номеру телефона")
    connection = get_db_connection()
    if connection is None:
        logger.info("connection is None")
        return None
    results = []
    try:
        cursor = connection.cursor(dictionary=True)
        # Получаем список таблиц, в которых есть столбец phone_number
        cursor.execute(
            "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.COLUMNS "
            "WHERE TABLE_SCHEMA = %s AND COLUMN_NAME = 'phone_number'",
            (DB_CONFIG['database'],)
        )
        tables = cursor.fetchall()
        for table in tables:

            table_name = table['TABLE_NAME']
            logger.info(f"Поиск по {table_name}")
            query = f"SELECT * FROM {table_name} WHERE phone_number LIKE %s LIMIT 10"
            param = f"%{search_query}%"
            try:
                cursor.execute(query, (param,))
                table_results = cursor.fetchall()
                for row in table_results:
                    row['table_name'] = table_name  # добавляем информацию о таблице
                    results.append(row)
            except Exception as e:
                logger.error(f"Ошибка поиска в таблице {table_name}: {e}")
        cursor.close()
    except Exception as e:
        logger.error(f"Ошибка выполнения поиска по телефону: {e}")
    finally:
        if connection.is_connected():
            connection.close()
    return results


# Пример функции отправки результатов форматированным сообщением
# async def send_results_message(update: Update, text: str) -> None:
#     await update.message.reply_text(text, parse_mode=ParseMode.HTML)


# Функция отправки ASCII-таблицы в сообщении (результат небольшой длины)
async def send_results_message(update: Update, table: str) -> None:
    # Заворачиваем таблицу в тег <pre> для корректного отображения моноширинным шрифтом
    text_message = f"<pre>{table}</pre>"
    await update.message.reply_text(text_message, parse_mode=ParseMode.HTML)


# Пример функции сохранения результатов в HTML-файл
# Функция может быть синхронной, поэтому мы вызываем её через asyncio.to_thread
# def save_results_as_html(results: list) -> str:
#     file_path = "results.html"
#     with open(file_path, "w", encoding="utf-8") as f:
#         f.write("<html><head><meta charset='utf-8'></head><body>")
#         f.write("<h2>Результаты поиска</h2>")
#         for row in results:
#             # Для каждой строки выводим таблицу и пары ключ: значение
#             table_name = row.get('table_name', 'unknown')
#             f.write(f"<p><strong>{table_name}</strong>: ")
#             row_data = " | ".join(f"{key}: {value}" for key, value in row.items() if key != 'table_name')
#             f.write(f"{row_data}</p>")
#         f.write("</body></html>")
#     return file_path


# Функция сохранения результатов в HTML-файл
def save_results_as_html(results: list) -> str:
    file_path = "results.html"
    html_content = build_html_table(results)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    return file_path


def build_ascii_table(results: list) -> str:
    """
        Строит ASCII-таблицу с двумя колонками: "Table Name" и "Record".
        Для каждой записи в results первая колонка — имя таблицы, вторая — строка вида "field: value | ..."
    """
    rows = []
    for row in results:
        table_name = row.get('table_name', 'unknown')
        # Собираем информацию по остальным полям через разделитель " | "
        record = " | ".join(f"{k}: {v}" for k, v in row.items() if k != 'table_name')
        rows.append([table_name, record])
    # Формируем таблицу с помощью tabulate
    table_str = tabulate(rows, headers=["Table Name", "Record"], tablefmt="grid")
    return table_str


# # Функция для формирования HTML-таблицы
# def build_html_table(results: list) -> str:
#     """
#     Строит HTML-страницу с таблицей результатов и базовой стилизацией.
#     """
#     html = """
#     <html>
#       <head>
#         <meta charset='utf-8'>
#         <style>
#           table { border-collapse: collapse; width: 100%; }
#           th, td { border: 1px solid #dddddd; text-align: left; padding: 8px; }
#           th { background-color: #f2f2f2; }
#           tr:nth-child(even) { background-color: #f9f9f9; }
#         </style>
#       </head>
#       <body>
#         <h2>Результаты поиска</h2>
#         <table>
#           <thead>
#             <tr>
#               <th>Table Name</th>
#               <th>Record</th>
#             </tr>
#           </thead>
#           <tbody>
#     """
#     for r in results:
#         table_name = r.get('table_name', 'unknown')
#         record = " | ".join(f"{k}: {v}" for k, v in r.items() if k != 'table_name')
#         html += f"<tr><td>{table_name}</td><td>{record}</td></tr>"
#     html += """
#           </tbody>
#         </table>
#       </body>
#     </html>
#     """
#     return html

def build_html_table(results: list) -> str:
    """
    Строит одну большую HTML-таблицу, в которой записи сгруппированы по именам таблиц.

    Для каждой группы записей:
      • Первая строка — заголовок группы, в ячейке с colspan, равным максимальному числу столбцов записей данной группы.
      • Затем идут строки с данными. Для каждой записи, содержащей дополнительные поля (кроме ключа table_name),
        значения выводятся в отдельных ячейках. Если у разных записей разное число столбцов, более короткую запись
        дополняем пустыми ячейками.

    Возвращаемая строка содержит одну HTML‑таблицу, в которой сначала идут все записи из первой таблицы, затем из
    второй и т.д.
    """

# Группируем записи по полю 'table_name'
    groups = {}
    for row in results:
        table_name = row.get('table_name', 'unknown')
        groups.setdefault(table_name, []).append(row)

    html_table = '<table border="1" cellspacing="0" cellpadding="4">\n'

    # Для каждой группы (таблицы) выводим заголовок и все записи
    for table_name, rows in groups.items():
        group_rows = []
        max_columns = 0  # Определяем максимальное количество столбцов в записях данной группы
        for row in rows:
            # Собираем строку из остальных полей записи
            record = " | ".join(f"{k}: {v}" for k, v in row.items() if k != 'table_name')
            # Разбиваем строку на отдельные столбцы
            cols = [col.strip() for col in record.split("|") if col.strip()]
            max_columns = max(max_columns, len(cols))
            group_rows.append(cols)

        # Если групповых записей нет, установим max_columns в 1, чтобы корректно вывести заголовок.
        if max_columns == 0:
            max_columns = 1

        # Добавляем строку-заголовок для группы (название таблицы)
        html_table += f'  <tr><td colspan="{max_columns}" style="text-align: center;"><b>{table_name}</b></td></tr>\n'

        # Добавляем строки с данными для каждой записи.
        # Если в записи меньше столбцов, дополняем пустыми ячейками до max_columns.
        for cols in group_rows:
            if len(cols) < max_columns:
                cols.extend([""] * (max_columns - len(cols)))
            html_table += "  <tr>" + "".join(f"<td>{col}</td>" for col in cols) + "</tr>\n"

    html_table += "</table>"
    return html_table


def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    logger.info("Бот запущен")
    application.run_polling()


if __name__ == '__main__':
    main()
