import asyncio
import time
from telegram import Update
from telegram.ext import ContextTypes
from bot.config import ADMIN_ID, MOTION_COOLDOWN_SECONDS, MOTION_FRAME_SKIP, MOTION_MIN_AREA, RECONNECT_MAX_DELAY, \
    HEALTH_TIMEOUT
from bot.rtsp_motion_detector import run_rtsp_detector
import logging


logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

# Глобальный словарь для отслеживания cooldown уведомлений
motion_notification_cooldown = {}


async def send_motion_alert_with_cooldown(bot, chat_id, photo_data, caption):
    """Отправка уведомления о движении с учетом cooldown"""
    current_time = time.time()

    # Проверяем cooldown для данного чата
    # if (chat_id in motion_notification_cooldown and
    #         current_time - motion_notification_cooldown[chat_id] < MOTION_COOLDOWN_SECONDS):
    #     logging.info(f"Уведомление пропущено из-за cooldown ({MOTION_COOLDOWN_SECONDS}s)")
    #     return False

    try:
        await bot.send_photo(chat_id=chat_id, photo=photo_data, caption=caption)
        motion_notification_cooldown[chat_id] = current_time
        logging.info(f"Уведомление отправлено с cooldown {MOTION_COOLDOWN_SECONDS}s")
        return True
    except Exception as e:
        logging.error(f"Ошибка отправки уведомления: {e}")
        return False


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
        # Передаем функцию send_motion_alert_with_cooldown в детектор
        context.bot_data['motion_task'] = asyncio.create_task(
            run_rtsp_detector(
                context.bot,
                lambda: context.bot_data.get('motion_enabled', False),
                send_motion_alert_with_cooldown
            )
        )
        logging.info("Motion detector task started with optimizations for multiple cameras")

    await update.message.reply_text(
        f"✅ Детектор движения включён\n"
        f"🔧 Оптимизации: анализ каждого {MOTION_FRAME_SKIP}-го кадра\n"
        f"⏰ Cooldown уведомлений: {MOTION_COOLDOWN_SECONDS}s\n"
        f"📹 Камеры будут запущены параллельно"
    )


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

    # Очищаем cooldown при выключении
    global motion_notification_cooldown
    motion_notification_cooldown.clear()

    await update.message.reply_text("⏹ Детектор движения выключен")


async def motion_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать статус детектора движения"""
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Нет прав для этой команды")
        return

    enabled = context.bot_data.get('motion_enabled', False)
    status = "🟢 Включён" if enabled else "🔴 Выключен"

    # Подсчитываем количество активных камер
    from bot.rtsp_motion_detector import active_camera_tasks
    active_cameras = len([task for task in active_camera_tasks if not task.done()])

    # await update.message.reply_text(
    #     f"📊 Статус детектора: {status}\n"
    #     f"📹 Активных камер: {active_cameras}\n"
    #     f"🔧 Анализ кадров: каждый {MOTION_FRAME_SKIP}-й\n"
    #     f"⏰ Cooldown: {MOTION_COOLDOWN_SECONDS}s\n"
    #     f"📏 Мин. площадь: {MOTION_MIN_AREA}px"
    # )

    await update.message.reply_text(
        f"📊 Статус детектора: {status}\n"
        f"📹 Активных камер: {active_cameras}\n"
        f"🔧 Анализ кадров: каждый {MOTION_FRAME_SKIP}-й\n"
        f"⏰ Cooldown: {MOTION_COOLDOWN_SECONDS}s\n"
        f"📏 Мин. площадь: {MOTION_MIN_AREA}px\n"
        f"🔄 Reconnect max delay: {RECONNECT_MAX_DELAY}s\n"  # Добавьте это
        f"🛡️ Health timeout: {HEALTH_TIMEOUT}s"
    )


# Функция для проверки состояния (если нужна из других модулей)
def is_motion_enabled(context: ContextTypes.DEFAULT_TYPE) -> bool:
    return context.bot_data.get('motion_enabled', False)


async def show_container_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать последние логи контейнера"""
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Нет прав для этой команды")
        return

    try:
        # Получаем последние 50 строк лога
        log_lines = []
        try:
            with open('motion_debug.log', 'r', encoding='utf-8') as f:
                lines = f.readlines()
                log_lines = lines[-50:]  # Последние 50 строк
        except FileNotFoundError:
            log_lines = ["Лог-файл не найден"]

        log_text = "".join(log_lines)

        # Разбиваем на части если лог слишком большой для Telegram
        if len(log_text) > 4000:
            log_text = log_text[-4000:]  # Берем последние 4000 символов

        await update.message.reply_text(f"📋 Последние логи:\n```\n{log_text}\n```",
                                        parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Ошибка чтения логов: {e}")
        await update.message.reply_text(f"❌ Ошибка чтения логов: {e}")