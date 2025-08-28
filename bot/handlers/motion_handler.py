# bot/handlers/motion_handler.py
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from bot.config import ADMIN_ID
from rtsp_motion_detector import run_rtsp_detector

# Глобальные флаги
MOTION_ENABLED = False
MOTION_TASK = None

def motion_enabled() -> bool:
    """Возвращает текущее состояние (вкл/выкл)"""
    return MOTION_ENABLED

async def motion_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Включает анализ движения"""
    global MOTION_ENABLED, MOTION_TASK

    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return

    if MOTION_ENABLED:
        await update.message.reply_text("📹 Детектор уже работает")
        return

    MOTION_ENABLED = True
    MOTION_TASK = context.application.create_task(run_rtsp_detector(context.bot, motion_enabled))
    await update.message.reply_text("✅ Детектор движения включён")

async def motion_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выключает анализ движения"""
    global MOTION_ENABLED, MOTION_TASK

    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return

    if not MOTION_ENABLED:
        await update.message.reply_text("⏹ Детектор и так выключен")
        return

    MOTION_ENABLED = False
    if MOTION_TASK:
        MOTION_TASK.cancel()
        try:
            await MOTION_TASK
        except asyncio.CancelledError:
            pass
        MOTION_TASK = None

    await update.message.reply_text("⏹ Детектор движения выключен")
