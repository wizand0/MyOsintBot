# data.py
import json
import os

pending_requests = set()  # для хранения id пользователей, подавших заявку


ALLOWED_USERS_FILE = os.path.join(os.path.dirname(__file__), 'allowed_users.json')

def load_allowed_users() -> list:
    if os.path.exists(ALLOWED_USERS_FILE):
        try:
            with open(ALLOWED_USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_allowed_users(users: list) -> None:
    with open(ALLOWED_USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2)