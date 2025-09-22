#!/bin/bash

# Скрипт для запуска теста PostgreSQL с использованием .venv и uv

echo "🚀 Запуск теста PostgreSQL с SQLAlchemy"
echo "========================================"

# Проверяем, что PostgreSQL контейнер запущен
echo "📋 Проверяем статус PostgreSQL контейнера..."
if ! docker ps | grep -q "aut_str_postgres"; then
    echo "❌ PostgreSQL контейнер не запущен. Запускаем..."
    docker-compose up -d postgres
    echo "⏳ Ждем запуска PostgreSQL..."
    sleep 10
else
    echo "✅ PostgreSQL контейнер уже запущен"
fi

# Активируем существующее виртуальное окружение
echo "🔧 Активируем существующее виртуальное окружение .venv..."
source .venv/bin/activate

# Устанавливаем uv если его нет
if ! command -v uv &> /dev/null; then
    echo "📥 Устанавливаем uv..."
    pip install uv
fi

# Устанавливаем зависимости через uv
echo "📦 Устанавливаем зависимости через uv..."
uv pip install -r requirements.txt

# Запускаем тест
echo "🧪 Запускаем тест PostgreSQL..."
python test_postgres_connection.py

echo "✅ Тест завершен!"
