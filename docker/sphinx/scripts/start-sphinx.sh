#!/bin/sh
set -e

# 1) Ждём, пока БД будет доступна
echo "Waiting for DB at ${DB_HOST}:${DB_PORT:-3306}..."
until mysql -h"$DB_HOST" -P"${DB_PORT:-3306}" -u"$DB_USER" -p"$DB_PASSWORD" -e "SELECT 1" > /dev/null 2>&1; do
  printf '.'
  sleep 2
done
echo "\nDB is up!"

# 2) Рендерим шаблон в реальный конфиг
envsubst < /etc/sphinx/sphinx.conf.tpl > /etc/sphinx/sphinx.conf
echo "Generated /etc/sphinx/sphinx.conf:"
cat /etc/sphinx/sphinx.conf

# 3) Прогоняем initial-indexer (можно без --rotate,
#    если индексы ещё не заведены)
echo "Running indexer..."
indexer --config /etc/sphinx/sphinx.conf --all --rotate

# 4) Запускаем демона внутри контейнера (foreground)
echo "Starting searchd..."
exec searchd --nodetach --config /etc/sphinx/sphinx.conf
