#!/bin/bash
# Попытка создать симлинк, если это возможно
if [ -d /host_sys/class/hwmon ] && [ ! -e /sys/class/hwmon ]; then
  rm -rf /sys/class/hwmon
  ln -s /host_sys/class/hwmon /sys/class/hwmon
fi

# Запускаем основное приложение
exec "$@"
