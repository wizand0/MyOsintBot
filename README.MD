# MyBot - Телеграм бот для поиска информации в базах данных MySQL (MariaDB)

## Ru, En - Localization

[Инструкция по использованию](usage.md)

▎English

▎Overview

MyOsintBot is a Telegram bot designed for OSINT (Open Source Intelligence) tasks. The bot provides a set of functions for authorized users and administrators to perform various searches and manage user settings. Its modular architecture ensures that functionalities such as authentication, handling different types of queries, and formatting search results are cleanly separated into individual modules. It is deployed via Docker and supports a range of OSINT features with an emphasis on usability and scalability.

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

     • perform_general_search: Conducts general OSINT data searches.

     • perform_phone_search: Executes searches specifically related to phone numbers.

   • The bot collates search results and offers them in both textual and tabulated formats.

4. Data Presentation  

   • The table_utils.py module provides utilities to convert result data into human-readable formats:

     • build_ascii_table: Generates a text table view.

     • build_html_table and save_results_as_html: Create HTML representations of the data.

   
5. Database Integration  

   • Through db.py, the bot establishes database connections using get_db_connection to store or retrieve data essential for the OSINT operations.

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
     
     docker build -t myosintbot .
     

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

     • Use the provided commands to perform OSINT searches.

     • Admins can use additional commands to manage the bot and user settings.

   
5. Extending Functionality  

   • Developers can add new handlers or utilities by following the existing module structure. New functionalities should integrate seamlessly due to the modular design.


▎Обзор

MyOsintBot — это Telegram-бот, предназначенный для задач OSINT (разведка с использованием открытых источников). Бот предоставляет набор функций для авторизованных пользователей и администраторов, позволяющих выполнять различные поисковые операции и управлять настройками пользователей. Его модульная архитектура обеспечивает разделение функционала, такого как аутентификация, обработка запросов и форматирование результатов поиска, что упрощает дальнейшую разработку и поддержание проекта. Развёртывание осуществляется с помощью Docker, а акцент ставится на удобстве использования и масштабируемости.

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

     • perform_general_search: выполнение общего поиска OSINT-данных.

     • perform_phone_search: осуществление поиска по телефонным номерам.

   • Бот собирает результаты поиска и отображает их в текстовом и табличном формате.

4. Представление данных
• Модуль table_utils.py включает утилиты для преобразования результатов в удобный для чтения формат:

     • build_ascii_table: создание таблицы в текстовом виде.

     • build_html_table и save_results_as_html: генерация HTML-таблиц для представления данных.

5. Интеграция с базой данных  

   • Модуль db.py отвечает за установление подключения к базе данных с помощью функции get_db_connection, позволяющей хранить и извлекать данные, необходимые для работы OSINT.

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

▎Инструкция по использованию

1. Установка и настройка  

   • Установите зависимости с помощью команды:
     
     pip install -r requirements.txt
     

   • Соберите Docker-контейнер:
     
     docker build -t myosintbot .
     

   • Либо запустите через docker-compose:
     
     docker-compose up --build
     

   
2. Конфигурация  

   • Настройте параметры в файле config.py под ваше окружение.

   • Добавьте разрешённые Telegram ID в файл allowed_users.json.

   
3. Запуск бота  

   • Основной входной файл находится в bot/main.py. Запустите его:
     
     python bot/main.py
     

   
4. Взаимодействие с ботом  

   • После запуска бота, начните общение через Telegram:

     • Используйте команды для выполнения OSINT-поисков.

     • Администраторы имеют доступ к дополнительным командам для управления настройками и пользователями.

   
5. Расширение функционала  

   • Разработчики могут добавлять новые обработчики и функции, следуя структуре проекта. Благодаря модульной архитектуре, новые возможности легко интегрируются в существующую систему.


## Первичная настройка бота
1. В каталоге проекта создать файл .env:
```
# .env
# Для бота
TOKEN=YOUR_TOKEN
DB_HOST=mariadb_server
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=bd_name
DB_PORT=3306
ALLOWED_USERS=123456789, 987654321

# Для MariaDB
MYSQL_ROOT_PASSWORD=root_password
MYSQL_DATABASE=SAME_AS_DB_HOST
MYSQL_USER=your_username_same_as_DB_USER
MYSQL_PASSWORD=your_password_same_as_DB_PASSWORD
```

## Создание контейнера
1. Скачать и установить Docker Desktop для Windows:

   • Перейдите на официальный сайт Docker Desktop (https://www.docker.com/products/docker-desktop) и скачайте установщик для Windows.

   • Установите Docker Desktop, следуя инструкциям установщика.

2. Запустить Docker Desktop и убедитесь, что он работает (значок Docker должен быть в системном трее).

---

3. Подготовка проекта

У вас уже есть следующая структура проекта:
```
MyBot/
├── Dockerfile
├── README.MD
├── README1.md
├── bot
│   ├── __init__.py
│   ├── _handlers.py
│   ├── auth.py
│   ├── config.py # - Настройки
│   ├── data.py
│   ├── db.py # - Работа с БД
│   ├── handlers
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   ├── admin_handlers.py
│   │   ├── common_handlers.py
│   │   ├── language_handlers.py
│   │   └── user_handlers.py
│   ├── language_texts.py
│   ├── main.py
│   ├── search.py # - Логика поиска (todo)
│   ├── table_utils.py # - Формат исходящих данных
│   └── utils.py
├── docker-compose.yml
├── import_all_sql.bat # - Импорт всех дампов в текущем каталоге (windows)
├── import_all_sql.sh # - Импорт всех дампов в текущем каталоге (linux)
├── requirements.txt
└── user_settings.json
```

Особенности:

• Файл .env содержит переменные окружения (например, токен Telegram-бота). Убедитесь, что ваш код загружает его (например, с помощью библиотеки python-dotenv).

• Файл requirements.txt должен содержать все зависимости, необходимые для работы бота.

---

4. Сборка Docker-образа

Откройте терминал (PowerShell, cmd, Windows Terminal) и перейдите в каталог с проектом (MyBot). Затем выполните команду сборки:
```
docker build -t mybot:latest .
```

Параметры:

• -t mybot:latest — задаёт тег для создаваемого образа.

• . — указывает, что Dockerfile находится в текущем каталоге.

---

▎5. Запуск контейнера

▎Вариант A: Если файл .env уже включён в образ

Просто запустите контейнер, используя созданный образ:
```
docker run -d --name mybot_container mybot:latest
```

Параметры:
```
• -d — запускает контейнер в фоновом режиме.

• --name mybot_container — задаёт имя контейнера.
```
▎Вариант B: Если вы хотите передать переменные окружения извне (рекомендуется для секретов)

1. Добавьте файл .dockerignore (опционально):  
   Если вы не хотите включать .env в образ, создайте файл .dockerignore в корне проекта со следующим содержимым:
```
   bot/.env
```
2. Запустите контейнер с передачей переменных:

   ```
   docker run -d --name mybot_container --env-file ./bot/.env mybot:latest
   ```

   Параметр --env-file ./bot/.env указывает Docker загрузить переменные окружения из указанного файла при старте контейнера.

---

▎6. Проверка работы контейнера

• Просмотреть логи контейнера:

  ```
  docker logs mybot_container
  ```

• При необходимости зайти внутрь контейнера для отладки:

  ```
  docker exec -it mybot_container /bin/sh
  ```


## Импорт базы данных
1. Проверка есть ли таблицы в БД:
2. Откройте PowerShell или другую консоль на Windows.
3. Подключитесь к контейнеру, запустив интерактивный терминал:  
```
docker exec -it mariadb_server bash
```
3a. Установите клиент MariaDB
```
apt-get update && apt-get install mariadb-client
```
4.  Запустите клиент MariaDB:  
   Внутри контейнера выполните:
   ```
   mariadb -u root -p
   ```
   При появлении запроса введите пароль:  
   ```
   [Root Password]
   ```
   После успешного ввода вы попадёте в интерактивную консоль MariaDB (приглашение будет примерно таково: 
   ```
MariaDB [(none)]>).
```
5. Подключитесь к нужной базе данных и посмотрите таблицы:  
   Выполните:
   ```
   USE [Your_DB];
   SHOW TABLES;
   ```
   После команды SHOW TABLES; отобразится список таблиц в базе данных [Your_DB].

6.  Убедитесь, что файл дампа расположен в текущей директории или укажите полный путь к файлу.
7. Выполните команду для импорта дампа непосредственно из Windows (cmd):
   ```
   docker exec -i mariadb_server mysql -u root -p!w1JM6bD2If7 osint_bd < dump.sql
   ```
   Обратите внимание, что здесь пароль указан сразу после -p без пробела. Если по соображениям безопасности вы не хотите его указывать в команде, можно оставить -p без пароля, тогда после запуска команды вам будет предложено ввести пароль:
   ```
   docker exec -i mariadb_server mysql -u root -p osint_bd < dump.sql
   ```
8. После выполнения команды дамп будет импортирован в базу данных [Your_DB].  
   При этом новые таблицы, которых не было, будут созданы, если они описаны в дампе.


## Если где-то ошиблись при разработке, то в каталоге проекта:
### 1. Сбросить контейнеры:
```
docker-compose down -v
```
### 2. Запустить их заново:
```
docker-compose up -d
```

p.s. Если у вас есть несколько дампов БД в формате *.sql определенном каталоге, скопируйте в этот каталог файл из проекта 
 <br>**для windows:**<br>
```
import_all_sql.bat
```
В каталоге с дампами БД запустить файл через **cmd** (не в PowerShell)
```
import_all_sql.bat
```
**для linux:**
```
import_all_sql.sh
```
```
chmod +x import_all_sql.sh
```
```
.\import_all_sql.sh
```


### p.p.s.
### Вариант 1. Использование команды `tree` в терминале (Linux / macOS / WSL)
1. **Установка утилиты `tree`:**
   - **Ubuntu/Debian:**  
     ```bash
     sudo apt update && sudo apt install tree
     ```
2. **Генерация дерева проекта:**
   Перейдите в корневую папку вашего проекта и выполните команду:
   ```bash
   tree -L 2 > README.md
   ```
   Здесь:
   - `-L 2` ограничивает глубину отображения до 2 уровней (при необходимости замените число на другое значение);
   - `> README.md` сохраняет вывод в файл `README.md`. Если README.md уже существует, команда перезапишет его содержимое.


### p.p.p.s.
▎1. Если изменились настройки в исходном коде или Dockerfile (билд-часть)

Перестройте образы и заново запустите контейнеры:
```
docker-compose up -d --build
```

Эта команда:

• Перестроит образы для контейнеров, для которых есть изменения в Dockerfile или в контексте сборки.

• Остановит старые контейнеры и запустит новые в фоновом режиме.

---

▎2. Если доступны обновлённые образы из Docker Hub или другого реестра

Чтобы скачать обновлённые версии образов, выполните:
```
docker-compose pull
```

А затем запустите контейнеры (это можно совместить с пересборкой, если необходимо):
```
docker-compose up -d
```

---

▎3. Если нужно перезапустить контейнеры (без пересборки образов)

Можно просто выполнить перезапуск сервисов:
```
docker-compose restart
```

Эта команда остановит и заново запустит контейнеры, не затрагивая образы, что удобно, если изменения касаются, например, переменных окружения (если они были переданы через env_file или переменные в Docker Compose).

---

▎4. Полная перезагрузка (при необходимости удалить старые контейнеры)

Если требуется удалить старые контейнеры, выполнить некоторые операции «с нуля», можно:

1. Остановить и удалить контейнеры:

   ```
   docker-compose down
   ```

2. (Опционально) Удалить неиспользуемые образы и контейнеры:

   ```
   docker system prune -f
   ```

3. Запустить контейнеры заново:

   ```
   docker-compose up -d --build
   ```



## TODO:
- ~~Мультимпорт с кириллице;~~ - Замена PowerShell на cmd
- ~~Закончить рефакторинг кода;~~
- ~~Добавить авторизацию;~~
- ~~Добавить администратора и возможность администратору добавлять пользователей;~~
- Отправка уведомлений админу в случае перезапуска сервера;
- Возможность админу следить за состоянием сервера (нагрузка, температура и т.д.)
- Сделать файл results.html временным и сразу после отправки удалять