# bot/handlers/motion_handler.py
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from bot.config import ADMIN_ID
from bot.rtsp_motion_detector import run_rtsp_detector


async def motion_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Включает анализ движения"""
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Нет прав для этой команды")
        return

    # Используем bot_data для хранения состояния
    if context.bot_data.get('motion_enabled', False):
        await update.message.reply_text("📹 Детектор уже работает")
        return

    context.bot_data['motion_enabled'] = True

    # Запускаем детектор в фоновой задаче
    if 'motion_task' not in context.bot_data:
        context.bot_data['motion_task'] = asyncio.create_task(
            run_rtsp_detector(context.bot, lambda: context.bot_data.get('motion_enabled', False))
        )

    await update.message.reply_text("✅ Детектор движения включён")


async def motion_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выключает анализ движения"""
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Нет прав для этой команды")
        return

    if not context.bot_data.get('motion_enabled', False):
        await update.message.reply_text("⏹ Детектор и так выключен")
        return

    context.bot_data['motion_enabled'] = False

    # Отменяем задачу если она существует
    if 'motion_task' in context.bot_data:
        context.bot_data['motion_task'].cancel()
        try:
            await context.bot_data['motion_task']
        except asyncio.CancelledError:
            pass
        del context.bot_data['motion_task']

    await update.message.reply_text("⏹ Детектор движения выключен")


# Функция для проверки состояния (если нужна из других модулей)
def is_motion_enabled(context: ContextTypes.DEFAULT_TYPE) -> bool:
    return context.bot_data.get('motion_enabled', False)