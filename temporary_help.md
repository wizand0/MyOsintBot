## Not standart container for mariadb
```
# docker exec -it mariadb_server bash # Переход в терминал контейнера
# mariadb -u root -p # Переход в терминал БД

# -------------------------------
# Данный раз не нужен - создан свой контейнер БД на базе стандартного взамен стандартного
# apt update
# apt install software-properties-common -y
# add-apt-repository universe
# apt update
# apt install mysqltuner -y
#---------------------------------

# Запуск mysqltuner для диагностики:
# mysqltuner --version
# mysqltuner --host 127.0.0.1 --port 3306 --user root --pass '!w1JM6bD2If7' --socket /var/run/mysqld/mysqld.sock
# systemctl restart mariadb

```
## stdout/stderr Log container
По‑умолчанию всё, что ваш бот пишет в stdout/stderr, попадает в лог Docker‑контейнера, и вы можете «смотреть» его прямо по SSH.

1. Подключаетесь к серверу по SSH:

   ```
   ssh user@your.server.com
   ```

2. Смотрим список запущенных контейнеров и находим имя (или id) того, в котором крутится бот:

   ```
   docker ps
   ```

3. Выводим логи «на лету», например:

   • Если у вас чистый Docker:
     ```
     docker logs -f --tail 100 <container_name_or_id>
     ```
     — -f (follow) держит соединение открытым и показывает новые строки по мере поступления;  
     — --tail 100 выведет последние 100 строк истории.  

   • Если вы используете docker‑compose:
     ```
     cd /path/to/your/project
     docker‑compose logs -f bot
     ```
     где bot — это имя сервиса в вашем docker‑compose.yml.

4. (Опционально) Если ваш бот логирует не в stdout, а в файл внутри контейнера, можно зайти внутрь и «затащить» этот файл:

   ```
   docker exec -it <container_name> sh
   # или bash, если он есть
   tail -f /path/to/your/bot.log
   ```

После этого вы увидите в реальном времени все сообщения от вашего бота — ошибки, отладочную информацию, любые print или logger.info.