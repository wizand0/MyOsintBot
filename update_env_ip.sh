#!/bin/bash

ENV_FILE=".env"  # <-- укажите путь к вашему .env

# Получаем локальный IP (например, первый из hostname -I)
LOCAL_IP=$(hostname -I | awk '{print $1}')

# Проверяем, что IP получен
if [[ -z "$LOCAL_IP" ]]; then
    echo "Не удалось определить локальный IP"
    exit 1
fi

# Заменяем строку YOUR_HOST_IP=... в .env
if grep -q "^YOUR_HOST_IP=" "$ENV_FILE"; then
    # Строка есть — заменяем
    sed -i "s/^YOUR_HOST_IP=.*/YOUR_HOST_IP=${LOCAL_IP}/" "$ENV_FILE"
else
    # Нет строки — добавляем в конец
    echo "YOUR_HOST_IP=${LOCAL_IP}" >> "$ENV_FILE"
fi
