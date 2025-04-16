## import_all_sql.sh

If you have several DB dumps in *.sql format in a specific directory, copy the following file from the project  
<br>for Windows:<br>
```
importallsql.bat  
```
Into the directory with the DB dumps and run the file via cmd (not in PowerShell):
```
import_all_sql.bat
```

For Linux:
copy
import_all_sql.sh
```
chmod +x import_all_sql.sh
./import_all_sql.sh
```


## Project Tree

Option 1. Using the tree command in the terminal (Linux / macOS / WSL)

1. Installing the tree utility:  

   • Ubuntu/Debian:  
     ```
     sudo apt update && sudo apt install tree
     ```

2. Generating the project tree:  
   Navigate to the root folder of your project and run the command:
   ```
   tree -L 2 > README.md
   ```

   Here:

   • -L 2 limits the displayed depth to 2 levels (replace the number with another value if necessary);

   • > README.md saves the output to the file README.md. If README.md already exists, the command will overwrite its contents.

---

Below is one approach for automatically generating a similar project structure, including a list of methods (functions) within files, which can be inserted into the Readme.md file. The idea is to write a specialized Python script that:

1. Recursively traverses the folders and files of the project.

2. For each Python file, uses the ast module to parse its contents and extract the function definitions (and, if necessary, class methods).

3. Formats a textual visualization in the form of a "tree" that can be inserted into the Readme.md.

Below is an example of such a script.

---

▎How to Use

1. Place the script.  
   Save the script in a file—for example, generate_tree.py in the root of your project.

2. Run the script.  
   Execute the following command in the terminal:
   
   python generate_tree.py > structure.txt
   
   The file structure.txt will contain the generated project tree with the list of functions (you can immediately open this file, copy its contents, and paste them into Readme.md).

3. Editing.  
   A small modification may be necessary for your needs. For example, you can choose to output functions only from the top level or also those inside classes, adjust the tree formatting, etc.

---

▎Note

If there is a .gitignore file in the root directory, it will be used to exclude the files and folders that meet the specified rules. To parse .gitignore, it is convenient to use the pathspec package (https://pypi.org/project/pathspec/). You can install it by running:
#### **pip install pathspec**

<br>
<br>

## split_sql.sh

скрипт, который делит SQL-дамп на указанное число частей (по умолчанию 10), разбивая файл примерно по количеству строк. Обратите внимание, что этот метод подходит для дампов, в которых каждая команда (например, INSERT) занимает одну строку или гарантированно завершается символом «;» в конце строки. Если ваши операторы разделены на несколько строк, то такое «механическое» разделение может повредить целостность SQL-запросов. В этом случае имеет смысл использовать более интеллектуальный парсер SQL или генерировать дамп по частям с помощью утилит БД.

Скрипт с комментариями:

---

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
OUTPUT_PREFIX="part_"
split -l "$LINES_PER_PART" -d --additional-suffix=.sql "$DUMP_FILE" "$OUTPUT_PREFIX"

echo "Разбивка завершена. Получены файлы:"
ls ${OUTPUT_PREFIX}*".sql"


---

▎Как использовать скрипт

1. Сохраните код в файл, например, split_sql.sh.

2. Сделайте его исполняемым:
      chmod +x split_sql.sh
   

3. Запустите скрипт:
      ./split_sql.sh dump.sql 10
   
   Где dump.sql — ваш исходный дамп, а 10 — число частей (если параметр не указан, по умолчанию будет 10).
   

▎Важно
— Если дамп содержит SQL-операторы, которые растянуты на несколько строк (например, многострочные INSERT), то деление по строкам может привести к разбиению одного оператора между файлами. Перед импортом в базу надо удостовериться, что каждый файл является корректным SQL-скриптом.  
— Если возможно, лучше получать дамп с разделением на части непосредственно средствами MariaDB (например, с помощью mysqldump с разбиением по таблицам или с использованием дополнительных флагов).

**Данный скрипт рассчитан на простые случаи и демонстрирует один из подходов для разделения больших SQL-дампов на части.**

**!!! Для Windows:**

Файл может иметь символы перевода строки в формате Windows — CRLF вместо LF). Тогда в шебанг-строке (#!/bin/bash) появляется невидимый символ возврата каретки (^M)
Чтобы проверить и исправить это, выполните следующие шаги:

1. Проверьте формат конца строк:

   Вы можете использовать команду file для определения, содержит ли файл DOS-линейные окончания:
      file split_sql.sh
   
   Если вывод будет содержать слово «CRLF», значит, файл сохранён в формате Windows.

2. Преобразуйте файл в формат Unix:

   Для этого можно использовать утилиту dos2unix. Если она не установлена, установите её (например, через apt):
      sudo apt-get update && sudo apt-get install dos2unix
   
   Затем выполните:
      dos2unix split_sql.sh
   

3. Проверьте права на выполнение:

   Убедитесь, что у файла есть права на выполнение:
      chmod +x split_sql.sh
   

4. Запустите скрипт с указанием нужного файла дампа, например:
      ./split_sql.sh beeline_full.sql