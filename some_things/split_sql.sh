#!/bin/bash
# Скрипт для разделения SQL дампа на N частей
# Использование:
#   ./split_sql.sh dump.sql [число_частей]
#
# По умолчанию число частей = 10

if [ "$#" -lt 1 ]; then
  echo "Использование: $0 <dump.sql> [число_частей]"
  exit 1
fi

DUMP_FILE="$1"
NUM_PARTS="${2:-10}"  # если не указано, использовать 10 частей

# Получаем «голое» имя дампа без пути и без расширения
BASE_NAME=$(basename "$DUMP_FILE")         # из «/path/to/dump.sql» сделает «dump.sql»
BASE_NO_EXT="${BASE_NAME%.*}"              # из «dump.sql» сделает «dump»



if [ ! -f "$DUMP_FILE" ]; then
  echo "Файл $DUMP_FILE не найден!"
  exit 1
fi

# Определяем общее число строк в дампе
TOTAL_LINES=$(wc -l < "$DUMP_FILE")
echo "Общее число строк в дампе: $TOTAL_LINES"

# Вычисляем число строк на часть
# Если число строк не делится ровно, то последняя часть может содержать меньше строк.
LINES_PER_PART=$(( (TOTAL_LINES + NUM_PARTS - 1) / NUM_PARTS ))
echo "Строк на каждую часть: $LINES_PER_PART"

# Используем утилиту split для разделения файла
# -l указывает число строк для каждого файла
# -d добавляет числовой суффикс (например, 00, 01, …)
# --additional-suffix задаёт расширение файла, например .sql


# Собираем префикс для split
# в результате файлы будут называться: dump_part_00.sql, dump_part_01.sql и т.д.
OUTPUT_PREFIX="${BASE_NO_EXT}_part_"
# OUTPUT_PREFIX="part_"


split -l "$LINES_PER_PART" -d --additional-suffix=.sql "$DUMP_FILE" "$OUTPUT_PREFIX"

echo "Разбивка завершена. Получены файлы:"
ls ${OUTPUT_PREFIX}*".sql"
