source src1
{
    type     = mysql
    sqlhost = mariadbserver
    sql_user = wizand0
    sql_pass = Pol2E16Li3O4
    sqldb   = osintbd
    sql_port = 3306
    sql_query= SELECT id, title, content FROM documents
}

index idx_main
{
    source = src1
    # единый путь + базовое имя; .sph, .spi, .spd и т.п. сформируются автоматически
    path   = /var/lib/sphinx/data/idx_main
}

searchd
{
    listen          = 9306:mysql41
    pid_file        = /tmp/searchd.pid
    log             = /tmp/searchd.log
    query_log       = /tmp/query.log
    seamless_rotate = 1
    preopen_indexes = 1
    unlink_old      = 1
    workers         = threads
    binlog_path     = /var/lib/sphinx/data
}