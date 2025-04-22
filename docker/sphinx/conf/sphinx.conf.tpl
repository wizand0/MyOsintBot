# .\docker\sphinx\sphinx.conf.tpl
source src_osint
{
 type          = mysql
 sql_host      = ${DB_HOST}
 sql_user      = ${DB_USER}
 sql_pass      = ${DB_PASSWORD}
 sql_db        = ${DB_NAME}
 sql_port      = ${DB_PORT}
 …
}