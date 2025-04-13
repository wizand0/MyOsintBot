import asyncio

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

from .auth import is_authorized
from .config import logger
from .search import perform_general_search, perform_phone_search
from .table_utils import send_results_message, save_results_as_html


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
