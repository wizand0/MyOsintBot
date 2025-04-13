# utils.py
from .config import ADMIN_ID, logger
from telegram.ext import ContextTypes


async def notify_admin(context: ContextTypes.DEFAULT_TYPE, applicant_id: int):
    try:
        message = f"Новая заявка на доступ от пользователя с id: {applicant_id}"
        await context.bot.send_message(chat_id=ADMIN_ID, text=message)
    except Exception as e:
        logger.error(f"Ошибка уведомления администратора: {e}")
