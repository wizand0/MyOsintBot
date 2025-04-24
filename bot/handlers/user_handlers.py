# user_handlers.py

# Обработчик команды /start – вывод меню или запроса выбора языка
import asyncio

from aiomysql import Pool
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from .admin_handlers import show_pending_requests, show_users_count, db_statistics, server_statistics
from .common_handlers import build_menu_keyboard
from ..auth import is_authorized, is_admin
from ..config import logger, USER_STATS
from ..data import pending_requests, save_user_stats
from ..language_texts import texts
from ..search import perform_phone_search, perform_general_search, dbasync_perform_general_search, \
    dbasync_perform_phone_search, sphinx_search_phone
from ..table_utils import send_results_message, save_results_as_html
from ..utils import notify_admin


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


# Основной обработчик текстовых сообщений (для работы с меню)
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    pool: Pool = context.bot_data["db_pool"]

    # Если язык не выбран, просим пользователя выбрать его через /start
    if 'language' not in context.user_data:
        await update.effective_message.reply_text(
            "Пожалуйста, выберите язык, выполнив /start; Please, choose language, press /start")
        return

    # Получаем выбранный язык
    lang = context.user_data['language']
    text = update.effective_message.text.strip().lower()

    # Обработка команд администратора (сравнение можно проводить либо в нижнем регистре, либо добавить отдельные ключи)
    if is_admin(user_id):
        if text == texts[lang].get("new_requests", "новые заявки").lower():
            await show_pending_requests(update, context)
            return

        if text == texts[lang].get("user_count", "количество пользователей").lower():
            await show_users_count(update, context)
            return

        if text == texts[lang].get("db_stats", "статистика БД").lower():
            await db_statistics(update, context)
            return

        if text == texts[lang].get("server_stats", "характеристики сервера").lower():
            await server_statistics(update, context)
            return

    # Проверка авторизации пользователя
    if not is_authorized(user_id):
        await update.effective_message.reply_text(texts[lang]['access_denied'])
        return
    logger.info(text)
    # Обработка команд меню
    if text == texts[lang].get("common_search", "общий поиск").lower():
        context.user_data['search_mode'] = 'general'
        await update.effective_message.reply_text(texts[lang]['general_search_query'])
        return

    if text == texts[lang].get("search_phone", "поиск по номеру телефона").lower():
        context.user_data['search_mode'] = 'phone'
        await update.effective_message.reply_text(texts[lang]['phone_search_query'])
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
        await update.effective_message.reply_text(texts[lang]['select_language'], reply_markup=reply_markup)
        return

    if text == texts[lang].get("instruction_cmd", "инструкция").lower():
        # Здесь можно использовать один из вариантов:
        # Если инструкция хранится в отдельном ключе:
        if is_admin(user_id):
            # отправляем админ‑версию
            await update.effective_message.reply_text(
                texts[lang].get(
                    "admin_instruction_text",
                    "Админ‑инструкция не задана, обратитесь к разработчику"
                )
            )
        else:
            # отправляем обычную инструкцию
            await update.effective_message.reply_text(
                texts[lang].get(
                    "instruction_text",
                    "Инструкция не найдена"
                )
            )
        return

    # Если пользователь уже выбрал режим поиска, обрабатываем его запрос
    if context.user_data.get('search_mode'):
        query_text = update.effective_message.text.strip()

        mode = context.user_data.get('search_mode')

        # Отправляем сообщение-заглушку для отображения прогресса с использованием перевода
        loading_msg = await update.effective_message.reply_text(
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
                # results = await asyncio.to_thread(perform_phone_search, query_text)
                results = await dbasync_perform_phone_search(pool, query_text)
                # results = await sphinx_search_phone(query_text)
                # инкрементим
                user_id = str(update.effective_user.id)
                USER_STATS.setdefault(user_id, {"general": 0, "phone": 0})
                USER_STATS[user_id]["phone"] += 1
                save_user_stats(USER_STATS)

            else:  # mode == 'general'
                # results = await asyncio.to_thread(perform_general_search, query_text)
                results = await dbasync_perform_general_search(pool, query_text)
                user_id = str(update.effective_user.id)
                # инкрементим
                USER_STATS.setdefault(user_id, {"general": 0, "phone": 0})
                USER_STATS[user_id]["general"] += 1
                save_user_stats(USER_STATS)

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
                        await update.effective_message.reply_document(
                            document=file,
                            filename="results.html",
                            caption=texts[lang].get(
                                "long_answer",
                                "Результаты поиска слишком длинные, поэтому отправлены в виде HTML-файла."
                            )
                        )
            else:
                await update.effective_message.reply_text(texts[lang].get("no_results", "Результатов не найдено."))

        except Exception as e:
            logger.exception("Ошибка при выполнении поиска")
            # При ошибке тоже удаляем сообщение-заглушку
            await loading_msg.delete()
            await update.effective_message.reply_text(texts[lang].get("error", "Произошла ошибка при выполнении запроса."))

        # Сбрасываем режим поиска после обработки запроса
        context.user_data.pop('search_mode', None)
    else:
        await update.effective_message.reply_text(
            texts[lang].get("enter_right_command",
                            "Пожалуйста, выберите команду из меню или используйте /start для повторного вызова меню.")
        )