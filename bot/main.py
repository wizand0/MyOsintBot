# main.py

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters, CallbackQueryHandler,
)

from bot.db import init_db_pool, close_db_pool
from bot.handlers.bot_core import start
from .handlers.common_handlers import callback_handler
from .handlers.admin_handlers import approve_user, delete_user, stats_handler
from .handlers.language_handlers import language_selection_handler, change_language_handler
from .handlers.user_handlers import message_handler
from .config import TOKEN
from .utils import notify_startup, notify_startup_try_if_no_internet
from bot.handlers.common_handlers import on_motion_on_text, on_motion_off_text
from bot.handlers.motion_handler import motion_on, motion_off


# from .handlers import start, message_handler, approve_user, language_selection_handler, change_language_handler, \
#     callback_handler

async def on_startup_callback(context):
    # Telegram‑бота можно получить из context.bot
    await notify_startup_try_if_no_internet(context.bot)
    # await notify_startup(context.bot)

stats_cmd = CommandHandler("stats", stats_handler)


async def on_startup(app):
    # создаём пул, сохраняем в bot_data
    app.bot_data["db_pool"] = await init_db_pool()
    await notify_startup_try_if_no_internet(app.bot)

async def on_shutdown(app):
    # корректно закрываем пул
    pool = app.bot_data.get("db_pool")
    if pool:
        await close_db_pool(pool)


def main():
    application = (ApplicationBuilder()
                   .token(TOKEN)
                   # v20+: post_init и post_shutdown
                   .post_init(on_startup)
                   .post_shutdown(on_shutdown)
                   .build())
    # Обработчик команды /start
    application.add_handler(CommandHandler("start", start))
    # Обработчик для одобрения заявки через команду /approve 123456789 (только для админа)
    application.add_handler(CommandHandler("approve", approve_user))
    # Обработчик для одобрения заявки через команду /delete 123456789 (только для админа)
    application.add_handler(CommandHandler("delete", delete_user))

    # ДОБАВЬТЕ ОБРАБОТЧИКИ MOTION ПЕРЕД ОБЩИМ ОБРАБОТЧИКОМ ТЕКСТА
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^▶️ Motion ON$"), motion_on))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^⏹ Motion OFF$"), motion_off))

    # Обработка всех текстовых сообщений (должен идти ПОСЛЕ специализированных обработчиков)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # Регистрируем обработчик на CallbackQuery для выбора языка
    # Регистрируем обработчик для выбора языка ('ru' или 'en')
    application.add_handler(CallbackQueryHandler(language_selection_handler, pattern="^(ru|en)$"))
    # Регистрируем обработчик для смены языка (callback_data = "change_language")
    application.add_handler(CallbackQueryHandler(change_language_handler, pattern="^change_language$"))
    # Регистрируем обработчики команд и callback query
    application.add_handler(CallbackQueryHandler(callback_handler))

    application.add_handler(stats_cmd)

    # Планируем единоразовый job на 5‑й секунде
    application.job_queue.run_once(on_startup_callback, when=5)

    # Запуск бота
    application.run_polling()


if __name__ == '__main__':
    main()
