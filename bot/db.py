# db.py
import json
import os

import aiomysql
import mysql.connector
from mysql.connector import Error

from .config import DB_CONFIG


# Функция для подключения к базе данных
def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SET NAMES 'utf8';")
            return connection
    except Error as e:
        print("Ошибка подключения к базе данных", e)
    return None


async def init_db_pool() -> aiomysql.Pool:
    """
    Инициализируем пул соединений к MariaDB/MySQL.
    DB_CONFIG = {
      "host": "...",
      "port": 3306,
      "user": "...",
      "password": "...",
      "db": "...",
    }
    """
    pool = await aiomysql.create_pool(
        host=DB_CONFIG["host"],
        port=DB_CONFIG.get("port", 3306),
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        db=DB_CONFIG["database"],
        autocommit=True,
        minsize=1,
        maxsize=10,
        charset="utf8mb4",
    )
    return pool

async def close_db_pool(pool: aiomysql.Pool) -> None:
    pool.close()
    await pool.wait_closed()