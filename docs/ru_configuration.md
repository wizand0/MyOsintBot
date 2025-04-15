# Конфигурация
     

## Создание контейнера
1. Скачать и установить Docker Desktop для Windows:

   • Перейдите на официальный сайт Docker Desktop (https://www.docker.com/products/docker-desktop) и скачайте установщик для Windows.

   • Установите Docker Desktop, следуя инструкциям установщика.

2. Запустить Docker Desktop и убедитесь, что он работает (значок Docker должен быть в системном трее).

---

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

4. Сборка и запуск контейнеров

Откройте терминал (например, PowerShell, терминал в VS Code или любой другой) и перейдите в корневую папку проекта (ту, где находятся файл docker-compose.yml и Dockerfile).

Запустите следующую команду для сборки и запуска контейнеров:
```
docker-compose up --build
```

Эта команда выполняет следующие действия:

• --build — пересобирает образы с нуля, используя инструкции из Dockerfile.

• up — поднимает сервисы, указанные в docker-compose.yml (в вашем случае это bot и db).

Если вы хотите запустить контейнеры в фоновом режиме (detached mode), добавьте флаг -d:
```
docker-compose up --build -d
```


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

▎6. Проверка работы контейнеров

• Логи контейнеров:  
  Чтобы посмотреть, как работает ваш бот или база данных, можно просмотреть логи:

  ```
  docker-compose logs -f bot
  docker-compose logs -f db
  ```

• Статус контейнеров:  
  Узнать состояние контейнеров можно с помощью команды:

  ```
  docker-compose ps
  ```

• Подключение к контейнеру:  
  Если необходимо войти в работающий контейнер (например, для диагностики), можно использовать команду:

  ```
  docker exec -it myosint_bot /bin/bash
  ```

  Здесь myosint_bot — это имя контейнера, указанное в docker-compose.yml.
  
Остановка контейнеров

Для остановки и удаления контейнеров (с сохранением данных в томах) выполните:
```
docker-compose down
```

Если нужно также удалить тома (например, для полного сброса данных базы), добавьте флаг -v:
```
docker-compose down -v
```

---

▎Заключение

Таким образом, чтобы собрать и запустить контейнеры, достаточно открыть терминал в папке проекта и выполнить команду:
```
docker-compose up --build
```

Это запустит оба сервиса — бота и базу данных MariaDB, используя настройки из docker-compose.yml и переменные из файла .env.
