# config.py
import os
import logging
from dotenv import load_dotenv

from .data import load_allowed_users, save_allowed_users

# Загружаем переменные из файла .env
load_dotenv()

# Настройка логирования (вывод в консоль)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Получаем секретные данные из переменных окружения
TOKEN = os.getenv('TOKEN')
DB_CONFIG = {
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'osint_bd'),
    'port': int(os.getenv('DB_PORT', 3306))
}

# Считываем идентификатор администратора
ADMIN_ID = int(os.getenv('ADMIN_ID', '0'))

# Получаем пользователей из файла
ALLOWED_USERS = load_allowed_users()
if not ALLOWED_USERS:
    # Если файл пустой или отсутствует, берем из .env
    ALLOWED_USERS = [int(uid.strip()) for uid in os.getenv("ALLOWED_USERS", "").split(',') if uid.strip().isdigit()]
    if ADMIN_ID not in ALLOWED_USERS:
        ALLOWED_USERS.append(ADMIN_ID)
    save_allowed_users(ALLOWED_USERS)
