source src1
{
    type            = mysql
    sql_host        = {{ DB_HOST }}
    sql_user        = {{ DB_USER }}
    sql_pass        = {{ DB_PASSWORD }}
    sql_db          = {{ DB_NAME }}
    sql_port        = {{ DB_PORT }}
    sql_query       = SELECT id, title, content FROM documents
}

index idx_main
{
    source          = src1
    path            = /var/lib/sphinx/data/idx_main
}

searchd
{
    listen          = 9306:mysql41
    log             = /var/log/sphinx/searchd.log
    query_log       = /var/log/sphinx/query.log
    pid_file        = /var/run/sphinx/searchd.pid
    max_children    = 30
    seamless_rotate = 1
    preopen_indexes = 1
    unlink_old      = 1
    workers         = threads
    binlog_path     = /var/lib/sphinx/data
}
