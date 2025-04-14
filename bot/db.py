# db.py
import json
import os

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
