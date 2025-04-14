# handlers.py
import asyncio
import json
import os

import logging
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton

from .auth import is_authorized, is_admin
from .config import logger, ALLOWED_USERS, TOKEN
from .search import perform_general_search, perform_phone_search
from .table_utils import send_results_message, save_results_as_html
from .data import pending_requests
from .utils import notify_admin  # Уведомление администратора
from .language_texts import texts  # Импортируем словарь с локализацией

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


# Обработчик команды /start – вывод меню или запроса выбора языка
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
        await update.message.reply_text(texts['ru']['select_language'], reply_markup=reply_markup)
        return

    user_lang = context.user_data['language']
    user_id = update.effective_user.id

    # Если пользователь не авторизован, обрабатываем заявку
    if not (is_admin(user_id) or is_authorized(user_id)):
        if user_id not in pending_requests:
            pending_requests.add(user_id)
            await notify_admin(context, user_id)
        await update.message.reply_text(texts[user_lang]['request_received'])
        return

    # Получаем клавиатуру для выбранного языка и типа пользователя
    reply_markup = build_menu_keyboard(user_lang, user_id)
    # Определяем приветственное сообщение
    if is_admin(user_id):
        welcome_text = texts[user_lang]['admin_welcome']
    else:
        welcome_text = texts[user_lang]['user_welcome']

    await update.message.reply_text(welcome_text, reply_markup=reply_markup)


# Основной обработчик текстовых сообщений (для работы с меню)
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    # Если язык не выбран, просим пользователя выбрать его через /start
    if 'language' not in context.user_data:
        await update.message.reply_text(
            "Пожалуйста, выберите язык, выполнив /start; Please, choose language, press /start")
        return

    # Получаем выбранный язык
    lang = context.user_data['language']
    text = update.message.text.strip().lower()

    # Обработка команд администратора (сравнение можно проводить либо в нижнем регистре, либо добавить отдельные ключи)
    if is_admin(user_id):
        if text == texts[lang].get("new_requests", "новые заявки").lower():
            await show_pending_requests(update, context)
            return

        if text == texts[lang].get("user_count", "количество пользователей").lower():
            await show_users_count(update, context)
            return

    # Проверка авторизации пользователя
    if not is_authorized(user_id):
        await update.message.reply_text(texts[lang]['access_denied'])
        return
    logger.info(text)
    # Обработка команд меню
    if text == texts[lang].get("common_search", "общий поиск").lower():
        context.user_data['search_mode'] = 'general'
        await update.message.reply_text(texts[lang]['general_search_query'])
        return

    if text == texts[lang].get("search_phone", "поиск по номеру телефона").lower():
        context.user_data['search_mode'] = 'phone'
        await update.message.reply_text(texts[lang]['phone_search_query'])
        return

    if text == texts[lang].get("change_language", "Сменить язык").lower():
        # Можно предложить выбор языка
        keyboard = [
            [
                InlineKeyboardButton("Русский", callback_data='ru'),
                InlineKeyboardButton("English", callback_data='en')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(texts[lang]['select_language'], reply_markup=reply_markup)
        return

    if text == texts[lang].get("instruction_cmd", "инструкция").lower():
        # Здесь можно использовать один из вариантов:
        # Если инструкция хранится в отдельном ключе:
        await update.message.reply_text(
            texts[lang].get(
                "instruction_text",
                "Инструкция по использованию бота:\n"
                "1. Выберите режим поиска ('Общий поиск' или 'Поиск по номеру телефона').\n"
                "2. Введите поисковый запрос.\n"
                "3. Бот выполнит поиск и вернет результаты (например, 10 записей из каждой таблицы).")
        )
        return

    # Если пользователь уже выбрал режим поиска, обрабатываем его запрос
    if context.user_data.get('search_mode'):
        query_text = update.message.text.strip()

        mode = context.user_data.get('search_mode')

        # Отправляем сообщение-заглушку для отображения прогресса с использованием перевода
        loading_msg = await update.message.reply_text(
            texts[lang].get("search_loading", "Идет поиск, пожалуйста, подождите..."))
        try:
            # Обновление статуса – подготовка запроса
            progress_msg = texts[lang].get("query_preparing", "Подготовка запроса...")
            await loading_msg.edit_text(progress_msg)
            await asyncio.sleep(0.5)

            # Обновление статуса – выполнение запроса в базе данных
            progress_msg = texts[lang].get("db_search", "Выполняется поиск в базе данных...")
            await loading_msg.edit_text(progress_msg)
            await asyncio.sleep(0.5)

            # Выполнение поиска в отдельном потоке
            if mode == 'phone':
                results = await asyncio.to_thread(perform_phone_search, query_text)
            else:  # mode == 'general'
                results = await asyncio.to_thread(perform_general_search, query_text)

            # Обновление статуса – обработка результатов
            progress_msg = texts[lang].get("processing_results", "Обработка результатов...")
            logger.info(progress_msg)
            await loading_msg.edit_text(progress_msg)
            await asyncio.sleep(0.5)

            # По завершении поиска удаляем сообщение с индикатором загрузки
            await loading_msg.delete()

            if results:
                # Формирование текстового ответа
                response = texts[lang].get("search_results_heading", "<b>Результаты поиска:</b>") + "\n"
                for row in results:
                    table_name = row.get('table_name', 'unknown')
                    row_data = " | ".join(f"{key}: {value}" for key, value in row.items() if key != 'table_name')
                    response += f"<i>[{table_name}]</i> {row_data}\n"

                # Если текст достаточно компактный – отправляем обычным сообщением
                if len(response) < 3500:
                    await send_results_message(update, response)
                else:
                    # Если результат слишком длинный, сохраняем его как HTML и отправляем файл
                    file_path = await asyncio.to_thread(save_results_as_html, results)
                    with open(file_path, "rb") as file:
                        await update.message.reply_document(
                            document=file,
                            filename="results.html",
                            caption=texts[lang].get(
                                "long_answer",
                                "Результаты поиска слишком длинные, поэтому отправлены в виде HTML-файла."
                            )
                        )
            else:
                await update.message.reply_text(texts[lang].get("no_results", "Результатов не найдено."))

        except Exception as e:
            logger.exception("Ошибка при выполнении поиска")
            # При ошибке тоже удаляем сообщение-заглушку
            await loading_msg.delete()
            await update.message.reply_text(texts[lang].get("error", "Произошла ошибка при выполнении запроса."))

        # Сбрасываем режим поиска после обработки запроса
        context.user_data.pop('search_mode', None)
    else:
        await update.message.reply_text(
            texts[lang].get("enter_right_command",
                            "Пожалуйста, выберите команду из меню или используйте /start для повторного вызова меню.")
        )


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

    from .data import pending_requests  # импортируем список заявок

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


# def build_menu_keyboard(user_lang: str, user_id: int) -> InlineKeyboardMarkup:
#     # Формируем клавиатуру для администратора
#     if is_admin(user_id):
#         menu_buttons = [
#             [
#                 InlineKeyboardButton(
#                     text=texts[user_lang]['common_search'], callback_data="common_search"
#                 ),
#                 InlineKeyboardButton(
#                     text=texts[user_lang]['search_phone'], callback_data="search_phone"
#                 )
#             ],
#             [
#                 InlineKeyboardButton(
#                     text=texts[user_lang]['instruction_cmd'], callback_data="instruction_cmd"
#                 )
#             ],
#             [
#                 InlineKeyboardButton(
#                     text=texts[user_lang]['new_requests'], callback_data="new_requests"
#                 ),
#                 InlineKeyboardButton(
#                     text=texts[user_lang]['user_count'], callback_data="user_count"
#                 )
#             ]
#         ]
#     # Формируем клавиатуру для авторизованного пользователя
#     elif is_authorized(user_id):
#         menu_buttons = [
#             [
#                 InlineKeyboardButton(
#                     text=texts[user_lang]['common_search'], callback_data="common_search"
#                 ),
#                 InlineKeyboardButton(
#                     text=texts[user_lang]['search_phone'], callback_data="search_phone"
#                 )
#             ],
#             [
#                 InlineKeyboardButton(
#                     text=texts[user_lang]['instruction_cmd'], callback_data="instruction_cmd"
#                 )
#             ]
#         ]
#     else:
#         # Для неавторизованных пользователей можно вернуть пустую клавиатуру или произвести иное действие.
#         menu_buttons = []
#
#     # Добавляем в конец меню кнопку для смены языка
#     menu_buttons.append([
#         InlineKeyboardButton(
#             text=texts[user_lang]['change_language'], callback_data="change_language"
#         )
#     ])
#
#     return InlineKeyboardMarkup(menu_buttons)

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
