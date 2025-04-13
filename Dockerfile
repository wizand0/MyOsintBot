# Используем официальный Python-образ (например, версия 3.10)
FROM python

# Обновляем пакеты и устанавливаем дополнительные зависимости, если они нужны
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install mariadb-client -y --no-install-recommends

# Копируем файл requirements.txt и устанавливаем зависимости
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходники бота
# COPY bot/ /app/
COPY bot /app/bot

# Если переменные окружения для бота хранятся в .env, их можно добавить при запуске контейнера через docker-compose
# Либо можно загрузить их внутри контейнера с помощью библиотеки python-dotenv (если она указана в requirements)

# Запускаем бота
# CMD ["python", "bot.py"]
CMD ["python", "-m", "bot.main"]
