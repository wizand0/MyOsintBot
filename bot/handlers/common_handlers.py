# common_handlers.py
import json
import os

from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes

from .admin_handlers import show_pending_requests, show_users_count
from ..auth import is_authorized, is_admin
from ..config import logger
from ..language_texts import texts

# Файл для хранения настроек пользователей
USER_SETTINGS_FILE = 'user_settings.json'


def load_user_settings() -> dict:
    """
    Загружает настройки пользователей (например, выбранный язык) из файла.
    Если файла нет или он повреждён, возвращается пустой словарь.
    """
    if os.path.exists(USER_SETTINGS_FILE):
        try:
            with open(USER_SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Не удалось загрузить настройки пользователя: {e}")
    return {}


def save_user_settings(settings: dict) -> None:
    """
    Сохраняет настройки пользователей в файл.
    """
    try:
        with open(USER_SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Не удалось сохранить настройки пользователя: {e}")



def build_menu_keyboard(user_lang: str, user_id: int) -> ReplyKeyboardMarkup:
    # Формируем клавиатуру для администратора
    if is_admin(user_id):
        menu_buttons = [
            [
                KeyboardButton(text=texts[user_lang]['common_search']),
                KeyboardButton(text=texts[user_lang]['search_phone'])
            ],
            [
                KeyboardButton(text=texts[user_lang]['instruction_cmd'])
            ],
            [
                KeyboardButton(text=texts[user_lang]['new_requests']),
                KeyboardButton(text=texts[user_lang]['user_count'])
            ]
        ]
    # Формируем клавиатуру для авторизованного пользователя
    elif is_authorized(user_id):
        menu_buttons = [
            [
                KeyboardButton(text=texts[user_lang]['common_search']),
                KeyboardButton(text=texts[user_lang]['search_phone'])
            ],
            [
                KeyboardButton(text=texts[user_lang]['instruction_cmd'])
            ]
        ]
    else:
        # Для неавторизованных пользователей можно вернуть пустую клавиатуру или произвести иное действие.
        menu_buttons = []

    # Добавляем в конец меню кнопку для смены языка
    menu_buttons.append([
        KeyboardButton(text=texts[user_lang]['change_language'])
    ])

    # Опция resize_keyboard=True позволяет автоматически подгонять размеры кнопок под окно чата.
    return ReplyKeyboardMarkup(menu_buttons, resize_keyboard=True)


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # Обязательно чтобы убрать "часики" в клиенте Telegram

    command = query.data  # Данные, переданные через callback_data

    # Получаем язык пользователя, поставим по умолчанию 'ru'
    lang = context.user_data.get('language', 'ru')
    user_id = query.from_user.id

    # Пример обработки команд:
    if command == 'new_requests' and is_admin(user_id):
        await show_pending_requests(update, context)
    elif command == 'user_count' and is_admin(user_id):
        await show_users_count(update, context)
    elif command == 'common_search':
        context.user_data['search_mode'] = 'general'
        await query.edit_message_text(texts[lang]['general_search_query'])
    elif command == 'search_phone':
        context.user_data['search_mode'] = 'phone'
        await query.edit_message_text(texts[lang]['phone_search_query'])
    elif command == 'instruction_cmd':
        await query.edit_message_text(texts[lang]['instruction_text'])


    elif command == 'change_language':
        # Можно предложить выбор языка
        keyboard = [
            [
                InlineKeyboardButton("Русский", callback_data='ru'),
                InlineKeyboardButton("English", callback_data='en')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(texts[lang]['select_language'], reply_markup=reply_markup)
    else:
        # Если команда не распознана, можно отправить уведомление
        await query.edit_message_text("Команда не распознана.")
