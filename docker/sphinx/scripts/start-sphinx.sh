#!/bin/sh
set -e

# --- опционально: ждём базу данных
echo "Waiting for DB at $DB_HOST..."
until mysql -h"$DB_HOST" -u"$DB_USER" -p"$DB_PASSWORD" -e "SELECT 1" >/dev/null 2>&1; do
  echo -n "."
  sleep 2
done
echo "DB is up!"

# --- генерируем реальный конфиг
envsubst < /etc/sphinx/sphinx.conf.tpl > /etc/sphinx/sphinx.conf
echo "Using sphinx config:"
cat /etc/sphinx/sphinx.conf

# --- запускаем демона
exec searchd --nodetach --config /etc/sphinx/sphinx.conf
