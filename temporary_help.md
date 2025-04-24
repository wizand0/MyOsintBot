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
## Создание пользователя
После этого вы увидите в реальном времени все сообщения от вашего бота — ошибки, отладочную информацию, любые print или logger.info.
```
SELECT User,Host FROM mysql.user
```
1. Создаём пользователя с паролем  
```
CREATE USER 'wizand0'@'%' IDENTIFIED BY 'Pol2E16Li3O4';
```

2. Делаем ему нужные привилегии (пример – даём все на базу mydb)  
```
GRANT ALL PRIVILEGES ON mydb.* TO 'wizand0'@'%';
```

3. Перезагружаем привилегии (обычно не требуется, но для надёжности):  
```
FLUSH PRIVILEGES;
```
вы выдавали GRANT на базу mydb, а пытаетесь работать с osint_bd – прав нет и поэтому 1044.

Что нужно сделать:

1. Залогиниться под админом (root или другим пользователем с правом GRANT), например:  
  ``` 
   mysql -u root -p
   ```

2. Выдать привилегии на нужную БД:  
   ```
   GRANT ALL PRIVILEGES  
     ON osint_bd.*  
     TO 'wizand0'@'%';
   ```
   Если вам не нужны «ALL», можно сузить до SELECT/INSERT/UPDATE и т.п.

3. (Опционально, в MariaDB обычно не требуется)  
   ```
   FLUSH PRIVILEGES;
4. ```

4. Проверить, что привилегии применились:  
   ```
   SHOW GRANTS FOR 'wizand0'@'%';
      ```
5. Выйти и попробовать подключиться уже под wizand0:  
   ```
   mysql -u wizand0 -p -h 127.0.0.1 -P 3306 osint_bd
   ```
   

root@2f8f18eae77c:/# apt install -y default-mysql-client

root@2f8f18eae77c:/# mysql -h 127.0.0.1 -P9306                                                                                                                                                                                                                
Welcome to the MariaDB monitor.  Commands end with ; or \g.                                                                                                                                                                                                   
Your MySQL connection id is 1
Server version: 2.2.11-id64-release (95ae9a6) 

Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

MySQL [(none)]> SHOW TABLES;
+-------+-------+
| Index | Type  |
+-------+-------+
| idx1  | local |
+-------+-------+
1 row in set (0.000 sec)

MySQL [(none)]> SELECT COUNT(*) FROM idx1;
ERROR 1064 (42000): index idx1: fullscan requires extern docinfo