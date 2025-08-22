import streamlit as st

# Настройка страницы
st.set_page_config(
    page_title="Multi-page App",
    page_icon="🔐",
    layout="wide"
)

# Импортируем модуль аутентификации
from auth import authenticate_user, logout, USERS_DB

def main():
    """Главная страница приложения"""
    
    # Проверка аутентификации
    if not authenticate_user():
        return
    
    # Информация о пользователе в боковой панели
    with st.sidebar:
        st.markdown(f"### Добро пожаловать!")
        st.markdown(f"**Пользователь:** {st.session_state['current_user']}")
        st.markdown(f"**Роль:** {st.session_state['user_role']}")
        
        if st.button("Выйти"):
            logout()
            st.rerun()
        
        st.markdown("---")
        st.markdown("### ℹ️ Информация")
        st.info("Используйте навигацию выше для перехода между страницами")
    
    # Основной контент главной страницы
    st.title("🏠 Главная страница")
    st.markdown("Добро пожаловать в многостраничное приложение с ролевым доступом!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔐 Система безопасности")
        st.success("✅ Вы успешно авторизованы")
        st.info(f"Ваша роль: **{st.session_state['user_role']}**")
        
        st.markdown("### 📋 Доступные страницы")
        user_role = st.session_state['user_role']
        
        # Определяем доступ к страницам
        pages_access = {
            "🏠 Home": ["admin", "user", "manager"],
            "⚙️ Admin": ["admin"],
            "📊 Management": ["admin", "manager"],
            "👤 User Profile": ["user", "admin", "manager"]
        }
        
        for page, roles in pages_access.items():
            if user_role in roles:
                st.success(f"✅ {page}")
            else:
                st.error(f"❌ {page} (нет доступа)")
    
    with col2:
        st.markdown("### 📊 Статистика")
        st.metric("Всего пользователей", len(USERS_DB))
        st.metric("Ваша роль", user_role)
        st.metric("Активных сессий", "3")
        
        st.markdown("### 🚀 Быстрые действия")
        if user_role == "admin":
            if st.button("🔧 Панель администратора"):
                st.switch_page("pages/2_⚙️_Admin.py")
        
        if user_role in ["admin", "manager"]:
            if st.button("📈 Управление"):
                st.switch_page("pages/3_📊_Management.py")
        
        if st.button("👤 Мой профиль"):
            st.switch_page("pages/4_👤_User_Profile.py")

if __name__ == "__main__":
    main()