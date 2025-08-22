import streamlit as st


def show_user_page():
    """Страница для обычного пользователя"""
    st.title("👤 Пользовательская панель")
    st.write(f"Добро пожаловать, {st.session_state['name']}!")
    
    st.subheader("Ваш профиль")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("Информация о профиле")
        st.write(f"**Имя:** {st.session_state['name']}")
        st.write(f"**Логин:** {st.session_state['username']}")
        st.write(f"**Роль:** Пользователь")
        st.write(f"**Email:** user@example.com")
    
    with col2:
        st.info("Доступные функции")
        if st.button("Просмотреть документы"):
            st.success("Загружен список ваших документов")
            st.write("📄 Документ 1.pdf")
            st.write("📄 Документ 2.docx")
            st.write("📄 Отчет за месяц.xlsx")
    
    st.subheader("Быстрые действия")
    col3, col4 = st.columns(2)
    
    with col3:
        if st.button("Создать новый документ"):
            st.success("Редактор документов открыт")
    
    with col4:
        if st.button("Загрузить файл"):
            st.info("Функция загрузки файлов")
            
if __name__ == "__main__":
    show_user_page()