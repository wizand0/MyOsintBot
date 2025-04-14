# admin_handlers.py

from telegram import Update
from telegram.ext import ContextTypes

from ..auth import is_admin
from ..config import ALLOWED_USERS, logger
from ..language_texts import texts
from ..data import pending_requests  # импортируем список заявок


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