import os
import logging
from dotenv import load_dotenv

from .data import load_allowed_users, save_allowed_users, load_user_stats, save_user_stats

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

SPHINX_HOST = os.getenv("SPHINX_HOST", "127.0.0.1")
SPHINX_PORT = int(os.getenv("SPHINX_PORT", 9306))

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

USER_STATS = load_user_stats()

# опционально — сразу сохраните, если файл не существовал
save_user_stats(USER_STATS)

# ===================== НАСТРОЙКИ ДЕТЕКЦИИ ДВИЖЕНИЯ =====================
# Производительность
MOTION_FRAME_SKIP = int(os.getenv('MOTION_FRAME_SKIP', '8'))  # Анализировать каждый N-й кадр
MOTION_COOLDOWN_SECONDS = int(os.getenv('MOTION_COOLDOWN_SECONDS', '15'))  # Cooldown между уведомлениями
MOTION_RESIZE_WIDTH = int(os.getenv('MOTION_RESIZE_WIDTH', '640'))  # Ширина для уменьшения кадра
MOTION_RESIZE_HEIGHT = int(os.getenv('MOTION_RESIZE_HEIGHT', '360'))  # Высота для уменьшения кадра

# Чувствительность детекции
MOTION_SENSITIVITY = int(os.getenv('MOTION_SENSITIVITY', '25'))  # Порог чувствительности
MOTION_MIN_AREA = int(os.getenv('MOTION_MIN_AREA', '1000'))  # Увеличили минимальную площадь
MOTION_RECOGNITION_DELAY_SEC = int(os.getenv('MOTION_RECOGNITION_DELAY_SEC', '4'))  # Задержка для YOLO

# YOLO настройки
YOLO_CONF_THRESHOLD = float(os.getenv('YOLO_CONF_THRESHOLD', '0.45'))  # Порог уверенности
YOLO_TARGET_CLASSES = os.getenv('YOLO_TARGET_CLASSES', 'person,cat,dog').split(',')  # Целевые классы

# Прочие настройки
MOTION_SAVE_FRAMES = os.getenv('MOTION_SAVE_FRAMES', 'True').lower() == 'true'
MOTION_PLAYBACK_SPEED = int(os.getenv('MOTION_PLAYBACK_SPEED', '8'))  # Скорость воспроизведения

# Настройки reconnect для RTSP
RECONNECT_INITIAL_DELAY = int(os.getenv('RECONNECT_INITIAL_DELAY', '1'))  # Начальная задержка retry в секундах
RECONNECT_MAX_DELAY = int(os.getenv('RECONNECT_MAX_DELAY', '60'))  # Максимальная задержка retry
HEALTH_TIMEOUT = int(os.getenv('HEALTH_TIMEOUT', '30'))  # Таймаут без новых кадров для reconnect

# .env
# RECONNECT_INITIAL_DELAY=1
# RECONNECT_MAX_DELAY=60
# HEALTH_TIMEOUT=30