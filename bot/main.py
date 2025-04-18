# main.py

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters, CallbackQueryHandler,
)

from .handlers.common_handlers import callback_handler
from .handlers.admin_handlers import approve_user
from .handlers.language_handlers import language_selection_handler, change_language_handler
from .handlers.user_handlers import message_handler
from .handlers.user_handlers import start
from .config import TOKEN

# from .handlers import start, message_handler, approve_user, language_selection_handler, change_language_handler, \
#     callback_handler



# Код до рефакторинга handlers.py в отдельные файлы
def main():
    application = ApplicationBuilder().token(TOKEN).build()
    # Обработчик команды /start
    application.add_handler(CommandHandler("start", start))
    # Обработчик для одобрения заявки через команду /approve 123456789 (только для админа)
    application.add_handler(CommandHandler("approve", approve_user))
    # Обработка всех текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    # Регистрируем обработчик на CallbackQuery для выбора языка
    # Регистрируем обработчик для выбора языка ('ru' или 'en')
    application.add_handler(CallbackQueryHandler(language_selection_handler, pattern="^(ru|en)$"))
    # Регистрируем обработчик для смены языка (callback_data = "change_language")
    application.add_handler(CallbackQueryHandler(change_language_handler, pattern="^change_language$"))
    # Регистрируем обработчики команд и callback query
    application.add_handler(CallbackQueryHandler(callback_handler))

    # Запуск бота
    application.run_polling()


if __name__ == '__main__':
    main()
