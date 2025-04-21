# ./docker/mysql/Dockerfile

FROM mariadb:latest

# чтобы add-apt-repository был доступен
RUN apt-get update \
   && apt-get install -y --no-install-recommends software-properties-common \
   && add-apt-repository universe \
   && apt-get update \
   && apt-get install -y mysqltuner \
   && rm -rf /var/lib/apt/lists/*

# при желании можно сразу скопировать свои конфиги
COPY ./conf.d/99-custom.cnf /etc/mysql/conf.d/99-custom.cnf

