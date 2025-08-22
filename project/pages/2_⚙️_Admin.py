import streamlit as st
import sys
import os

# Добавляем родительскую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import authenticate_user, check_page_access, show_access_denied, logout, USERS_DB

st.set_page_config(page_title="Admin Panel", page_icon="⚙️")

# Проверка аутентификации
if not authenticate_user():
    st.stop()

# Проверка доступа к странице
if not check_page_access("Admin"):
    show_access_denied()
    st.stop()

# Информация о пользователе в боковой панели
with st.sidebar:
    st.markdown(f"### Администратор: {st.session_state['current_user']}")
    st.markdown(f"**Роль:** {st.session_state['user_role']}")
    
    if st.button("Выйти"):
        logout()
        st.switch_page("../main.py")
    
    st.markdown("---")
    st.markdown("### 🔧 Админ-панель")
    st.success("У вас есть полный доступ")

# Основное содержимое страницы администратора
st.title("⚙️ Панель администратора")
st.success("✅ Добро пожаловать в административную панель!")

# Вкладки для разных разделов администрирования
tab1, tab2, tab3 = st.tabs(["👥 Пользователи", "⚙️ Настройки", "📊 Мониторинг"])

with tab1:
    st.markdown("### Управление пользователями")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### Список пользователей")
        for username, data in USERS_DB.items():
            with st.expander(f"👤 {username} ({data['role']})"):
                st.write(f"**Роль:** {data['role']}")
                st.write(f"**Статус:** {'🟢 Онлайн' if username == st.session_state['current_user'] else '⚪ Офлайн'}")
                
                col_edit, col_delete = st.columns(2)
                with col_edit:
                    if st.button(f"Редактировать {username}", key=f"edit_{username}"):
                        st.success(f"Редактирование {username}")
                with col_delete:
                    if st.button(f"Удалить {username}", key=f"delete_{username}"):
                        st.error(f"Удален пользователь {username}")
    
    with col2:
        st.markdown("#### Быстрые действия")
        if st.button("➕ Добавить пользователя"):
            st.success("Форма добавления пользователя")
        
        if st.button("📧 Отправить уведомления"):
            st.success("Уведомления отправлены")
        
        if st.button("🔄 Обновить список"):
            st.rerun()

with tab2:
    st.markdown("### Системные настройки")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Безопасность")
        enable_2fa = st.checkbox("Включить двухфакторную аутентификацию", value=False)
        session_timeout = st.selectbox("Время сессии", ["30 минут", "1 час", "4 часа", "24 часа"])
        log_level = st.selectbox("Уровень логирования", ["ERROR", "WARNING", "INFO", "DEBUG"])
        
        if st.button("💾 Сохранить настройки"):
            st.success("Настройки сохранены!")
    
    with col2:
        st.markdown("#### Система")
        maintenance_mode = st.checkbox("Режим обслуживания", value=False)
        allow_registration = st.checkbox("Разрешить регистрацию", value=True)
        
        st.markdown("#### Резервное копирование")
        if st.button("💾 Создать резервную копию"):
            st.success("Резервная копия создана")
        
        if st.button("📥 Восстановить из копии"):
            st.warning("Функция восстановления")

with tab3:
    st.markdown("### Мониторинг системы")
    
    # Метрики
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Активные пользователи", "3", "1")
    
    with col2:
        st.metric("Использование CPU", "45%", "5%")
    
    with col3:
        st.metric("Использование RAM", "2.1GB", "0.3GB")
    
    with col4:
        st.metric("Дисковое пространство", "67%", "2%")
    
    # График активности
    st.markdown("#### График активности пользователей")
    import random
    import datetime
    
    dates = [datetime.date.today() - datetime.timedelta(days=i) for i in range(7, 0, -1)]
    users_online = [random.randint(1, 10) for _ in dates]
    
    chart_data = {"Дата": dates, "Активных пользователей": users_online}
    st.line_chart(chart_data, x="Дата", y="Активных пользователей")
    
    # Логи системы
    st.markdown("#### Последние события")
    st.text_area("Системные логи", 
                value="""2024-01-20 10:30:15 INFO: Пользователь admin вошел в систему
2024-01-20 10:25:32 INFO: Создана резервная копия базы данных  
2024-01-20 10:20:01 WARNING: Превышено время отклика на 200ms
2024-01-20 10:15:45 INFO: Обновлены настройки безопасности""", 
                height=150, disabled=True)