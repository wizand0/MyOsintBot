#!/usr/bin/env bash
set -e

# Генерируем sphinx.conf из шаблона

# Создаём директорию для индексов, если не существует
mkdir -p /var/lib/sphinxsearch/data

# Пробуем сменить владельца, если есть права (можно обернуть в if)
chown -R sphinxsearch:sphinxsearch /var/lib/sphinxsearch || true

# если вызывают именно searchd – перед запуском пробуем один раз проиндексировать
if [ "$1" = "searchd" ]; then
  printf "[entrypoint] First run indexer --all --rotate"
  indexer --all --rotate || true
fi

#chown -R sphinxsearch:sphinxsearch /var/lib/sphinxsearch

# передаём всё управление дальше
exec "$@"
