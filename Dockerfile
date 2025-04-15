# Dockerfile
# Используем официальный Python-образ (например, версия 3.10)
FROM python

# Обновляем пакеты и устанавливаем дополнительные зависимости, если они нужны
# RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*
# RUN apt-get update && apt-get install mariadb-client -y --no-install-recommends
# RUN apt-get update && apt-get install lm-sensors  -y --no-install-recommends

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    mariadb-client \
    lm-sensors \
 && rm -rf /var/lib/apt/lists/*

# символическая ссылку (symlink) внутри контейнера, чтобы `/sys/class/hwmon` указывал на смонтированную `/host_sys/class/hwmon`
# RUN rm -rf /sys/class/hwmon && ln -s /host_sys/class/hwmon /sys/class/hwmon

# Копируем файл requirements.txt и устанавливаем зависимости
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходники бота
# COPY bot/ /app/
COPY bot /app/bot

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh


# Если переменные окружения для бота хранятся в .env, их можно добавить при запуске контейнера через docker-compose
# Либо можно загрузить их внутри контейнера с помощью библиотеки python-dotenv (если она указана в requirements)

# Запускаем бота
# CMD ["python", "bot.py"]

# !!!!!!!!!!! Раскомментировать в Linux
# ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["python", "-m", "bot.main"]
