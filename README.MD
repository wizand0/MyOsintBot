# MyBot - Телеграм бот для поиска информации в базах данных MySQL (MariaDB)

## Ru, En - Localization

## RU
[Инструкция по использованию - RU](docs/ru_usage.md)<br>
[Запуск и настройка - RU](docs/ru_configuration.md)<br>
[Работа с БД MySQL - RU](docs/ru_db.md)<br>
[Полезное и работа c контейнерами Docker - RU](docs/ru_docker.md)<br>
[Полезные инструменты - RU](docs/ru_helps.md)<br>

## RU
[Instruction - EN](docs/en_usage.md)<br>
[Deploy - EN](docs/en_configuration.md)<br>
[Work with MySQL - EN](docs/en_db.md)<br>
[Helps for Docker - EN](docs/en_docker.md)<br>
[Some instruments - EN](docs/en_helps.md)<br>

▎English

▎Overview

MyBot is a Telegram bot designed for Mysql searching tasks. The bot provides a set of functions for authorized users and administrators to perform various searches and manage user settings. Its modular architecture ensures that functionalities such as authentication, handling different types of queries, and formatting search results are cleanly separated into individual modules. It is deployed via Docker and supports a range of features with an emphasis on usability and scalability.

▎Functionality and Capabilities

1. User and Admin Authentication  

   • The auth.py module contains functions for user authorization:

     • is_authorized: Checks if a user is allowed to access the bot.

     • is_admin: Determines if the current user has administrative privileges.

   • Additionally, allowed_users.json stores the list of permitted users.

2. User Settings and Menu Interaction  

   • Handlers in handlers.py and commonhandlers.py include:

     • load_user_settings and save_user_settings: Manage user-specific settings.

     • build_menu_keyboard: Constructs interactive menu keyboards for users.

   • The bot utilizes language texts provided in language_texts.py to offer localized user interfaces.

3. Search Capabilities  

   • The search.py module offers advanced search functions:

     • perform_general_search: Conducts general data searches.

     • perform_phone_search: Executes searches specifically related to phone numbers.

   • The bot collates search results and offers them in both textual and tabulated formats.

4. Data Presentation  

   • The table_utils.py module provides utilities to convert result data into human-readable formats:

     • build_ascii_table: Generates a text table view.

     • build_html_table and save_results_as_html: Create HTML representations of the data.

   
5. Database Integration  

   • Through db.py, the bot establishes database connections using get_db_connection to store or retrieve data essential for the operations.

6. Modular Handlers for Specific Tasks  

   • The handlers directory includes:

     • admin_handlers.py for management operations.

     • user_handlers.py for general user operations.

     • language_handlers.py for language-specific actions.

   • This structure enables the bot to separate functionality according to user roles and internationalization needs.

7. Utility Functions and Configuration  

   • Utility functions found in utils.py assist in various general tasks.

   • The config.py file holds configuration settings, ensuring the bot can be easily adjusted for different environments.

8. Deployment and Setup  

   • The project is containerized with Dockerfile and uses docker-compose.yml for easy multi-container orchestration.

   • For database setup, scripts like importallsql.sh and importallsql.bat automate the import of necessary SQL files.

9. Project Maintenance and Code Inspection  

   • Tools like generate_tree.py help in visualizing the project structure and extracting function definitions.

   • The project includes a .gitignore ensuring that unnecessary files (log files, caches, etc.) are excluded from version control.

▎Usage Instructions

1. Installation and Setup  

   • Install the required dependencies by running:
     
     pip install -r requirements.txt
     

   • Build the Docker container using:
     
     docker build -t myntbot .
     

   • Alternatively, use docker-compose:
     
     docker-compose up --build
     

   
2. Configuration
• Adjust settings in config.py according to your environment.

   • Update allowed_users.json with the list of authorized Telegram user IDs.

   
3. Running the Bot  

   • The main entry point is in bot/main.py. Ensure you run the script (or the Docker container) in the appropriate context:
     
     python bot/main.py
     

   
4. Interacting with the Bot  

   • Once the bot is running, interact with it on Telegram:

     • Use the provided commands to perform searches.

     • Admins can use additional commands to manage the bot and user settings.

   
5. Extending Functionality  

   • Developers can add new handlers or utilities by following the existing module structure. New functionalities should integrate seamlessly due to the modular design.


▎Обзор

MyBot — это Telegram-бот, предназначенный для задач поиска инфомрации в ваших базх данных MySQL. Бот предоставляет набор функций для авторизованных пользователей и администраторов, позволяющих выполнять различные поисковые операции и управлять настройками пользователей. Его модульная архитектура обеспечивает разделение функционала, такого как аутентификация, обработка запросов и форматирование результатов поиска, что упрощает дальнейшую разработку и поддержание проекта. Развёртывание осуществляется с помощью Docker, а акцент ставится на удобстве использования и масштабируемости.

▎Функциональность и возможности

1. Аутентификация пользователей и администраторов  

   • Модуль auth.py содержит функции для проверки авторизации:

     • is_authorized: проверяет, имеет ли пользователь доступ к боту.

     • is_admin: определяет, обладает ли пользователь административными правами.

   • Файл allowed_users.json хранит список разрешённых пользователей.

2. Настройки пользователей и взаимодействие через меню  

   • Обработчики в handlers.py и commonhandlers.py предоставляют следующие возможности:

     • load_user_settings и save_user_settings: загрузка и сохранение настроек пользователя.

     • build_menu_keyboard: создание интерактивного меню для пользователей.

   • Для локализации интерфейса бот использует тексты, определённые в language_texts.py.

3. Поисковые возможности  

   • Модуль search.py предлагает расширенные функции поиска:

     • perform_general_search: выполнение общего поиска данных.

     • perform_phone_search: осуществление поиска по телефонным номерам.

   • Бот собирает результаты поиска и отображает их в текстовом и табличном формате.

4. Представление данных
• Модуль table_utils.py включает утилиты для преобразования результатов в удобный для чтения формат:

     • build_ascii_table: создание таблицы в текстовом виде.

     • build_html_table и save_results_as_html: генерация HTML-таблиц для представления данных.

5. Интеграция с базой данных  

   • Модуль db.py отвечает за установление подключения к базе данных с помощью функции get_db_connection, позволяющей хранить и извлекать данные, необходимые для работы.

6. Модульные обработчики для различных задач  

   • В папке handlers расположены:

     • admin_handlers.py — обработчики для административных функций.

     • user_handlers.py — обработчики для обычных пользователей.

     • language_handlers.py — обработчики, отвечающие за изменения языка интерфейса.

   • Такая структура позволяет разделить функционал в зависимости от ролей пользователей и требований к интернационализации.

7. Утилиты и настройки  

   • Файл utils.py содержит вспомогательные функции, применяемые во многих частях проекта.

   • Конфигурация проекта находится в config.py, что упрощает настройку бота под различные окружения.

8. Разворачивание и настройка проекта  

   • Проект контейнеризирован с помощью Dockerfile и использует docker-compose.yml для оркестрации сервисов.

   • Скрипты importallsql.sh и importallsql.bat автоматизируют импорт необходимых SQL-скриптов для базы данных.

9. Поддержка и инспекция кода  

   • Скрипт generate_tree.py помогает визуализировать структуру проекта и извлекает список функций для анализа.

   • Файл .gitignore гарантирует, что временные файлы, кэш и прочие ненужные артефакты не будут попадать под контроль версий.



   
5. Расширение функционала  

   • Разработчики могут добавлять новые обработчики и функции, следуя структуре проекта. Благодаря модульной архитектуре, новые возможности легко интегрируются в существующую систему.



## TODO:
- ~~Мультимпорт с кириллице;~~ - Замена PowerShell на cmd
- ~~Закончить рефакторинг кода;~~
- ~~Добавить авторизацию;~~
- ~~Добавить администратора и возможность администратору добавлять пользователей;~~
- Отправка уведомлений админу в случае перезапуска сервера;
- ~~Возможность админу следить за состоянием сервера (нагрузка, температура и т.д.)~~
- ~~Сделать файл results.html временным и сразу после отправки удалять~~