import streamlit as st


def show_admin_page():
    """Страница для администратора"""
    st.title("🔧 Панель администратора")
    st.write(f"Добро пожаловать, {st.session_state['name']}!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Управление пользователями")
        st.info("Здесь администратор может управлять пользователями системы")
        if st.button("Просмотреть всех пользователей"):
            st.success("Список пользователей загружен")
            st.write("1. admin@example.com - Администратор")
            st.write("2. user@example.com - Пользователь")
    
    with col2:
        st.subheader("Системные настройки")
        st.info("Доступ к системным настройкам")
        if st.button("Открыть настройки"):
            st.success("Настройки системы открыты")
            st.write("⚙️ Конфигурация базы данных")
            st.write("⚙️ Настройки безопасности")
            st.write("⚙️ Резервное копирование")
    
    st.subheader("Статистика")
    col3, col4, col5 = st.columns(3)
    with col3:
        st.metric("Активные пользователи", "2")
    with col4:
        st.metric("Сессии сегодня", "15")
    with col5:
        st.metric("Общий трафик", "1.2 ГБ")

if __name__ == "__main__":
    show_admin_page()
