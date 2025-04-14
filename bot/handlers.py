# handlers.py
import asyncio
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from .auth import is_authorized, is_admin
from .config import logger, ALLOWED_USERS
from .search import perform_general_search, perform_phone_search
from .table_utils import send_results_message, save_results_as_html
from .data import pending_requests
from .utils import notify_admin  #Уведомление администратора
from .language_texts import texts  # Импортируем словарь с локализацией


# Обработчик для выбора языка через инлайн-кнопки
async def language_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    chosen_lang = query.data  # 'ru' или 'en'
    context.user_data['language'] = chosen_lang

    # После выбора языка можно отправить приветственное сообщение
    user_id = update.effective_user.id
    if is_admin(user_id):
        menu_keyboard = [
            [texts[chosen_lang]['common_search'], texts[chosen_lang]['search_phone']],
            [texts[chosen_lang]['instruction_cmd']],
            [texts[chosen_lang]['new_requests'], texts[chosen_lang]['user_count']]
        ]
    else:
    # Если пользователь авторизован – показываем стандартное меню
        if is_authorized(user_id):
            menu_keyboard = [
                [texts[chosen_lang]['common_search'], texts[chosen_lang]['search_phone']],
                [texts[chosen_lang]['instruction_cmd']]
            ]
        else:
            if user_id not in pending_requests:
                pending_requests.add(user_id)
                await notify_admin(context, user_id)
            await query.edit_message_text(texts[chosen_lang]['request_received'])
            return

    reply_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)
    welcome_text = texts[chosen_lang]['admin_welcome'] if is_admin(user_id) else texts[chosen_lang]['user_welcome']
    # await query.edit_message_text(welcome_text, reply_markup=reply_markup)
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=welcome_text,
        reply_markup=ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )

# Обработчик команды /start – вывод меню или запроса выбора языка
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Если язык ещё не выбран, показываем клавиатуру выбора языка
    if 'language' not in context.user_data:
        keyboard = [
            [InlineKeyboardButton("Русский", callback_data='ru'),
             InlineKeyboardButton("English", callback_data='en')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(texts['ru']['select_language'], reply_markup=reply_markup)
        return

    user_lang = context.user_data['language']
    user_id = update.effective_user.id

    # Если пользователь является администратором, даем полный набор возможностей
    if is_admin(user_id):
        menu_keyboard = [
            [texts[user_lang]['common_search'], texts[user_lang]['search_phone']],
            [texts[user_lang]['instruction_cmd']],
            [texts[user_lang]['new_requests'], texts[user_lang]['user_count']]
        ]
        reply_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            texts[user_lang]['admin_welcome'],
            reply_markup=reply_markup
        )
        return

    # Если пользователь авторизован – показываем стандартное меню
    if is_authorized(user_id):
        menu_keyboard = [
            [texts[user_lang]['common_search'], texts[user_lang]['search_phone']],
            [texts[user_lang]['instruction_cmd']]
        ]
        reply_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            texts[user_lang]['user_welcome'],
            reply_markup=reply_markup
        )
    else:
        # Если пользователь не авторизован, регистрируем заявку
        if user_id not in pending_requests:
            pending_requests.add(user_id)
            await notify_admin(context, user_id)
        await update.message.reply_text(
            texts[user_lang]['request_received']
        )


# Основной обработчик текстовых сообщений (для работы с меню)
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    text = update.message.text.strip().lower()

    # Если язык не выбран, просим пользователя выбрать его через /start
    if 'language' not in context.user_data:
        await update.message.reply_text("Пожалуйста, выберите язык, выполнив /start")
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

    if text == texts[lang].get("instruction_cmd", "инструкция").lower():
        # Здесь можно использовать один из вариантов:
        # Если инструкция хранится в отдельном ключе:
        await update.message.reply_text(texts[lang].get("instruction_text",
            "Инструкция по использованию бота:\n"
            "1. Выберите режим поиска ('Общий поиск' или 'Поиск по номеру телефона').\n"
            "2. Введите поисковый запрос.\n"
            "3. Бот выполнит поиск и вернет результаты (например, 10 записей из каждой таблицы)."))
        return

    # Если пользователь уже выбрал режим поиска, обрабатываем его запрос
    if context.user_data.get('search_mode'):
        query_text = update.message.text.strip()

        mode = context.user_data.get('search_mode')

        # Отправляем сообщение-заглушку для отображения прогресса с использованием перевода
        loading_msg = await update.message.reply_text(texts[lang].get("search_loading", "Идет поиск, пожалуйста, подождите..."))
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
            "Пожалуйста, выберите команду из меню или используйте /start для повторного вызова меню."
        )


async def show_pending_requests(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Если язык не выбран, просим пользователя выбрать его через /start
    if 'language' not in context.user_data:
        await update.message.reply_text("Пожалуйста, выберите язык, выполнив /start")
        return

    # Получаем выбранный язык
    lang = context.user_data['language']
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text(texts[lang].get("private_zone", "У вас нет прав для этой команды."))
        return

    from .data import pending_requests  # импортируем список заявок

    if not pending_requests:
        await update.message.reply_text("Нет новых заявок.")
        return

    # Отправляем администратору список заявок
    requests_list = "\n".join(str(uid) for uid in pending_requests)
    await update.message.reply_text(f"Новые заявки:\n{requests_list}")


# команды авторизации пользователя администратором
async def approve_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Если язык не выбран, просим пользователя выбрать его через /start
    if 'language' not in context.user_data:
        await update.message.reply_text("Пожалуйста, выберите язык, выполнив /start")
        return

    # Получаем выбранный язык
    lang = context.user_data['language']

    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text(texts[lang].get("private_zone", "У вас нет прав для этой команды."))
        return

    # Ожидаем, что администратор передаст id пользователя в виде аргумента команды
    try:
        applicant_id = int(context.args[0])
    except (IndexError, ValueError):
        await update.message.reply_text("Укажите корректный id пользователя. Пример: /approve 123456789")
        return

    if applicant_id in pending_requests:
        pending_requests.remove(applicant_id)
        # Добавляем пользователя в список разрешённых. При желании можно обновить файл или базу данных
        ALLOWED_USERS.add(applicant_id)
        await update.message.reply_text(f"Пользователь {applicant_id} успешно авторизован.")
        # Опционально: уведомляем пользователя об успешной авторизации
        try:
            await context.bot.send_message(chat_id=applicant_id,
                                           text="Ваша заявка одобрена. Теперь вы можете пользоваться ботом.")
        except Exception as e:
            logger.error(f"Ошибка уведомления пользователя: {e}")
    else:
        await update.message.reply_text("Пользователь с таким id не найден в заявках.")


#  обработчик для команды «Количество пользователей»
async def show_users_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Если язык не выбран, просим пользователя выбрать его через /start
    if 'language' not in context.user_data:
        await update.message.reply_text("Пожалуйста, выберите язык, выполнив /start")
        return

    # Получаем выбранный язык
    lang = context.user_data['language']

    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text(texts[lang].get("private_zone", "У вас нет прав для этой команды."))
        return

    count = len(ALLOWED_USERS)
    await update.message.reply_text(f"Количество авторизованных пользователей: {count}")
