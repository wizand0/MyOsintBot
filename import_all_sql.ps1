# Параметры подключения и имя контейнера
$container = "mariadb_server"
$dbUser    = "root"
$dbPass    = "!w1JM6bD2If7"
$dbName    = "osint_bd"

# Получаем список всех *.sql файлов в текущем каталоге
$files = Get-ChildItem -Filter "*.sql"
$total = $files.Count
$i = 0

foreach ($file in $files) {
    $i++
    # Вычисляем процент выполнения
    $percent = [math]::Round(($i / $total) * 100, 0)
    
    Write-Progress -Activity "Импорт файла" -Status "Обработка файла $($file.Name) ($i из $total)" -PercentComplete $percent

    Write-Host "`nНачинаю импорт файла: $($file.Name)" -ForegroundColor Cyan

    # Выполняем импорт, перенаправляя ошибки в вывод (2>&1)
    $output = Get-Content -Raw $file.FullName | docker exec -i $container mariadb -u $dbUser -p"$dbPass" $dbName 2>&1

    # Вывод результата выполнения
    if ($output) {
        Write-Host $output
    }

    # Проверяем код завершения docker-команды ($LASTEXITCODE)
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✔️ Файл '$($file.Name)' успешно импортирован." -ForegroundColor Green
    }
    else {
        Write-Host "✘ Ошибка при импорте файла '$($file.Name)'." -ForegroundColor Red
    }
}