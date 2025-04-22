#!/usr/bin/env sh
set -e

# ждём Марию
until mysql -h "${DBHOST}" -u"${DBUSER}" -p"${DB_PASSWORD}" \
     -e "SHOW DATABASES;" >/dev/null; do
 echo "Waiting for MariaDB..."
 sleep 2
done

# генерим конфиг
envsubst '${DBHOST} ${DBUSER} ${DBPASSWORD} ${DBNAME} ${DB_PORT}' \
 < /etc/sphinx/sphinx.conf.tpl \
 > /etc/sphinx/sphinx.conf

# индексируем
indexer --all --rotate

# стартуем демона, причём путь к конфигу должен совпадать
exec searchd --nodetach --config /etc/sphinx/sphinx.conf