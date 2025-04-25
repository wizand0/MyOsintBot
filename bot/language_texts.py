# language_texts.py

texts = {
    'ru': {
        'main': "Главная",
        'choose_language_start': "Пожалуйста, выберите язык, выполнив /start",
        'admin_welcome': "Добро пожаловать, администратор!\nВыберите действие:",
        'user_welcome': "Добро пожаловать!\nВыберите действие:",
        'access_denied': "Извините, у вас нет доступа к боту.",
        'request_received': "Ваша заявка на доступ получена. Пожалуйста, обратитесь к администратору для авторизации.",
        'select_language': "Пожалуйста, выберите язык / Please select your language:",
        'general_search_query': "Введите поисковый запрос для общего поиска:",
        'general_search_cmd': "общий поиск",
        'phone_search_query': "Введите номер телефона для поиска:",
        'phone_search_cmd': "поиск по номеру телефона",
        'html_results_caption': "Результаты поиска слишком длинные, поэтому отправлены в виде HTML-файла.",
        'nothing_found': "Ничего не найдено по вашему запросу.",
        'error_search': "Произошла ошибка при выполнении поиска, повторите попытку позже.",
        'common_search': 'Общий поиск',
        'search_phone': 'Поиск по номеру телефона',
        'instruction_cmd': 'Инструкция',
        'instruction_text': "Инструкция по использованию бота:\n"
            "1. Выберите режим поиска ('Общий поиск' или 'Поиск по номеру телефона').\n"
            "2. Введите поисковый запрос.\n"
            "3. Бот выполнит поиск и вернет результаты (например, 10 записей из каждой таблицы).",
        'new_requests': 'Новые заявки',
        'user_count': 'Количество пользователей',
        'search_loading': "Идет поиск, пожалуйста, подождите...",
        'query_preparing': "Подготовка запроса...",
        'db_search': "Выполняется поиск в базе данных...",
        'processing_results': "Обработка результатов...",
        'search_results_heading': "<b>Результаты поиска:</b>",
        'long_answer': "Результаты поиска слишком длинные, поэтому отправлены в виде HTML-файла.",
        'no_results': "Результатов не найдено.",
        'error': "Произошла ошибка при выполнении запроса.",
        'private_zone': "У вас нет прав для этой команды.",
        'enter_right_command': "Пожалуйста, выберите команду из меню или используйте /start для повторного вызова меню.",
        'approve_user': "Новая заявка на доступ(для доступа укажите: /approve",
        'no_user_found': "Пользователь с таким id не найден в заявках.",
        'user': "Пользователь",
        'is_authorizied': "успешно авторизован",
        'your_request_approved': "Ваша заявка одобрена. Теперь вы можете пользоваться ботом.",
        'user_amount': "Количество авторизованных пользователей",
        'no_new_application': "Нет новых заявок",
        'new_applications': "Новые заявки",
        'change_language': 'Сменить язык',
        'choose_language': 'Выберите язык:',
        'db_stats': 'Статистика БД',
        'server_stats': 'Характеристики сервера',
        'user_requests': 'Запросы пользователей',
        "admin_instruction_text": (
        "— /approve 123456789 – добавить пользователя\n"
        "— /delete 123456789 – удалить пользователя\n"
        "— /stats – счетчики поисков (общий и по телефону)\n"
        "По пользователям и запросам – подробности в админ‑панели."
        ),
    },
    'en': {
        'main': "Main",
        'choose_language_start': "Please choose a language by executing /start",
        'admin_welcome': "Welcome, Administrator!\nSelect an action:",
        'user_welcome': "Welcome!\nSelect an action:",
        'access_denied': "Sorry, you do not have access to the bot.",
        'request_received': "Your access request has been received. Please contact the administrator for authorization.",
        'select_language': "Please select your language:",
        'general_search_query': "Enter the search query for a general search:",
        'general_search_cmd': "general search",
        'phone_search_query': "Enter the phone number to search:",
        'phone_search_cmd': "search by phone number",
        'html_results_caption': "The search results are too long and have been sent as an HTML file.",
        'nothing_found': "Nothing was found for your query.",
        'error_search': "An error occurred during the search. Please try again later.",
        'common_search': "General Search",
        'search_phone': "Search by Phone Number",
        'instruction_cmd': "Instruction",
        'instruction_text': (
            "Bot usage instructions:\n"
            "1. Choose the search mode ('General Search' or 'Search by Phone Number').\n"
            "2. Enter the search query.\n"
            "3. The bot will perform a search and return the results (for example, 10 records from each table)."
        ),
        'new_requests': "New Requests",
        'user_count': "Number of Users",
        'search_loading': "Searching, please wait...",
        'query_preparing': "Preparing query...",
        'db_search': "Searching in the database...",
        'processing_results': "Processing results...",
        'search_results_heading': "<b>Search Results:</b>",
        'long_answer': "The search results are too long and have been sent as an HTML file.",
        'no_results': "No results found.",
        'error': "An error occurred while processing the request.",
        'private_zone': "You do not have permission to use this command.",
        'enter_right_command': "Please select a command from the menu or use /start to re-display the menu.",
        'approve_user': "New Request(approve by command: /approve",
        'no_user_found': "No user with this ID was found in the requests.",
        'user': "User",
        'is_authorizied': "has been successfully authorized",
        'your_request_approved': "Your request has been approved. You can now use the bot.",
        'user_amount': "Number of authorized users",
        'no_new_application': "No new applications",
        'new_applications': "New applications",
        'change_language': 'Change language',
        'choose_language': 'Choose language:',
        'db_stats': 'DB Statistics',
        'server_stats': 'Server Statistics',
        'user_requests': 'User Requests',
        "admin_instruction_text": (
        "👮‍♂️ Админ‑инструкция:\n"
        "— /approve 123456789 – approve user\n"
        "— /delete 123456789 – delete user\n"
        "— /stats – search stats\n"
        ),
    }
}
