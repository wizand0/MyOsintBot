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