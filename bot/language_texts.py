# language_texts.py

texts = {
    'ru': {
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
    },
    'en': {
        'admin_welcome': "Welcome, administrator!\nChoose an action:",
        'user_welcome': "Welcome!\nChoose an action:",
        'access_denied': "Sorry, you do not have access to this bot.",
        'request_received': "Your access request has been received. Please contact your administrator for access.",
        'select_language': "Please select your language / Пожалуйста, выберите язык:",
        'general_search_query': "Enter the search query:",
        'general_search_cmd': "general search",
        'phone_search_query': "Enter the phone number for search:",
        'phone_search_cmd': "phone search",
        'html_results_caption': "The search results are too long and were sent as an HTML file.",
        'nothing_found': "Nothing was found for your query.",
        'error_search': "An error occurred during the search; please try again later.",
        'common_search': 'Common search',
        'search_phone': 'Search by phone number',
        'instruction_cmd': 'Instruction',
        'instruction_text': "Bot usage instructions:\n"
                            "1. Choose the search mode ('General search' or 'Search by phone number').\n"
                            "2. Enter your search query.\n"
                            "3. The bot will perform the search and return results (for example, 10 records from each table).",
        'new_requests': 'New requests',
        'user_count': 'User count',
        'search_loading': "Searching, please wait...",
        'query_preparing': "Preparing querry...",
        'db_search': "Searching...",
        'processing_results': "Processing results...",
        'search_results_heading': "<b>Search results:</b>",
        'long_answer': "Results are very long, Preparing HTML-file.",
        'no_results': "No results found.",
        'error': "Some error during querry.",
        'private_zone': "You don't have the rights for this command.",
    }
}
