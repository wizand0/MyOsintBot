# auth.py
from .config import ALLOWED_USERS, ADMIN_ID


# Функция проверки прав пользователя
def is_authorized(user_id: int) -> bool:
    return user_id in ALLOWED_USERS


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID
