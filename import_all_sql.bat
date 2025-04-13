@echo off
REM Отключаем расширение переменных (чтобы символ "!" в пароле не вызывал проблем)
SETLOCAL DISABLEDELAYEDEXPANSION

REM Переходим в каталог с SQL файлами
echo Starting script
REM cd /d "D:/backup/Fedora/mysql/os_mysql"
echo Finding sql files in:
timeout /t 2 >nul
echo %CD%
timeout /t 2 >nul


REM Для каждого файла .sql в каталоге выполняем импорт
for %%F in (*.sql) do (
    echo Importing file: %%F
    docker exec -i mariadb_server mariadb -u root -p!w1JM6bD2If7 osint_bd < "%%F"
    REM Немного задерживаем выполнение (по желанию)
    timeout /t 2 >nul
)

echo Ready
pause
