# .\docker\sphinx\Dockerfile
FROM sphinxsearch/sphinx

# установим envsubst
RUN apt-get update && apt-get install -y gettext-base

# копируем tpl и скрипт
COPY conf/sphinx.conf.tpl  /etc/sphinx/sphinx.conf.tpl
COPY ./scripts/start-sphinx.sh /usr/local/bin/start-sphinx.sh
RUN chmod +x /usr/local/bin/start-sphinx.sh

ENTRYPOINT ["/usr/local/bin/start-sphinx.sh"]

