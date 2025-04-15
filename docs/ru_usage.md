# Инструкция по использованию

1. Установка и настройка  

   • Установите зависимости с помощью команды:
     
     pip install -r requirements.txt
     

   • Соберите Docker-контейнер:
     
     docker build -t myosintbot .
     

   • Либо запустите через docker-compose:
     
     docker-compose up --build
     
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
