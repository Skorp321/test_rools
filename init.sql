-- Создание таблицы пользователей
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы продуктов
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT now()
);

-- Создание таблица пользователей с правами
CREATE TABLE product_users (
    id SERIAL PRIMARY KEY,
    product_id INT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role TEXT CHECK (role IN ('viewer', 'editor')) DEFAULT 'viewer',
    UNIQUE (product_id, user_id)
);

-- Сооздание таблицы владельцев проектов
CREATE TABLE product_owners (
    id SERIAL PRIMARY KEY,
    product_id INT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE (product_id, user_id)
);

-- Создание индексов
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- Вставка тестовых данных
INSERT INTO users (username) VALUES
('Ivan'),
('Petr'),
('Fedor')
ON CONFLICT (username) DO NOTHING;

-- Вставка продуктов
INSERT INTO products (name, description) VALUES
('admin', 'Административный продукт'),
('user', 'Пользовательский продукт')
ON CONFLICT DO NOTHING;

-- Вставка связей владения
INSERT INTO product_owners (product_id, user_id) VALUES
(1, 1), -- Ivan владеет admin
(2, 2)  -- Petr владеет user
ON CONFLICT (product_id, user_id) DO NOTHING;

-- Вставка прав доступа пользователей к продуктам
INSERT INTO product_users (product_id, user_id, role) VALUES
(1, 1, 'editor'), -- Ivan имеет доступ к admin как editor
(2, 1, 'editor'), -- Ivan имеет доступ к user как editor
(2, 2, 'viewer')  -- Petr имеет доступ к user как viewer
ON CONFLICT (product_id, user_id) DO NOTHING;

-- Схема базы данных для управления сессиями пользователей
-- Создание таблицы для хранения активных сессий

CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

-- Индекс для быстрого поиска по username
CREATE INDEX IF NOT EXISTS idx_user_sessions_username ON user_sessions(username);

-- Индекс для быстрого поиска по session_id
CREATE INDEX IF NOT EXISTS idx_user_sessions_session_id ON user_sessions(session_id);

-- Индекс для поиска активных сессий
CREATE INDEX IF NOT EXISTS idx_user_sessions_active ON user_sessions(is_active) WHERE is_active = TRUE;

-- Функция для очистки неактивных сессий (старше 9 часов)
CREATE OR REPLACE FUNCTION cleanup_inactive_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM user_sessions 
    WHERE last_activity < NOW() - INTERVAL '9 hours' 
    OR (is_active = FALSE AND created_at < NOW() - INTERVAL '1 hour');
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Создание триггера для автоматического обновления last_activity
CREATE OR REPLACE FUNCTION update_last_activity()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_activity = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Применение триггера к таблице (если нужно автоматическое обновление)
CREATE TRIGGER trigger_update_last_activity
    BEFORE UPDATE ON user_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_last_activity();

-- Создание таблицы для записи попыток входа неавторизованных пользователей
CREATE TABLE IF NOT EXISTS unauthorized_login_attempts (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    ip_address INET,
    user_agent TEXT,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reason TEXT DEFAULT 'User not found in product_users table'
);

-- Индекс для быстрого поиска по username
CREATE INDEX IF NOT EXISTS idx_unauthorized_login_attempts_username ON unauthorized_login_attempts(username);

-- Индекс для поиска по времени попытки
CREATE INDEX IF NOT EXISTS idx_unauthorized_login_attempts_attempted_at ON unauthorized_login_attempts(attempted_at);

-- Индекс для поиска по IP адресу
CREATE INDEX IF NOT EXISTS idx_unauthorized_login_attempts_ip ON unauthorized_login_attempts(ip_address);