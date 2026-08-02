#!/bin/bash
set -e

# Переходим в папку проекта
cd /root/parce_bot

# Проверяем, есть ли новые коммиты на GitHub
git fetch origin main
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" != "$REMOTE" ]; then
    echo "Обнаружены изменения, обновляем проект..."
    git pull origin main

    # Обновляем образы и запускаем контейнеры через Docker Compose
    docker-compose pull
    docker-compose up -d --build

    echo "Деплой успешно завершен!"
else
    echo "Обновлений нет."
fi
