FROM debian:bookworm-slim

ENV SPHINX_VERSION=latest

RUN apt-get update && apt-get install -y --no-install-recommends \
    default-mysql-client \
    sphinxsearch \
    procps \
    cron \
 && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/lib/sphinxsearch/data && chown -R sphinxsearch:sphinxsearch /var/lib/sphinxsearch

COPY sphinx.conf /etc/sphinxsearch/sphinx.conf
COPY sphinx-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/sphinx-entrypoint.sh

RUN mkdir -p /var/lib/sphinxsearch/data && \
    chown -R sphinxsearch:sphinxsearch /var/lib/sphinxsearch

ENTRYPOINT ["sphinx-entrypoint.sh"]
CMD ["searchd","--nodetach","--config","/etc/sphinxsearch/sphinx.conf"]