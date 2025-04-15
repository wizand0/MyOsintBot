# Конфигурация
     

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
├── .gitignore
├── Dockerfile
├── README.MD
├── bot/
    ├── __init__.py
    ├── __pycache__/
    ├── _handlers.py
        ├── def load_user_settings
        ├── def save_user_settings
        ├── def build_menu_keyboard
        ├── def send_message
    ├── allowed_users.json
    ├── auth.py
        ├── def is_authorized
        ├── def is_admin
    ├── config.py
    ├── data.py
        ├── def load_allowed_users
        ├── def save_allowed_users
    ├── db.py
        ├── def get_db_connection
    ├── handlers/
        ├── __init__.py
        ├── __pycache__/
        ├── admin_handlers.py
            ├── def send_message
        ├── common_handlers.py
            ├── def load_user_settings
            ├── def save_user_settings
            ├── def build_menu_keyboard
        ├── language_handlers.py
        └── user_handlers.py
    ├── language_texts.py
    ├── main.py
        ├── def main
    ├── search.py
        ├── def perform_general_search
        ├── def perform_phone_search
    ├── table_utils.py
        ├── def save_results_as_html
        ├── def build_ascii_table
        ├── def build_html_table
    └── utils.py
├── docker-compose.yml
├── generate_tree.py
    ├── def get_functions
    ├── def load_ignore_spec
    ├── def print_tree
├── import_all_sql.bat
├── import_all_sql.sh
├── requirements.txt
├── structure.txt

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