import streamlit as st

# База данных пользователей
USERS_DB = {
    "admin": {"password": "admin123", "role": "admin"},
    "user": {"password": "user123", "role": "user"},  
    "manager": {"password": "manager123", "role": "manager"}
}

# Определение доступа к страницам по ролям
PAGE_PERMISSIONS = {
    "Home": ["admin", "user", "manager"],
    "Admin": ["admin"],
    "Management": ["admin", "manager"],
    "User_Profile": ["user", "admin", "manager"]
}

def authenticate_user():
    """Функция аутентификации пользователя"""
    
    def password_entered():
        username = st.session_state["username"]
        password = st.session_state["password"]
        
        if username in USERS_DB and USERS_DB[username]["password"] == password:
            st.session_state["password_correct"] = True
            st.session_state["user_role"] = USERS_DB[username]["role"]
            st.session_state["current_user"] = username
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    # Если пользователь не авторизован
    if "password_correct" not in st.session_state:
        st.markdown("### 🔐 Вход в систему")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.text_input("Логин", key="username", placeholder="Введите логин")
            st.text_input("Пароль", type="password", key="password", placeholder="Введите пароль")
            st.button("Войти", on_click=password_entered, type="primary")
        
        with col2:
            st.markdown("### 👥 Тестовые аккаунты:")
            st.code("""
admin / admin123
- Полный доступ ко всем страницам
            
manager / manager123  
- Доступ к управлению и профилю
            
user / user123
- Доступ только к профилю
            """)
        
        return False
        
    elif not st.session_state["password_correct"]:
        st.markdown("### 🔐 Вход в систему")
        st.text_input("Логин", key="username")
        st.text_input("Пароль", type="password", key="password")
        st.button("Войти", on_click=password_entered)
        st.error("😕 Неверный логин или пароль")
        return False
    else:
        return True

def check_page_access(page_name):
    """Проверка доступа к странице"""
    if "user_role" not in st.session_state:
        return False
    
    user_role = st.session_state["user_role"]
    return user_role in PAGE_PERMISSIONS.get(page_name, [])

def logout():
    """Выход из системы"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]

def show_access_denied():
    """Страница отказа в доступе"""
    st.error("🚫 Доступ запрещен")
    st.markdown("### У вас недостаточно прав для просмотра этой страницы")
    
    st.markdown("**Ваша текущая роль:** " + st.session_state.get("user_role", "Не определена"))
    
    if st.button("🏠 Вернуться на главную"):
        st.switch_page("main.py")