from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes

from bot.auth import is_admin, is_authorized
from bot.data import pending_requests
from bot.language_texts import texts
from bot.utils import notify_admin


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Если язык ещё не выбран, показываем клавиатуру для выбора языка.
    if 'language' not in context.user_data:
        keyboard = [
            [
                InlineKeyboardButton("Русский", callback_data='ru'),
                InlineKeyboardButton("English", callback_data='en')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.effective_message.reply_text(texts['ru']['select_language'], reply_markup=reply_markup)
        return

    user_lang = context.user_data['language']
    user_id = update.effective_user.id

    # Если пользователь не авторизован, обрабатываем заявку
    if not (is_admin(user_id) or is_authorized(user_id)):
        if user_id not in pending_requests:
            pending_requests.add(user_id)
            await notify_admin(context, user_id)
        await update.effective_message.reply_text(texts[user_lang]['request_received'])
        return

    # Получаем клавиатуру для выбранного языка и типа пользователя
    reply_markup = build_menu_keyboard(user_lang, user_id)
    # Определяем приветственное сообщение
    if is_admin(user_id):
        welcome_text = texts[user_lang]['admin_welcome']
    else:
        welcome_text = texts[user_lang]['user_welcome']

    await update.effective_message.reply_text(welcome_text, reply_markup=reply_markup)


def build_menu_keyboard(user_lang: str, user_id: int) -> ReplyKeyboardMarkup:
    # Формируем клавиатуру для администратора
    if is_admin(user_id):
        menu_buttons = [
            [
                KeyboardButton(text=texts[user_lang]['main']),
                KeyboardButton(text=texts[user_lang]['instruction_cmd'])
            ],
            [
                KeyboardButton(text=texts[user_lang]['common_search']),
                KeyboardButton(text=texts[user_lang]['search_phone'])
            ],
            [
                KeyboardButton(text=texts[user_lang]['new_requests']),
                KeyboardButton(text=texts[user_lang]['user_count'])
            ],
            [
                KeyboardButton(text=texts[user_lang].get('db_stats', 'Статистика БД')),
                KeyboardButton(text=texts[user_lang].get('server_stats', 'Характеристики сервера'))
            ],
            [
                KeyboardButton(text="Motion ON"),
                KeyboardButton(text="Motion OFF")
            ],
            [
                KeyboardButton(text="📊 Motion Status"),
                KeyboardButton(text="📋 Container Logs")
            ]
        ]
    # Формируем клавиатуру для авторизованного пользователя
    elif is_authorized(user_id):
        menu_buttons = [
            [
                KeyboardButton(text=texts[user_lang]['instruction_cmd']),
                KeyboardButton(text=texts[user_lang]['main'])
            ],
            [
                KeyboardButton(text=texts[user_lang]['common_search']),
                KeyboardButton(text=texts[user_lang]['search_phone'])
            ],
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



