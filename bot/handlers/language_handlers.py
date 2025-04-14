# language_handlers.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from ..auth import is_authorized, is_admin
from ..data import pending_requests
from ..handlers.common_handlers import load_user_settings, save_user_settings, build_menu_keyboard
from ..language_texts import texts
from ..utils import notify_admin


# Обработчик для выбора языка через инлайн-кнопки
async def language_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    chosen_lang = query.data  # 'ru' или 'en'
    context.user_data['language'] = chosen_lang

    user_id = update.effective_user.id
    # Сохраняем настройки пользователя
    user_settings = load_user_settings()
    user_settings[str(user_id)] = {'language': chosen_lang}
    save_user_settings(user_settings)

    # Если пользователь не авторизован, можно отправить уведомление и завершить
    if not (is_admin(user_id) or is_authorized(user_id)):
        if user_id not in pending_requests:
            pending_requests.add(user_id)
            await notify_admin(context, user_id)
        await query.edit_message_text(texts[chosen_lang]['request_received'])
        return

    # Получаем меню с inline-клавиатурой
    reply_markup = build_menu_keyboard(chosen_lang, user_id)
    welcome_text = texts[chosen_lang]['admin_welcome'] if is_admin(user_id) else texts[chosen_lang]['user_welcome']

    # Отправляем новое сообщение с меню
    await context.bot.send_message(
        chat_id=user_id,
        text=welcome_text,
        reply_markup=reply_markup
    )


async def change_language_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды для смены языка.
    Отправляет пользователю инлайн-клавиатуру с выбором языка.
    """
    # Попытаемся определить текущий язык из сохранённых настроек
    user_id = update.effective_user.id
    user_settings = load_user_settings()
    current_lang = texts.get('ru')  # значение по умолчанию
    if str(user_id) in user_settings:
        chosen_lang = user_settings[str(user_id)].get('language', 'ru')
    else:
        chosen_lang = 'ru'

    # Создаём инлайн-клавиатуру для смены языка
    inline_keyboard = [
        [
            InlineKeyboardButton(text="Русский", callback_data="ru"),
            InlineKeyboardButton(text="English", callback_data="en")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard)
    await context.bot.send_message(
        chat_id=user_id,
        text=texts[chosen_lang].get('choose_language', 'Выберите язык / Choose language:'),
        reply_markup=reply_markup
    )