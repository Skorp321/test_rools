import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from utils import PAGE_PERMISSIONS
from app_pages.admin import show_admin_page
from app_pages.user import show_user_page
from app_pages.velkome_page import show_velkome_page
from models import (
    authenticate_user, 
    get_user_by_username, 
    get_available_pages_for_user,
    create_user_session,
    check_user_active_sessions,
    check_session_active,
    deactivate_user_session,
    update_session_activity,
    cleanup_inactive_sessions
)

# Конфигурация для cookie (остается в config.yaml)
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Передаем минимальную структуру, которую ожидает streamlit_authenticator
fake_credentials = {
    'usernames': {}
}
authenticator = stauth.Authenticate(
    fake_credentials,
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)

def force_logout():
    """Принудительный выход пользователя из системы"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.user_info = None
    st.session_state.session_id = None
    st.rerun()

def check_session_validity():
    """Проверка валидности текущей сессии"""
    if st.session_state.authenticated and st.session_state.session_id:
        if not check_session_active(st.session_state.session_id):
            force_logout()
            return False
    return True

def main():
    # Периодическая очистка неактивных сессий (выполняется при каждом запуске)
    cleanup_inactive_sessions()
    
    # Инициализация session_state в самом начале
    if "ip_address" not in st.session_state:
        st.session_state.ip_address = '127.0.0.1'
    if "user_agent" not in st.session_state:
        st.session_state.user_agent = None
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    
    # Проверяем валидность сессии перед отображением интерфейса
    if not check_session_validity():
        return

    with st.sidebar:
        st.header("Авторизация")
        
        if not st.session_state.authenticated:
            # Форма входа
            with st.form("login_form"):
                username = st.text_input("Имя пользователя")
                password = st.text_input("Пароль", type="password")
                submit_button = st.form_submit_button("Войти")
                
                if submit_button:
                    if username and password:
                        user_info = authenticate_user(
                            username, 
                            password, 
                            ip_address=st.session_state.ip_address,
                            user_agent=st.session_state.user_agent
                        )
                        if user_info:
                            # Создаем новую сессию
                            session_id = create_user_session(
                                username=username,
                                ip_address=st.session_state.ip_address,
                                user_agent=st.session_state.user_agent
                            )
                            
                            st.session_state.authenticated = True
                            st.session_state.username = username
                            st.session_state.user_info = user_info
                            st.session_state.session_id = session_id
                            st.success(f"Добро пожаловать, {username}!")
                            st.rerun()
                        else:
                            st.error("Неверный логин или пароль")
                    else:
                        st.error("Пожалуйста, заполните все поля")
        else:
            # Пользователь авторизован
            user_info = st.session_state.user_info
            st.success(f"Вы вошли как: {user_info['username']}")
            
            # Кнопка выхода
            if st.button("Выход"):
                # Деактивируем сессию в базе данных
                if st.session_state.session_id:
                    deactivate_user_session(st.session_state.session_id)
                
                st.session_state.authenticated = False
                st.session_state.username = None
                st.session_state.user_info = None
                st.session_state.session_id = None
                st.rerun()

    # Основной контент
    if st.session_state.authenticated:
        # Проверяем валидность сессии перед обновлением активности
        if not check_session_validity():
            return  # Если сессия невалидна, функция уже выполнила принудительный выход
        
        # Обновляем активность сессии
        if st.session_state.session_id:
            update_session_activity(st.session_state.session_id)
        
        user_info = st.session_state.user_info
        
        with st.sidebar:
            # Получаем доступные страницы из базы данных
            available_pages = get_available_pages_for_user(user_info['id'])
            
            if available_pages:
                selected_page = st.selectbox(
                    "Выберите страницу:",
                    available_pages,
                    key="current_page"
                )
            else:
                st.warning("У вас нет доступа ни к одной странице")
                selected_page = None
            
        # Отображение выбранной страницы
        if selected_page == "Главная":
            show_user_page()
        elif selected_page == "Админка":
            show_admin_page()
        elif selected_page is None:
            st.info("Выберите страницу из списка выше")
    else:
        # Показываем приветственную страницу для неавторизованных пользователей
        show_velkome_page()
        with st.sidebar:
            st.write("Пожалуйста, войдите в систему")
            
if __name__ == "__main__":
    main()