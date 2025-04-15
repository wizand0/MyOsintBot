# Инструкция по использованию

▎Инструкция по использованию

1. Взаимодействие с ботом  

   • После запуска бота, начните общение через Telegram:

     • Используйте команды для выполнения поисков.

     • Администраторы имеют доступ к дополнительным командам для управления настройками и пользователями.

## Первичная настройка бота
1. В каталоге проекта создать файл bot/.env:
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