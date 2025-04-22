#!/usr/bin/env sh
set -e

# 1) Ждём поднятия MariaDB
until mysql -h "$DB_HOST" -u"$DB_USER" -p"$DB_PASSWORD" \
    -e "SHOW DATABASES;" &>/dev/null
do
  echo "Waiting for MariaDB…"
  sleep 2
done

# 2) Подставляем переменные в шаблон
envsubst '${DB_HOST} ${DB_USER} ${DB_PASSWORD} ${DB_NAME} ${DB_PORT}'  \
  < /etc/sphinx/sphinx.conf.tpl \
  > /etc/sphinx/sphinx.conf

# 3) Индексируем
indexer --all --rotate

# 4) Запускаем демона
exec searchd --nodetach --config /etc/sphinx/sphinx.conf
# docker exec -it sphinx_search sh mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" -e "SHOW DATABASES;"

