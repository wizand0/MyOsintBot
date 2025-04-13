# main.py

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

from .config import TOKEN, logger
from .handlers import start, message_handler, approve_user


# def main() -> None:
#     application = ApplicationBuilder().token(TOKEN).build()
#
#     application.add_handler(CommandHandler("start", start))
#     application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
#
#     logger.info("Бот запущен")
#     application.run_polling()
#
#
# if __name__ == '__main__':
#     main()


def main():
    application = ApplicationBuilder().token(TOKEN).build()
    # Обработчик команды /start
    application.add_handler(CommandHandler("start", start))
    # Обработчик для одобрения заявки через команду /approve 123456789 (только для админа)
    application.add_handler(CommandHandler("approve", approve_user))
    # Обработка всех текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # Запуск бота
    application.run_polling()


if __name__ == '__main__':
    main()