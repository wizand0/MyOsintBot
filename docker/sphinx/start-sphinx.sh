 #!/usr/bin/env sh
 set -e

 # подставляем нужные переменные из окружения
 envsubst
   '${DB_HOST} ${DB_USER} ${DB_PASSWORD} ${DB_NAME} ${DB_PORT}'
   < /etc/sphinx/sphinx.conf.tpl
   > /etc/sphinx/sphinx.conf

 # стартуем демона
 exec searchd --nodetach --config /etc/sphinx/sphinx.conf

