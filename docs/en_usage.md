# User Guide

1. Bot Interaction

   • After starting the bot, begin communicating via Telegram:

     • Use commands to perform searches.

     • Administrators have access to additional commands for managing settings and users.

▎Initial Bot Setup

1. In the project directory, create the file bot/.env:
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