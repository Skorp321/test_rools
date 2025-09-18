from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine
import yaml
from yaml.loader import SafeLoader
import uuid
import os

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())

    product_users = relationship("ProductUser", back_populates="user")
    product_owners = relationship("ProductOwner", back_populates="user")

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    created_at = Column(DateTime, default=func.current_timestamp())

    product_users = relationship("ProductUser", back_populates="product")
    product_owners = relationship("ProductOwner", back_populates="product")

class ProductUser(Base):
    __tablename__ = 'product_users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    role = Column(String(20), nullable=False)  # 'viewer' или 'editor'

    product = relationship("Product", back_populates="product_users")
    user = relationship("User", back_populates="product_users")

class ProductOwner(Base):
    __tablename__ = 'product_owners'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    product = relationship("Product", back_populates="product_owners")
    user = relationship("User", back_populates="product_owners")

class UserSession(Base):
    __tablename__ = 'user_sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False)
    session_id = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    last_activity = Column(DateTime, default=func.current_timestamp())
    ip_address = Column(String(45))  # IPv6 может быть до 45 символов
    user_agent = Column(Text)
    is_active = Column(Boolean, default=True)

class UnauthorizedLoginAttempt(Base):
    __tablename__ = 'unauthorized_login_attempts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False)
    ip_address = Column(String(45))  # IPv6 может быть до 45 символов
    user_agent = Column(Text)
    attempted_at = Column(DateTime, default=func.current_timestamp())
    reason = Column(Text, default='User not found in product_users table')

# Функция для получения настроек базы данных из config.yaml
def get_database_config():
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    return config['database']['url']

# Создание движка базы данных
DATABASE_URL = get_database_config()
engine = create_engine(DATABASE_URL)

# Создание фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session():
    """Получение сессии базы данных"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Сессия будет закрыта в вызывающем коде

def authenticate_user(username: str, password: str, ip_address: str = None, user_agent: str = None) -> dict:
    """
    Аутентификация пользователя
    
    Args:
        username: Имя пользователя
        password: Пароль в открытом виде
        ip_address: IP адрес пользователя (опционально)
        user_agent: User agent браузера (опционально)
        
    Returns:
        dict: Информация о пользователе или None если аутентификация не удалась
    """
    db = get_db_session()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user:
            # Проверяем, есть ли у пользователя доступ к продуктам
            if check_user_in_product_users(username):
                # Получаем доступные продукты для пользователя
                available_products = get_user_available_products(user.id)
                return {
                    'id': user.id,
                    'username': user.username,
                    'available_products': available_products
                }
            else:
                # Пользователь существует, но не имеет доступа к продуктам
                log_unauthorized_login_attempt(
                    username=username,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    reason='User exists but has no access to any products'
                )
                return None
        else:
            # Пользователь не найден в системе
            log_unauthorized_login_attempt(
                username=username,
                ip_address=ip_address,
                user_agent=user_agent,
                reason='User not found in users table'
            )
            return None
    finally:
        db.close()

def get_user_by_username(username: str) -> dict:
    """
    Получение информации о пользователе по имени пользователя
    
    Args:
        username: Имя пользователя
        
    Returns:
        dict: Информация о пользователе или None если пользователь не найден или не имеет доступа к продуктам
    """
    db = get_db_session()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user and check_user_in_product_users(username):
            available_products = get_user_available_products(user.id)
            return {
                'id': user.id,
                'username': user.username,
                'available_products': available_products
            }
        return None
    finally:
        db.close()

def get_user_available_products(user_id: int) -> list:
    """
    Получение доступных продуктов для пользователя
    
    Args:
        user_id: ID пользователя
        
    Returns:
        list: Список доступных продуктов с ролями
    """
    db = get_db_session()
    try:
        # Получаем продукты, к которым у пользователя есть доступ
        product_users = db.query(ProductUser).filter(ProductUser.user_id == user_id).all()
        
        available_products = []
        for pu in product_users:
            product = db.query(Product).filter(Product.id == pu.product_id).first()
            if product:
                available_products.append({
                    'id': product.id,
                    'name': product.name,
                    'description': product.description,
                    'role': pu.role
                })
        
        return available_products
    finally:
        db.close()

def get_available_pages_for_user(user_id: int) -> list:
    """
    Получение доступных страниц для пользователя на основе его продуктов
    
    Args:
        user_id: ID пользователя
        
    Returns:
        list: Список доступных страниц
    """
    available_products = get_user_available_products(user_id)
    available_pages = []
    
    # Маппинг продуктов на страницы
    product_to_page = {
        'admin': 'Админка',
        'user': 'Главная'
    }
    
    for product in available_products:
        page_name = product_to_page.get(product['name'])
        if page_name and page_name not in available_pages:
            available_pages.append(page_name)
    
    return available_pages

def create_user_session(username: str, ip_address: str = None, user_agent: str = None) -> str:
    """
    Создание новой сессии для пользователя.
    Автоматически деактивирует все существующие активные сессии для этого пользователя.
    
    Args:
        username: Имя пользователя
        ip_address: IP адрес пользователя
        user_agent: User agent браузера
        
    Returns:
        str: ID созданной сессии
    """
    db = get_db_session()
    try:
        # Деактивируем все существующие активные сессии для этого пользователя
        # Это позволяет пользователю войти с новой сессией, разорвав старую
        db.query(UserSession).filter(
            UserSession.username == username,
            UserSession.is_active == True
        ).update({UserSession.is_active: False})
        
        # Создаем новую сессию
        session_id = str(uuid.uuid4())
        new_session = UserSession(
            username=username,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            is_active=True
        )
        
        db.add(new_session)
        db.commit()
        
        return session_id
    finally:
        db.close()

def check_user_active_sessions(username: str) -> int:
    """
    Проверка количества активных сессий для пользователя
    
    Args:
        username: Имя пользователя
        
    Returns:
        int: Количество активных сессий
    """
    db = get_db_session()
    try:
        count = db.query(UserSession).filter(
            UserSession.username == username,
            UserSession.is_active == True
        ).count()
        return count
    finally:
        db.close()

def check_session_active(session_id: str) -> bool:
    """
    Проверка активности сессии по session_id
    
    Args:
        session_id: ID сессии
        
    Returns:
        bool: True если сессия активна, False если неактивна или не найдена
    """
    db = get_db_session()
    try:
        session = db.query(UserSession).filter(
            UserSession.session_id == session_id,
            UserSession.is_active == True
        ).first()
        return session is not None
    finally:
        db.close()

def deactivate_user_session(session_id: str) -> bool:
    """
    Деактивация сессии пользователя
    
    Args:
        session_id: ID сессии
        
    Returns:
        bool: True если сессия была деактивирована, False если не найдена
    """
    db = get_db_session()
    try:
        session = db.query(UserSession).filter(
            UserSession.session_id == session_id,
            UserSession.is_active == True
        ).first()
        
        if session:
            session.is_active = False
            db.commit()
            return True
        return False
    finally:
        db.close()

def update_session_activity(session_id: str) -> bool:
    """
    Обновление времени последней активности сессии
    
    Args:
        session_id: ID сессии
        
    Returns:
        bool: True если сессия была обновлена, False если не найдена
    """
    db = get_db_session()
    try:
        session = db.query(UserSession).filter(
            UserSession.session_id == session_id,
            UserSession.is_active == True
        ).first()
        
        if session:
            session.last_activity = func.current_timestamp()
            db.commit()
            return True
        return False
    finally:
        db.close()

def cleanup_inactive_sessions() -> int:
    """
    Очистка неактивных сессий (старше 9 часов)
    
    Returns:
        int: Количество удаленных сессий
    """
    db = get_db_session()
    try:
        # Выполняем SQL запрос напрямую для корректной работы с интервалами
        result = db.execute(func.text("""
            DELETE FROM user_sessions 
            WHERE last_activity < CURRENT_TIMESTAMP - INTERVAL '9 hours' 
            OR (is_active = FALSE AND created_at < CURRENT_TIMESTAMP - INTERVAL '1 hour')
        """))
        
        db.commit()
        return result.rowcount
    finally:
        db.close()

def log_unauthorized_login_attempt(username: str, ip_address: str = None, user_agent: str = None, reason: str = None) -> int:
    """
    Запись попытки входа неавторизованного пользователя
    
    Args:
        username: Имя пользователя
        ip_address: IP адрес пользователя
        user_agent: User agent браузера
        reason: Причина отказа в доступе
        
    Returns:
        int: ID созданной записи
    """
    db = get_db_session()
    try:
        attempt = UnauthorizedLoginAttempt(
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            reason=reason or 'User not found in product_users table'
        )
        
        db.add(attempt)
        db.commit()
        db.refresh(attempt)
        
        return attempt.id
    finally:
        db.close()

def get_unauthorized_login_attempts(username: str = None, limit: int = 100) -> list:
    """
    Получение списка попыток неавторизованного входа
    
    Args:
        username: Фильтр по имени пользователя (опционально)
        limit: Максимальное количество записей
        
    Returns:
        list: Список попыток входа
    """
    db = get_db_session()
    try:
        query = db.query(UnauthorizedLoginAttempt)
        
        if username:
            query = query.filter(UnauthorizedLoginAttempt.username == username)
        
        attempts = query.order_by(UnauthorizedLoginAttempt.attempted_at.desc()).limit(limit).all()
        
        return [
            {
                'id': attempt.id,
                'username': attempt.username,
                'ip_address': attempt.ip_address,
                'user_agent': attempt.user_agent,
                'attempted_at': attempt.attempted_at,
                'reason': attempt.reason
            }
            for attempt in attempts
        ]
    finally:
        db.close()

def check_user_in_product_users(username: str) -> bool:
    """
    Проверка наличия пользователя в таблице product_users
    
    Args:
        username: Имя пользователя
        
    Returns:
        bool: True если пользователь найден в product_users, False если нет
    """
    db = get_db_session()
    try:
        # Сначала проверяем, существует ли пользователь в таблице users
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return False
        
        # Проверяем, есть ли у пользователя доступ к продуктам
        product_user = db.query(ProductUser).filter(ProductUser.user_id == user.id).first()
        return product_user is not None
    finally:
        db.close()

def cleanup_old_unauthorized_attempts(days: int = 30) -> int:
    """
    Очистка старых записей попыток неавторизованного входа
    
    Args:
        days: Количество дней для хранения записей
        
    Returns:
        int: Количество удаленных записей
    """
    db = get_db_session()
    try:
        result = db.execute(func.text("""
            DELETE FROM unauthorized_login_attempts 
            WHERE attempted_at < CURRENT_TIMESTAMP - INTERVAL '%s days'
        """ % days))
        
        db.commit()
        return result.rowcount
    finally:
        db.close()

def get_user_sessions(username: str = None, limit: int = 100, active_only: bool = False) -> list:
    """
    Получение списка сессий пользователей
    
    Args:
        username: Фильтр по имени пользователя (опционально)
        limit: Максимальное количество записей
        active_only: Показывать только активные сессии
        
    Returns:
        list: Список сессий пользователей
    """
    db = get_db_session()
    try:
        query = db.query(UserSession)
        
        if username:
            query = query.filter(UserSession.username == username)
        
        if active_only:
            query = query.filter(UserSession.is_active == True)
        
        sessions = query.order_by(UserSession.created_at.desc()).limit(limit).all()
        
        return [
            {
                'id': session.id,
                'username': session.username,
                'session_id': session.session_id,
                'created_at': session.created_at,
                'last_activity': session.last_activity,
                'ip_address': session.ip_address,
                'user_agent': session.user_agent,
                'is_active': session.is_active
            }
            for session in sessions
        ]
    finally:
        db.close()

def get_user_sessions_stats() -> dict:
    """
    Получение статистики по сессиям пользователей
    
    Returns:
        dict: Статистика по сессиям
    """
    db = get_db_session()
    try:
        total_sessions = db.query(UserSession).count()
        active_sessions = db.query(UserSession).filter(UserSession.is_active == True).count()
        unique_users = db.query(UserSession.username).distinct().count()
        
        # Сессии за последние 24 часа
        recent_sessions = db.execute(func.text("""
            SELECT COUNT(*) FROM user_sessions 
            WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
        """)).scalar()
        
        return {
            'total_sessions': total_sessions,
            'active_sessions': active_sessions,
            'unique_users': unique_users,
            'recent_sessions': recent_sessions
        }
    finally:
        db.close()

def cleanup_old_user_sessions(days: int = 30) -> int:
    """
    Очистка старых записей сессий пользователей
    
    Args:
        days: Количество дней для хранения записей
        
    Returns:
        int: Количество удаленных записей
    """
    db = get_db_session()
    try:
        result = db.execute(func.text("""
            DELETE FROM user_sessions 
            WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '%s days'
            AND is_active = FALSE
        """ % days))
        
        db.commit()
        return result.rowcount
    finally:
        db.close()
