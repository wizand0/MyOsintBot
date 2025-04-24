FROM debian:buster-slim

ENV SPHINX_VERSION=latest

RUN apt-get update && apt-get install -y --no-install-recommends \
    sphinxsearch \
 && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/lib/sphinxsearch/data && chown -R sphinxsearch:sphinxsearch /var/lib/sphinxsearch

# COPY sphinx-entrypoint.sh /usr/local/bin/

# COPY sphinx.conf.template /etc/sphinxsearch/
COPY Dockerfile /etc/sphinxsearch/test.txt

COPY sphinx.conf /etc/sphinxsearch/sphinx.conf
COPY sphinx-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/sphinx-entrypoint.sh

USER sphinxsearch

ENTRYPOINT ["sphinx-entrypoint.sh"]
CMD ["searchd","--nodetach","--config","/etc/sphinxsearch/sphinx.conf"]
