# common_handlers.py
import json
import os

from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, MessageHandler, filters

from .admin_handlers import show_users_count, show_pending_requests, show_pending_requests_as_inline
from ..auth import is_authorized, is_admin
from ..config import logger, ALLOWED_USERS
from ..data import pending_requests, save_allowed_users
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
            ],
            [
                KeyboardButton(text=texts[user_lang].get('db_stats', 'Статистика БД')),
                KeyboardButton(text=texts[user_lang].get('server_stats', 'Характеристики сервера'))
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


# async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     query = update.callback_query
#     await query.answer()  # Обязательно чтобы убрать "часики" в клиенте Telegram
#
#     command = query.data  # Данные, переданные через callback_data
#
#     # Получаем язык пользователя, поставим по умолчанию 'ru'
#     lang = context.user_data.get('language', 'ru')
#     user_id = query.from_user.id
#
#     # Пример обработки команд:
#     if command == 'new_requests' and is_admin(user_id):
#         await show_pending_requests(update, context)
#     elif command == 'user_count' and is_admin(user_id):
#         await show_users_count(update, context)
#     elif command == 'common_search':
#         context.user_data['search_mode'] = 'general'
#         await query.edit_message_text(texts[lang]['general_search_query'])
#     elif command == 'search_phone':
#         context.user_data['search_mode'] = 'phone'
#         await query.edit_message_text(texts[lang]['phone_search_query'])
#     elif command == 'instruction_cmd':
#         await query.edit_message_text(texts[lang]['instruction_text'])
#
#
#     elif command == 'change_language':
#         # Можно предложить выбор языка
#         keyboard = [
#             [
#                 InlineKeyboardButton("Русский", callback_data='ru'),
#                 InlineKeyboardButton("English", callback_data='en')
#             ]
#         ]
#         reply_markup = InlineKeyboardMarkup(keyboard)
#         await query.edit_message_text(texts[lang]['select_language'], reply_markup=reply_markup)
#     else:
#         # Если команда не распознана, можно отправить уведомление
#         await query.edit_message_text("Команда не распознана.")





async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # быстрое «ок»
    command = query.data
    user_id = update.effective_user.id
    lang = context.user_data.get('language', 'en')

    # 1) Главное меню админа
    if command == 'back_to_admin_menu':
        await query.edit_message_text(
            texts[lang]['admin_menu'],
            reply_markup=show_admin_menu(lang)
        )

    # 2) Показать новые заявки
    elif command == 'new_requests' and is_admin(user_id):
        if not pending_requests:
            await query.edit_message_text(texts[lang]['no_requests'])
            return
        kb = [
            [InlineKeyboardButton(str(uid), callback_data=f"view_req:{uid}")]
            for uid in pending_requests
        ]
        kb.append([InlineKeyboardButton("← Назад", callback_data="back_to_admin_menu")])
        await query.edit_message_text(
            texts[lang]['choose_request'],
            reply_markup=InlineKeyboardMarkup(kb)
        )

    # 3) Просмотр одной конкретной заявки
    elif command.startswith("view_req:") and is_admin(user_id):
        _, uid_str = command.split(":", 1)
        applicant_id = int(uid_str)
        kb = [
            [
                InlineKeyboardButton("✅ Одобрить", callback_data=f"approve_req:{applicant_id}"),
                InlineKeyboardButton("❌ Отказать", callback_data=f"deny_req:{applicant_id}")
            ],
            [InlineKeyboardButton("← Назад", callback_data="new_requests")]
        ]
        await query.edit_message_text(
            texts[lang]['request_from'].format(applicant=applicant_id),
            reply_markup=InlineKeyboardMarkup(kb)
        )

    # 4) Одобрение заявки
    elif command.startswith("approve_req:") and is_admin(user_id):
        _, uid_str = command.split(":", 1)
        applicant_id = int(uid_str)
        if applicant_id in pending_requests:
            pending_requests.remove(applicant_id)
            ALLOWED_USERS.add(applicant_id)
            save_allowed_users(ALLOWED_USERS)

            # меняем текст в чате администратора
            await query.edit_message_text(
                texts[lang]['user_authorized'].format(user=applicant_id)
            )
            # уведомляем пользователя
            try:
                await context.bot.send_message(
                    chat_id=applicant_id,
                    text=texts[lang]['your_request_approved']
                )
            except Exception as e:
                logger.error(f"Can't notify user {applicant_id}: {e}")
        else:
            await query.answer(texts[lang]['no_user_found'], show_alert=True)

    # 5) Отказ в заявке
    elif command.startswith("deny_req:") and is_admin(user_id):
        _, uid_str = command.split(":", 1)
        applicant_id = int(uid_str)
        if applicant_id in pending_requests:
            pending_requests.remove(applicant_id)
            await query.edit_message_text(texts[lang]['request_denied'])
            try:
                await context.bot.send_message(
                    chat_id=applicant_id,
                    text=texts[lang]['your_request_denied']
                )
            except:
                pass
        else:
            await query.answer(texts[lang]['no_user_found'], show_alert=True)

    # 6) Остальные ваши команды
    elif command == 'user_count' and is_admin(user_id):
        # ваш existing код ...
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
        keyboard = [
            [
                InlineKeyboardButton("Русский", callback_data='ru'),
                InlineKeyboardButton("English", callback_data='en')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(texts[lang]['select_language'], reply_markup=reply_markup)

    elif command in ('ru', 'en'):
        # Переключаем язык
        context.user_data['language'] = command
        await query.edit_message_text(texts[command]['language_changed'])

    else:
        await query.edit_message_text("Команда не распознана.")


# ловим “Новые заявки” как обычный текст
async def on_new_requests_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = context.user_data.get('language','ru')
    if not is_admin(user_id):
        return await update.message.reply_text(texts[lang]['no_access'])
    # тут вы можете вызвать ваш show_pending_requests,
    # но, скорее всего, вам нужно вручную отрисовать Inline‑кнопки с заявками:
    await show_pending_requests_as_inline(update, context)

# в том же common_handlers.py
def register_common_handlers(app):
    app.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(f"^{texts['ru']['new_requests']}$"),
        on_new_requests_text
    ))


async def show_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = context.user_data.get('language', 'ru')

    # Здесь вы переиспользуете вашу функцию из варианта A:
    kb = build_menu_keyboard(lang, user_id)

    # Если это CallbackQuery – можно ответить так:
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text=texts[lang]['choose_option'],
            reply_markup=kb
        )
    else:
        # Это обычное сообщение
        await update.effective_message.reply_text(
            text=texts[lang]['choose_option'],
            reply_markup=kb
        )