import os
import logging
from dotenv import load_dotenv

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

# Получаем список разрешенных пользователей из переменных окружения
allowed_users_str = os.getenv('ALLOWED_USERS', '')
ALLOWED_USERS = set()
if allowed_users_str:
    # Преобразуем строку вида "123456789,987654321" в множество чисел
    ALLOWED_USERS = {int(x.strip()) for x in allowed_users_str.split(',') if x.strip()}
