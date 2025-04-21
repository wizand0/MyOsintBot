# admin_MyOsintBot/bot/handlers/admin_handlers.py
import os
import socket
import time

import psutil
from mysql.connector import Error
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler

from ..auth import is_admin
from ..config import ALLOWED_USERS, logger
from ..data import pending_requests, save_allowed_users  # импортируем список заявок
from ..db import get_db_connection
from ..language_texts import texts

async def db_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Подключается к базе данных через функцию get_db_connection() из db.py,
    получает список таблиц и для каждой таблицы – количество строк.
    Формирует сообщение со статистикой БД и отправляет его в чат.
    """
    stats_message = "Статистика БД:\n"
    connection = get_db_connection()

    if connection is None:
        await update.effective_message.reply_text("Ошибка подключения к базе данных.")
        return

    try:
        cursor = connection.cursor(dictionary=True)
        try:
            # Получаем список таблиц
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            for table_dict in tables:
                # Имя таблицы обычно содержится в значении словаря.
                table_name = list(table_dict.values())[0]
                # Используем обратные кавычки для правильного именования таблицы
                cursor.execute(f"SELECT COUNT(*) AS count FROM `{table_name}`;")
                result = cursor.fetchone()
                count = result['count'] if result else 0
                stats_message += f"• Таблица `{table_name}`: {count} строк\n"
        except Error as e:
            stats_message = f"Ошибка при получении статистики БД: {e}"
        finally:
            cursor.close()
    finally:
        connection.close()
    # Используем reply_text вместо edit_text, чтобы отправить новое сообщение
    await update.effective_message.reply_text(stats_message)


# команды авторизации пользователя администратором
async def approve_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Вспомогательная функция для отправки сообщения,
    # которая учитывает тип обновления (message или callback_query)
    async def send_message(text: str):
        if update.message:
            return await update.message.reply_text(text)
        elif update.callback_query and update.callback_query.message:
            return await update.callback_query.message.reply_text(text)
        else:
            # Если ни message, ни callback_query не доступны,
            # используем chat_id из update.effective_chat
            return await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    # Если язык не выбран, просим пользователя выбрать его через /start
    if 'language' not in context.user_data:
        await send_message(
            "Пожалуйста, выберите язык, выполнив /start; Please, choose language, press /start"
        )
        return

    # Получаем выбранный язык
    lang = context.user_data['language']

    user_id = update.effective_user.id
    if not is_admin(user_id):
        await send_message(texts[lang].get("private_zone", "У вас нет прав для этой команды."))
        return

    # Ожидаем, что администратор передаст id пользователя в виде аргумента команды
    try:
        applicant_id = int(context.args[0])
    except (IndexError, ValueError):
        await send_message(
            texts[lang].get("approve_user", "Укажите корректный id пользователя. Пример: /approve 123456789")
        )
        return

    if applicant_id in pending_requests:
        pending_requests.remove(applicant_id)
        # Добавляем пользователя в список разрешённых. При желании можно обновить файл или базу данных
        ALLOWED_USERS.add(applicant_id)
        text1 = texts[lang].get("user", "Пользователь")
        text2 = texts[lang].get("is_authorizied", "успешно авторизован")
        save_allowed_users(ALLOWED_USERS)
        await send_message(f"{text1} {applicant_id} {text2}.")

        # Опционально: уведомляем пользователя об успешной авторизации
        try:
            await context.bot.send_message(
                chat_id=applicant_id,
                text=texts[lang].get(
                    "your_request_approved",
                    "Ваша заявка одобрена. Теперь вы можете пользоваться ботом."
                )
            )
        except Exception as e:
            logger.error(f"Ошибка уведомления пользователя: {e}")
    else:
        await send_message(
            texts[lang].get("no_user_found", "Пользователь с таким id не найден в заявках.")
        )


# Обработчик для команды «Количество пользователей»
async def show_users_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Функция-обёртка отправки сообщений,
    # выбирающая метод в зависимости от типа обновления.
    async def send_message(text: str):
        if update.message:
            return await update.message.reply_text(text)
        elif update.callback_query:
            # Например, редактируем сообщение у callback query
            return await update.callback_query.edit_message_text(text)
        else:
            # Если ни message, ни callback_query не доступны, отправляем сообщение через контекст бота
            return await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    # Если язык не выбран, просим пользователя выбрать его через /start
    if 'language' not in context.user_data:
        await send_message("Пожалуйста, выберите язык, выполнив /start; Please, choose language, press /start")
        return

    # Получаем выбранный язык
    lang = context.user_data['language']

    user_id = update.effective_user.id
    if not is_admin(user_id):
        await send_message(texts[lang].get("private_zone", "У вас нет прав для этой команды."))
        return

    count = len(ALLOWED_USERS)
    text1 = texts[lang].get("user_amount", "Количество авторизованных пользователей")
    await send_message(f"{text1}: {count}")


async def show_pending_requests(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    def send_message(text: str):
        if update.message:
            return update.message.reply_text(text)
        elif update.callback_query:
            # Изменим текст сообщения, к которому прикреплена inline-кнопка
            return update.callback_query.edit_message_text(text)
        else:
            # Если ни message, ни callback_query не доступны, можно использовать context.bot.send_message()
            return context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    # Если язык не выбран, просим пользователя выбрать его через /start
    if 'language' not in context.user_data:
        await send_message("Пожалуйста, выберите язык, выполнив /start; Please, choose language, press /start")
        return

    # Получаем выбранный язык
    lang = context.user_data['language']

    user_id = update.effective_user.id
    if not is_admin(user_id):
        await send_message(texts[lang].get("private_zone", "У вас нет прав для этой команды."))
        return

    if not pending_requests:
        await send_message(texts[lang].get("no_new_application", "Нет новых заявок."))
        return

    # Отправляем администратору список заявок
    requests_list = "\n".join(str(uid) for uid in pending_requests)
    text1 = texts[lang].get("new_applications", "Новые заявки")
    await send_message(f"{text1}:\n{requests_list}")


async def server_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Получает характеристики сервера, такие как загрузка CPU и температура.
    """
    lang = context.user_data.get('language', 'ru')

    # Получаем загрузку CPU
    cpu_percent = psutil.cpu_percent(interval=1)

    # 2) Внутренний IP
    local_ip = os.getenv("HOST_LAN_IP", "N/A")
    try:
        # способ без DNS-запроса к самому себе
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        local_container_ip = sock.getsockname()[0]
        # local_ip = get_host_ip()
    except Exception:
        local_container_ip = "N/A"
    finally:
        try:
            sock.close()
        except:
            pass

    boot_ts = psutil.boot_time()
    up_seconds = int(time.time() - boot_ts)
    days, rem = divmod(up_seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    uptime_str = f"{days} дн. {hours} ч. {minutes} мин. {seconds} сек."

    # 4) Температуры
    if hasattr(psutil, "sensors_temperatures"):
        temps = psutil.sensors_temperatures()
    else:
        temps = {}

    if temps:
        temp_lines = []
        for sensor_name, entries in temps.items():
            for entry in entries:
                label = entry.label or sensor_name
                temp_lines.append(f"  • {label}: {entry.current}°C")
        temp_message = "\n".join(temp_lines)
    else:
        temp_message = "Информация о температуре недоступна."


# new messages
    message = (
        f"Характеристики сервера:\n"
        f"• Загрузка CPU: {cpu_percent}%\n"
        # f"• Uptime: {uptime_val:.0f} секунд\n" if uptime_val is not None else ""
        f"• Uptime: {uptime_str}\n"
        f"• Температура:\n{temp_message}\n"
        f"• Lan IP:\n{local_ip}\n"
        f"• IP container:\n{local_container_ip}"
    )

    await update.effective_message.reply_text(message)


def read_uptime(uptime_path='/host_uptime'):
    try:
        with open(uptime_path, 'r') as f:
            uptime_value = f.readline().split()[0]
            return float(uptime_value)
    except Exception as e:
        return None

def read_loadavg(loadavg_path='/host_loadavg'):
    try:
        with open(loadavg_path, 'r') as f:
            content = f.read().strip()
            return content  # Или попарсить данные по необходимости
    except Exception as e:
        return None

def get_host_ip() -> str:
    # перебираем все интерфейсы
    for iface_name, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                ip = addr.address
                # исключаем loopback и docker‑сети
                if not ip.startswith("127.") and not ip.startswith("172."):
                    return ip
    return "N/A"


# ---
# 2) show_pending_requests_as_inline – собирает список
#    заявок и рисует для каждой Inline‑кнопку.
# ---
async def show_pending_requests_as_inline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('language', 'ru')

    # TODO: Реализуйте свой способ достать из БД список «новых» заявок
    # здесь просто заглушка:
    pending = show_pending_requests()  # → List[Dict] или List[ВашКласс]

    if not pending:
        await (update.message or update.callback_query).reply_text(
            texts[lang]['no_pending_requests']
        )
        return

    # Собираем клавиатуру: на каждую заявку своя callback_data
    kb = []
    for req in pending:
        # допустим у вас в req есть id и title
        button = InlineKeyboardButton(
            text=f"{req['id']}: {req['title']}",
            callback_data=f"view_req:{req['id']}"
        )
        kb.append([button])

    reply_markup = InlineKeyboardMarkup(kb)

    # Если мы пришли по тексту – update.message, иначе по коллбэку:
    target = update.message or update.callback_query
    if isinstance(target, Update().callback_query.__class__):
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text=texts[lang]['choose_request'],
            reply_markup=reply_markup
        )
    else:
        await target.reply_text(
            texts[lang]['choose_request'],
            reply_markup=reply_markup
        )