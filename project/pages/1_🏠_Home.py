import streamlit as st
import sys
import os

# Добавляем родительскую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import authenticate_user, logout

st.set_page_config(page_title="Home", page_icon="🏠")

# Проверка аутентификации
if not authenticate_user():
    st.stop()

# Информация о пользователе в боковой панели
with st.sidebar:
    st.markdown(f"### Пользователь: {st.session_state['current_user']}")
    st.markdown(f"**Роль:** {st.session_state['user_role']}")
    
    if st.button("Выйти"):
        logout()
        st.switch_page("../main.py")

# Основная страница (дублирует содержимое main.py для навигации)
st.title("🏠 Главная страница")
st.info("Это альтернативная точка входа на главную страницу через навигацию.")

if st.button("↩️ Перейти к основной главной странице"):
    st.switch_page("../main.py")