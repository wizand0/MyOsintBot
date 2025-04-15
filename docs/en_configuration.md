Configuration

▎Creating a Container

1. Download and install Docker Desktop for Windows:

   • Visit the official Docker Desktop website (https://www.docker.com/products/docker-desktop) and download the installer for Windows.

   • Install Docker Desktop by following the installer instructions.

2. Launch Docker Desktop and ensure it is running (the Docker icon should appear in the system tray).

---

▎Initial Bot Setup

1. In the project directory, create the .env file.

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

2. Preparing the Project

You should already have the following project structure:
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

Features:

• The .env file contains environment variables (e.g., the Telegram bot token). Make sure your code loads it (for example, using the python-dotenv library).

• The requirements.txt file should include all dependencies required for the bot to function.

---

4. Building the Docker Image

Open a terminal (PowerShell, cmd, Windows Terminal) and navigate to the project directory (MyBot). Then run the build command:
```
docker build -t mybot:latest .
```

Parameters:

• -t mybot:latest — specifies the tag for the created image.

• . — indicates that the Dockerfile is located in the current directory.

---

▎5. Running the Container

▎Option A: If the .env file is already included in the image

Simply run the container using the created image:
```
docker run -d --name mybot_container mybot:latest
```

Parameters:
• -d — runs the container in detached mode.

• --name mybot_container — assigns a name to the container.

▎Option B: If you want to pass environment variables externally (recommended for secrets)

1. Optionally, add a .dockerignore file:  
   If you do not want to include .env in the image, create a .dockerignore file in the root of the project with the following content:
   ```
   bot/.env
   ```

2. Run the container with environment variable injection:

   ```
   docker run -d --name mybot_container --env-file ./bot/.env mybot:latest
   ```

   The --env-file ./bot/.env parameter tells Docker to load environment variables from the specified file when the container starts.

---

▎6. Checking the Container Operation

• View the container logs:

   ```
   docker logs mybot_container
   ```

• If necessary, access the container for debugging:

   ```
   docker exec -it mybot_container /bin/sh
```