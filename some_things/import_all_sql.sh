#!/bin/bash
# Параметры подключения и имя контейнера
container="mariadb_server"
dbUser="root"
dbPass="!w1JM6bD2If7"
dbName="osint_bd"

# Получаем список всех *.sql файлов в текущем каталоге
files=( *.sql )
total=${#files[@]}

# Если файлов нет, то выходим
if [ "$total" -eq 0 ]; then
    echo "Файлы с расширением .sql не найдены. Завершение работы."
    exit 1
fi

i=0
# Обходим файлы
for file in "${files[@]}"; do
    ((i++))
    # Вычисляем процент выполнения
    percent=$(( i * 100 / total ))
    
    # Выводим информацию об импорте файла и прогрессе
    echo -e "\n---------------------------"
    echo -e "Импорт файла: $file ($i из $total) - $percent%"

    # Выполняем импорт SQL файла через docker
    # Читаем содержимое файла и направляем его в stdin контейнера
    docker exec -i "$container" mariadb -u "$dbUser" -p"$dbPass" "$dbName" < "$file"
    exitCode=$?
    
    # Вывод результата выполнения с использованием ANSI-цветов
    if [ $exitCode -eq 0 ]; then
        echo -e "033[0;32m✔️ Файл '$file' успешно импортирован.033[0m"
    else
        echo -e "033[0;31m✘ Ошибка при импорте файла '$file'.033[0m"
    fi
done

echo -e "\nИмпорт завершён."