import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from utils import PAGE_PERMISSIONS
from app_pages.admin import show_admin_page
from app_pages.user import show_user_page
from app_pages.velkome_page import show_velkome_page

# Конфигурация для пользователей и их ролей
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Создание объекта аутентификатора
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    
)

def main():
    # Размещение авторизации в боковой панели
    with st.sidebar:
        st.header("Авторизация")
        name, authentication_status, username = authenticator.login('Форма входа', 'main')

    # Основной контент
    if authentication_status:
        st.session_state['user_role'] = config['credentials']['usernames'][username]['role']
            # Отображение выбранной страницы
        
        with st.sidebar:
            
            if authentication_status:
                available_pages = [
                page for page, roles in PAGE_PERMISSIONS.items() 
                if st.session_state['user_role'] in roles
                ]
                selected_page = st.selectbox(
                    "Выберите страницу:",
                    available_pages,
                    key="current_page"
                )
            authenticator.logout('Выход', 'main', key='clear_cookies')
            
        if selected_page == "Главная":
            show_user_page()
        elif selected_page == "Админка":
            show_admin_page()
            
    elif authentication_status == False:
        show_velkome_page()
        with st.sidebar:
            st.error("Неверный логин или пароль")
    else:
        show_velkome_page()
        with st.sidebar:
            st.write("Пожалуйста, введите логин и пароль")
            
if __name__ == "__main__":
    main()