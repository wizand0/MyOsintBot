from .config import ALLOWED_USERS


# Функция проверки прав пользователя
def is_authorized(user_id: int) -> bool:
    return user_id in ALLOWED_USERS
