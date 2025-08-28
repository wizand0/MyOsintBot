# Dockerfile
# Используем официальный Python-образ с конкретной версией
FROM python:3.13-slim

# Обновляем пакеты и устанавливаем дополнительные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    mariadb-client \
    lm-sensors \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgl1-mesa-glx \
 && rm -rf /var/lib/apt/lists/*

# Копируем файл requirements.txt и устанавливаем зависимости
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходники бота
COPY bot /app/bot

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

CMD ["python", "-m", "bot.main"]