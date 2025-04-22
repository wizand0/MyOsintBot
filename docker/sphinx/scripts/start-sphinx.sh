#!/bin/bash
# ждём, пока поднимется БД
until mysql -h "${DB_HOST}" -u"${DB_USER}" -p"${DB_PASSWORD}" -e "SHOW DATABASES;" &>/dev/null; do
 echo "Waiting for MariaDB..."
 sleep 2
done



 #!/usr/bin/env sh
 set -e

 # подставляем нужные переменные из окружения
 envsubst
   '${DB_HOST} ${DB_USER} ${DB_PASSWORD} ${DB_NAME} ${DB_PORT}'
   < /etc/sphinx/sphinx.conf.tpl
   > /etc/sphinx/sphinx.conf


# проиндексируем
indexer --all --rotate
# запустим демона Sphinx
exec searchd --nodetach --config /etc/sphinxsearch/sphinx.conf

