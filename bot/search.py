# search.py
import logging
from typing import List, Dict

import aiomysql
from aiomysql import Pool

from .config import DB_CONFIG, logger
from .db import get_db_connection

from .config import SPHINX_HOST, SPHINX_PORT

_sphinx_pool = None

logger = logging.getLogger(__name__)


async def dbasync_perform_general_search(
        pool: aiomysql.Pool,
        search_query: str
) -> List[Dict]:
    """
    Выполняет общий поиск по всем текстовым столбцам всех таблиц,
    возвращая до 10 строк из каждой таблицы.
    """
    results: List[Dict] = []

    # Аквизим соединения из пула
    async with pool.acquire() as conn:
        # Для удобства используем DictCursor
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            try:
                # 1) Собираем список таблиц
                await cursor.execute(
                    "SELECT TABLE_NAME "
                    "FROM INFORMATION_SCHEMA.TABLES "
                    "WHERE TABLE_SCHEMA = %s",
                    (DB_CONFIG["database"],)
                )
                tables = await cursor.fetchall()  # List[{"TABLE_NAME": "..."}]

                for row in tables:
                    table_name = row["TABLE_NAME"]

                    # 2) Получаем текстовые колонки в этой таблице
                    await cursor.execute(
                        "SELECT COLUMN_NAME "
                        "FROM INFORMATION_SCHEMA.COLUMNS "
                        "WHERE TABLE_SCHEMA = %s "
                        "AND TABLE_NAME = %s "
                        "AND DATA_TYPE IN ('char','varchar','text')",
                        (DB_CONFIG["database"], table_name)
                    )
                    cols = await cursor.fetchall()
                    columns = [c["COLUMN_NAME"] for c in cols]
                    if not columns:
                        continue

                    # 3) Строим условие LIKE для каждой колонки
                    #    Параметры – это одинаковые шаблоны '%search_query%'
                    conditions = " OR ".join(f"{col} LIKE %s" for col in columns)
                    sql = f"SELECT * FROM {table_name} WHERE {conditions} LIMIT 10"
                    params = tuple(f"%{search_query}%" for _ in columns)

                    # 4) Выполняем поиск
                    try:
                        await cursor.execute(sql, params)
                        found = await cursor.fetchall()  # List[Dict]
                        for item in found:
                            item["table_name"] = table_name
                            results.append(item)
                    except Exception as e:
                        logger.error(f"Ошибка поиска в таблице {table_name}: {e!r}")

            except Exception as e:
                logger.error(f"Ошибка общего поиска: {e!r}")

    return results


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



async def dbasync_perform_phone_search(pool: Pool, search_query: str) -> list[dict]:
    """
    Асинхронный поиск по phone_number во всех таблицах схемы,
    где есть колонка phone_number.
    """
    logger.info("Начато async выполнение поиска по номеру телефона")
    results: list[dict] = []

    try:
        # 1) Захватываем одно соединение из пула
        async with pool.acquire() as conn:
            # 2) Создаем курсор с возвратом строк как dict
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # 3) Сначала находим все таблицы, где есть колонка phone_number
                await cursor.execute(
                    """
                    SELECT TABLE_NAME
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = %s
                      AND COLUMN_NAME = 'phone_number'
                    """,
                    (DB_CONFIG["database"],)
                )
                tables = [row["TABLE_NAME"] for row in await cursor.fetchall()]

                # 4) Для каждой таблицы – проверяем индекс и делаем LIKE‐запрос
                for table in tables:
                    logger.info("Поиск в таблице %s", table)

                    # проверим наличие индекса idx_phone
                    await cursor.execute(
                        f"SHOW INDEX FROM {table} WHERE Key_name = 'idx_phone'"
                    )
                    idx_row = await cursor.fetchone()
                    if idx_row:
                        like_pattern = f"{search_query}%"
                        logger.info(" → используем индекс idx_phone, LIKE '%s'", like_pattern)
                    else:
                        like_pattern = f"%{search_query}%"
                        logger.info(" → индекс не найден, LIKE '%%%s%%'", search_query)

                    sql = f"SELECT * FROM {table} WHERE phone_number LIKE %s LIMIT 10"
                    try:
                        await cursor.execute(sql, (like_pattern,))
                        rows = await cursor.fetchall()
                        # пометим, из какой таблицы пришла каждая строка
                        for r in rows:
                            r["table_name"] = table
                        results.extend(rows)

                    except Exception as e:
                        logger.error("Ошибка при поиске в %s: %s", table, e)

    except Exception:
        logger.exception("Критическая ошибка в dbasync_perform_search:")

    return results


async def get_sphinx_pool():
    global _sphinx_pool
    if _sphinx_pool is None:
        _sphinx_pool = await aiomysql.create_pool(
            host=SPHINX_HOST,
            port=SPHINX_PORT,
            user="",  # в SphinxQL можно пустые
            password="",
            db="",
            minsize=1,
            maxsize=5,
            autocommit=True,
        )
        return _sphinx_pool

async def sphinx_search_phone(prefix: str, limit: int = 10) -> list[dict]:
   pool = await get_sphinx_pool()
   async with pool.acquire() as conn:
       async with conn.cursor(aiomysql.DictCursor) as cur:
           if not prefix.isdigit():
               return []  # или обработайте ошибку
           match = f"@phone_number \"{prefix}\""
           sql = (
               f"SELECT * "
               f"FROM idx1 "
               f"WHERE MATCH('{match}') "
               f"LIMIT {int(limit)}"
           )
           await cur.execute(sql)
           rows = await cur.fetchall()
           return rows

           # SELECT * FROM
           # idx1
           # WHERE
           # MATCH('@phone_number "79152151368"')
           # LIMIT
           # 10;


           # MATCH ‑ prefix‑поиск по phone_number
           # match = f"@phone_number {prefix}*"
           # sql = (
           #     "SELECT id, phone_number, weight() AS score "
           #     "FROM idx1 "
           #     "WHERE MATCH(%s) "
           #     "LIMIT %s"
           # )
           # await cur.execute(sql, (match, limit))
           # rows = await cur.fetchall()
           # return rows