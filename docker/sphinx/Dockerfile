FROM macbre/sphinxsearch:latest

# создаём рабочие директории
RUN mkdir -p /etc/sphinx


# устанавливаем утилиты
RUN apk update \
 && apk add --no-cache mariadb-client gettext dos2unix \
 && rm -rf /var/cache/apk/*

# копируем шаблон конфига
COPY docker/sphinx/conf/sphinx.conf.tpl /etc/sphinx/sphinx.conf.tpl

# копируем и правим скрипт запуска
COPY docker/sphinx/scripts/start-sphinx.sh /usr/local/bin/start-sphinx.sh
RUN dos2unix /usr/local/bin/start-sphinx.sh \
 && chmod +x    /usr/local/bin/start-sphinx.sh

ENTRYPOINT ["/usr/local/bin/start-sphinx.sh"]
CMD []