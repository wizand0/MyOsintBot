from bot.config import DB_CONFIG, logger
from bot.db import get_db_connection


def perform_general_search(search_query: str):
    connection = get_db_connection()
    if connection is None:
        return None
    results = []
    try:
        cursor = connection.cursor(dictionary=True)
        # Получаем список таблиц в указанной базе данных.
        cursor.execute(
            "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = %s",
            (DB_CONFIG['database'],)
        )
        tables = cursor.fetchall()

        for table in tables:
            table_name = table['TABLE_NAME']
            # Получаем имена текстовых столбцов для текущей таблицы.
            cursor.execute(
                "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s "
                "AND DATA_TYPE IN ('char','varchar','text')",
                (DB_CONFIG['database'], table_name)
            )
            columns_data = cursor.fetchall()
            columns = [row['COLUMN_NAME'] for row in columns_data]
            if not columns:
                continue  # В этой таблице нет текстовых столбцов

            # Формируем условие для поиска по каждому столбцу через LIKE.
            conditions = " OR ".join([f"{col} LIKE %s" for col in columns])
            query = f"SELECT * FROM {table_name} WHERE {conditions} LIMIT 10"
            params = tuple([f"%{search_query}%"] * len(columns))
            try:
                cursor.execute(query, params)
                table_results = cursor.fetchall()
                for row in table_results:
                    row['table_name'] = table_name  # Добавляем информацию, из какой таблицы найден результат
                    results.append(row)
            except Exception as e:
                logger.error(f"Ошибка поиска в таблице {table_name}: {e}")
    except Exception as e:
        logger.error(f"Ошибка выполнения общего поиска: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    return results


# Функция для поиска по номеру телефона
def perform_phone_search(search_query: str):
    logger.info("Начато выполнение поиска по номеру телефона")
    connection = get_db_connection()
    if connection is None:
        logger.info("connection is None")
        return None
    results = []
    try:
        cursor = connection.cursor(dictionary=True)
        # Получаем список таблиц, в которых есть столбец phone_number
        cursor.execute(
            "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.COLUMNS "
            "WHERE TABLE_SCHEMA = %s AND COLUMN_NAME = 'phone_number'",
            (DB_CONFIG['database'],)
        )
        tables = cursor.fetchall()
        for table in tables:

            table_name = table['TABLE_NAME']
            logger.info(f"Поиск по {table_name}")
            query = f"SELECT * FROM {table_name} WHERE phone_number LIKE %s LIMIT 10"
            param = f"%{search_query}%"
            try:
                cursor.execute(query, (param,))
                table_results = cursor.fetchall()
                for row in table_results:
                    row['table_name'] = table_name  # добавляем информацию о таблице
                    results.append(row)
            except Exception as e:
                logger.error(f"Ошибка поиска в таблице {table_name}: {e}")
        cursor.close()
    except Exception as e:
        logger.error(f"Ошибка выполнения поиска по телефону: {e}")
    finally:
        if connection.is_connected():
            connection.close()
    return results
