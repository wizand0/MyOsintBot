# utils.py
import asyncio

from .config import ADMIN_ID, logger
from telegram.ext import ContextTypes
from datetime import datetime, timezone
from telegram import Bot
import logging

from .language_texts import texts

logger1 = logging.getLogger(__name__)


async def notify_admin(context: ContextTypes.DEFAULT_TYPE, applicant_id: int):
    # Получаем выбранный язык
    lang = context.user_data['language']


    try:
        text1 = texts[lang].get("approve_user", "Новая заявка на доступ(для доступа укажите: /approve 123456789):")
        message = f"{text1} {applicant_id}"

        await context.bot.send_message(chat_id=ADMIN_ID, text=message)
    except Exception as e:
        logger.error(f"Ошибка уведомления администратора: {e}")


async def notify_startup(bot: Bot):
    try:
        # now = datetime.utcnow().strftime("%Y‑%m‑%d %H:%M:%S UTC")
        now = datetime.now(timezone.utc).strftime("%Y‑%m‑%d %H:%M:%S UTC")
        text = f"✅ Бот запущен на сервере. Время: {now}"
        await bot.send_message(chat_id=ADMIN_ID, text=text)
    except Exception as e:
        logger1.error("Не удалось отправить уведомление о старте: %s", e)


async def notify_startup_try_if_no_internet(bot: Bot):
    # Подготовка текста с таймзоной UTC
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    text = f"✅ Бот запущен на сервере. Время: {now}"

    # Список задержек перед повторными попытками (секунды)
    delays = [0, 30, 600]  # 0 — сразу, 30 с, 600 с = 10 мин

    for idx, delay in enumerate(delays):
        if delay:
            logger.info("Ждём %s секунд перед попыткой #%d отправки", delay, idx + 1)
            await asyncio.sleep(delay)

        try:
            await bot.send_message(chat_id=ADMIN_ID, text=text)
            logger.info("Уведомление о старте успешно отправлено (попытка #%d)", idx + 1)
            break
        except Exception as e:
            logger.error(
                "Провалена попытка #%d отправить уведомление: %s",
                idx + 1, e, exc_info=True
            )
    else:
        # Этот блок выполнится, если цикл завершился без break
        logger.critical(
            "Не удалось отправить уведомление о старте ни одной из попыток"
        )
