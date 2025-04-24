#!/usr/bin/env bash
set -e

# Генерируем sphinx.conf из шаблона
#envsubst < /etc/sphinxsearch/sphinx.conf.template > /etc/sphinxsearch/sphinx.conf

# если вызывают именно searchd – перед запуском пробуем один раз проиндексировать
if [ "$1" = "searchd" ]; then
  printf "[entrypoint] First run indexer --all --rotate"
  indexer --all --rotate || true
fi

chown -R sphinxsearch:sphinxsearch /var/lib/sphinxsearch

# передаём всё управление дальше
exec "$@"
