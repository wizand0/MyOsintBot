FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
   && apt-get install -y sphinxsearch \
   && rm -rf /var/lib/apt/lists/*
# скопируем конфиг
COPY conf/sphinx.conf /etc/sphinxsearch/sphinx.conf
# наш стартовый скрипт индексирует данные и запускает демона
COPY scripts/start-sphinx.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/start-sphinx.sh
ENTRYPOINT ["start-sphinx.sh"]

