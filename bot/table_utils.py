from tabulate import tabulate
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode


# Функция отправки ASCII-таблицы в сообщении (результат небольшой длины)
async def send_results_message(update: Update, table: str) -> None:
    # Заворачиваем таблицу в тег <pre> для корректного отображения моноширинным шрифтом
    text_message = f"<pre>{table}</pre>"
    await update.message.reply_text(text_message, parse_mode=ParseMode.HTML)


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