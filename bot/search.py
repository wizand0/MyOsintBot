# search.py

from .config import DB_CONFIG, logger
from .db import get_db_connection


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

def has_idx_phone(cursor, table_name):
    """
    Проверяем, есть ли в данной таблице индекс idx_phone
    """
    sql = """
      SELECT 1
      FROM information_schema.STATISTICS
      WHERE table_schema = %s
        AND table_name   = %s
        AND index_name   = 'idx_phone'
      LIMIT 1
    """
    cursor.execute(sql, (DB_CONFIG['database'], table_name))
    return cursor.fetchone() is not None


def perform_phone_search(search_query: str):
    logger.info("Начато выполнение поиска по номеру телефона")
    conn = get_db_connection()
    if conn is None:
        logger.error("Не удалось получить соединение с БД")
        return []

    results = []
    try:
        cursor = conn.cursor(dictionary=True)

        # 1) Найти все таблицы с колонкой phone_number
        cursor.execute(
            "SELECT TABLE_NAME "
            "FROM INFORMATION_SCHEMA.COLUMNS "
            "WHERE TABLE_SCHEMA = %s AND COLUMN_NAME = 'phone_number'",
            (DB_CONFIG['database'],)
        )
        tables = [row['TABLE_NAME'] for row in cursor.fetchall()]

        for table in tables:
            logger.info("Поиск в таблице %s", table)

            # 2) Проверяем, есть ли индекс idx_phone
            use_index = has_idx_phone(cursor, table)

            if use_index:
                # префиксный поиск: телефон начинается с нашего запроса
                like_pattern = f"{search_query}%"
                logger.info(" → Будем использовать индекс idx_phone, LIKE '%s'", like_pattern)
            else:
                # обычный поиск с двусторонним wildcard
                like_pattern = f"%{search_query}%"
                logger.info(" → Индекс idx_phone не найден, используем LIKE '%%%s%%'", search_query)

            # ВАЖНО: оборачиваем имя таблицы в backticks, чтобы обезопаситься от спецсимволов
            sql = f"SELECT * FROM {table} WHERE phone_number LIKE %s LIMIT 10"
            try:
                cursor.execute(sql, (like_pattern,))
                rows = cursor.fetchall()
                for r in rows:
                    r['table_name'] = table
                results += rows
            except Exception as e:
                logger.error("Ошибка при поиске в %s: %s", table, e)

        cursor.close()

    except Exception as e:
        logger.exception("Критическая ошибка при perform_phone_search:")
    finally:
        try:
            conn.close()
        except:
            pass

    return results