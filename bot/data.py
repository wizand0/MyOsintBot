# data.py
import json
import os
from typing import Set, Dict

pending_requests = set()  # для хранения id пользователей, подавших заявку

# для хранения заявок в памяти
pending_requests: Set[int] = set()

ALLOWED_USERS_FILE = os.path.join(os.path.dirname(__file__), 'allowed_users.json')

STATS_FILE = os.path.join(os.path.dirname(__file__), "user_stats.json")


def load_allowed_users() -> Set[int]:
    """
    Считывает файл allowed_users.json (список [123,456,...])
    и возвращает множество {123,456,...}.
    Если файла нет или он битый — возвращает пустое множество.
    """
    if not os.path.exists(ALLOWED_USERS_FILE):
        return set()

    try:
        with open(ALLOWED_USERS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return set()

    # фильтруем мусор и приводим к int
    result: Set[int] = set()
    for item in data:
        if isinstance(item, (int, str)) and str(item).isdigit():
            result.add(int(item))
    return result


def save_allowed_users(users: Set[int]) -> None:
    """
    Принимает множество int и сохраняет его в JSON в виде отсортированного списка.
    """
    # сортировка нужна только для удобочитаемости файла
    to_dump = sorted(users)
    with open(ALLOWED_USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(to_dump, f, ensure_ascii=False, indent=2)


# Структура: { "<user_id>": { "general": int, "phone": int } }
def load_user_stats() -> Dict[str, Dict[str, int]]:
    if not os.path.exists(STATS_FILE):
        return {}
    try:
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # на всякий случай привести ключи к строкам и значения к int
            cleaned = {}
            for k, v in data.items():
                if not k.isdigit():
                    continue
                cleaned[k] = {
                    "general": int(v.get("general", 0)),
                    "phone": int(v.get("phone", 0)),
                }
            return cleaned
    except (OSError, json.JSONDecodeError):
        return {}


def save_user_stats(stats: Dict[str, Dict[str, int]]) -> None:
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
