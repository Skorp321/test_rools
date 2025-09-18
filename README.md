# Streamlit приложение с ограничением активных сессий

Это приложение реализует систему авторизации с ограничением количества активных сессий для каждого пользователя (максимум 1 активная сессия на пользователя).

## Функциональность

- ✅ Авторизация пользователей
- ✅ Управление сессиями с автоматическим разрывом старых при входе
- ✅ Автоматическая деактивация предыдущих сессий при входе
- ✅ Отслеживание активности сессий
- ✅ Автоматическая очистка неактивных сессий (через 9 часов)
- ✅ Управление доступом к страницам на основе ролей

## Структура базы данных

Приложение использует PostgreSQL с таблицами:
- `users` - пользователи
- `products` - продукты/страницы
- `product_users` - права доступа пользователей к продуктам
- `product_owners` - владельцы продуктов
- `user_sessions` - активные сессии пользователей

## Установка и запуск

### Предварительные требования

- Python 3.8+
- Docker и Docker Compose
- Git

### Быстрый запуск

1. **Клонируйте репозиторий:**
   ```bash
   git clone <repository-url>
   cd aut_str
   ```

2. **Запустите приложение одним из способов:**

   **Способ 1 - Bash скрипт:**
   ```bash
   ./run_app.sh
   ```

   **Способ 2 - Python скрипт:**
   ```bash
   python3 run_app.py
   ```

   **Способ 3 - Ручной запуск:**
   ```bash
   # Создайте виртуальное окружение
   python3 -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # или
   .venv\Scripts\activate     # Windows

   # Установите зависимости
   pip install -r requirements.txt

   # Запустите PostgreSQL
   docker-compose up -d postgres

   # Запустите приложение
   streamlit run test.py
   ```

3. **Откройте браузер:**
   ```
   http://localhost:8501
   ```

### Тестовые пользователи

- **Ivan** - имеет доступ к админке и главной странице
- **Petr** - имеет доступ только к главной странице

## Конфигурация

### База данных
Настройки подключения к PostgreSQL находятся в `config.yaml`:
```yaml
database:
  url: postgresql://aut_str_user:aut_str_password@localhost:5432/aut_str_db
```

### Cookie
Настройки cookie для сессий:
```yaml
cookie:
  expiry_days: 0.001  # Очень короткий срок жизни cookie
  key: superstrongkey
  name: demo_cookie
```

## Управление сессиями

### Логика работы
- При входе пользователя создается новая сессия
- Все предыдущие активные сессии для этого пользователя автоматически деактивируются
- Пользователь может войти в систему, даже если у него уже есть активная сессия (старая разорвется)
- Неактивные сессии автоматически удаляются через **9 часов**

### Функции управления сессиями

- `create_user_session()` - создание новой сессии
- `check_user_active_sessions()` - проверка количества активных сессий
- `deactivate_user_session()` - деактивация сессии
- `update_session_activity()` - обновление времени активности
- `cleanup_inactive_sessions()` - очистка неактивных сессий

## Структура проекта

```
aut_str/
├── app_pages/           # Страницы приложения
├── project/            # Дополнительные модули
├── task_kb/            # База знаний задач
├── models.py           # Модели базы данных и функции
├── test.py             # Основное приложение Streamlit
├── utils.py            # Утилиты
├── config.yaml         # Конфигурация
├── database.env        # Переменные окружения БД
├── docker-compose.yml  # Docker конфигурация
├── init.sql           # Инициализация БД
├── requirements.txt   # Python зависимости
├── run_app.sh         # Bash скрипт запуска
├── run_app.py         # Python скрипт запуска
└── README.md          # Документация
```

## Разработка

### Добавление новых страниц

1. Создайте функцию в `app_pages/`
2. Добавьте продукт в базу данных
3. Настройте права доступа в `product_users`

### Изменение времени очистки сессий

Измените время в `models.py`:
```python
# В функции cleanup_inactive_sessions измените интервал
UserSession.last_activity < func.current_timestamp() - func.interval('9 hours')
```

## Устранение неполадок

### База данных не подключается
```bash
# Проверьте статус контейнера
docker ps | grep postgres

# Перезапустите контейнер
docker-compose restart postgres
```

### Ошибки зависимостей
```bash
# Пересоздайте виртуальное окружение
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Проблемы с сессиями
```bash
# Очистите все сессии вручную
docker exec -it aut_str_postgres psql -U aut_str_user -d aut_str_db -c "DELETE FROM user_sessions;"
```

## Лицензия

MIT License
