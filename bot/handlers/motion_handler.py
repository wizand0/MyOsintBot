# bot/handlers/motion_handler.py
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from bot.config import ADMIN_ID
from bot.rtsp_motion_detector import run_rtsp_detector
import logging


logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

async def motion_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("motion_on handler called")
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        logging.info(f"User {user_id} attempted to use motion_on but is not admin")
        await update.message.reply_text("❌ Нет прав для этой команды")
        return

    if context.bot_data.get('motion_enabled', False):
        logging.info("Motion detector already enabled")
        await update.message.reply_text("📹 Детектор уже работает")
        return

    context.bot_data['motion_enabled'] = True

    if 'motion_task' not in context.bot_data:
        context.bot_data['motion_task'] = asyncio.create_task(
            run_rtsp_detector(context.bot, lambda: context.bot_data.get('motion_enabled', False))
        )
        logging.info("Motion detector task started")

    await update.message.reply_text("✅ Детектор движения включён")

async def motion_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("motion_off handler called")
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        logging.info(f"User {user_id} attempted to use motion_off but is not admin")
        await update.message.reply_text("❌ Нет прав для этой команды")
        return

    if not context.bot_data.get('motion_enabled', False):
        logging.info("Motion detector already disabled")
        await update.message.reply_text("⏹ Детектор и так выключен")
        return

    context.bot_data['motion_enabled'] = False

    if 'motion_task' in context.bot_data:
        context.bot_data['motion_task'].cancel()
        try:
            await context.bot_data['motion_task']
        except asyncio.CancelledError:
            logging.info("Motion detector task cancelled")
        del context.bot_data['motion_task']

    await update.message.reply_text("⏹ Детектор движения выключен")


# Функция для проверки состояния (если нужна из других модулей)
def is_motion_enabled(context: ContextTypes.DEFAULT_TYPE) -> bool:
    return context.bot_data.get('motion_enabled', False)