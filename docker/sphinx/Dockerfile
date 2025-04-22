# .\docker\sphinx\Dockerfile
# FROM sphinxsearch/sphinx
FROM macbre/sphinxsearch:latest


# установим envsubst
# RUN apk apt-get update && apt-get install -y gettext-base
RUN apk add --no-cache gettext dos2unix

# копируем tpl и скрипт
COPY docker/sphinx/conf/sphinx.conf.tpl  /etc/sphinx/sphinx.conf.tpl
COPY docker/sphinx/scripts/start-sphinx.sh /usr/local/bin/start-sphinx.sh
RUN dos2unix /usr/local/bin/start-sphinx.sh \
        & chmod +x /usr/local/bin/start-sphinx.sh
ENTRYPOINT ["/usr/local/bin/start-sphinx.sh"]
CMD []