Database Import

1. Check if there are any tables in the DB:

2. Open PowerShell or another terminal on Windows.

3. Connect to the container by starting an interactive terminal:
   ```
   docker exec -it mariadb_server bash
   ```
3a. Install the MariaDB client:
   ```
   apt-get update && apt-get install mariadb-client
   ```

4. Start the MariaDB client:  
   Inside the container, execute:
   ```
   mariadb -u root -p
   ```
   When prompted, enter the password:
   ```
   [Root Password]
   ```
   After a successful login, you will enter the interactive MariaDB console (the prompt will look something like:
   ```
   MariaDB [(none)]>
   ```
).

5. Connect to the desired database and view the tables:  
   Execute:
   ```
   USE [Your_DB];
   SHOW TABLES;
   ```
   After the SHOW TABLES; command, a list of tables in the [Your_DB] database will be displayed.

6. Make sure that the dump file is located in the current directory or specify the full path to the file.

7. Execute the command to import the dump directly from Windows (cmd):
   ```
   docker exec -i mariadb_server mysql -u root -p!w1JM6bD2If7 osint_bd < dump.sql
   ```
   Please note that here the password is specified immediately after -p without a space. If, for security reasons, you do not want to specify it in the command, you can leave -p without the password; then, after running the command, you will be prompted for the password:
   ```
   docker exec -i mariadb_server mysql -u root -p osint_bd < dump.sql
   ```

8. After executing the command, the dump will be imported into the database [Your_DB].  
   In the process, any new tables that were not present will be created if they are described in the dump.

---

▎If there was a mistake during development, then in the project directory:

▎1. Reset the containers:
```
docker-compose down -v
```

▎2. Restart them:
```
docker-compose up -d
```

p.s. If you have several DB dumps in *.sql format in a specific directory, copy the following file from the project  
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
