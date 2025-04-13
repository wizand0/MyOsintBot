import mysql.connector
from mysql.connector import Error
from .config import DB_CONFIG


# Функция для подключения к базе данных
def get_db_connection():
    try:
        # connection = mysql.connector.connect(
        #     host=DB_CONFIG['host'],
        #     user=DB_CONFIG['user'],
        #     password=DB_CONFIG['password'],
        #     database=DB_CONFIG['database'],
        #     port=DB_CONFIG['port'],
        #     charset='utf8'
        # )
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SET NAMES 'utf8';")
            return connection
    except Error as e:
        print("Ошибка подключения к базе данных", e)
    return None