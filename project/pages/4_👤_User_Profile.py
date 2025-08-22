import streamlit as st
import sys
import os

# Добавляем родительскую директорию в путь для импорта  
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import authenticate_user, check_page_access, show_access_denied, logout

st.set_page_config(page_title="User Profile", page_icon="👤")

# Проверка аутентификации
if not authenticate_user():
    st.stop()

# Проверка доступа к странице
if not check_page_access("User_Profile"):
    show_access_denied()
    st.stop()

# Информация о пользователе в боковой панели
with st.sidebar:
    st.markdown(f"### {st.session_state['current_user']}")
    st.markdown(f"**Роль:** {st.session_state['user_role']}")
    
    if st.button("Выйти"):
        logout()
        st.switch_page("../main.py")
    
    st.markdown("---")
    st.markdown("### 👤 Личный кабинет")
    st.info("Управление профилем и настройками")

# Основное содержимое профиля пользователя
st.title("👤 Личный кабинет")
st.success(f"✅ Добро пожаловать, {st.session_state['current_user']}!")

# Вкладки профиля
tab1, tab2, tab3 = st.tabs(["📝 Профиль", "📊 Активность", "⚙️ Настройки"])

with tab1:
    st.markdown("### Информация о профиле")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### 📷 Аватар")
        # Заглушка для аватара
        st.markdown("""
        <div style='width: 150px; height: 150px; background: linear-gradient(45deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                    color: white; font-size: 48px; font-weight: bold;'>
            {initial}
        </div>
        """.format(initial=st.session_state['current_user'][0].upper()), unsafe_allow_html=True)
        
        if st.button("📤 Загрузить новое фото"):
            st.success("Функция загрузки фото")
    
    with col2:
        st.markdown("#### 📋 Персональные данные")
        
        with st.form("profile_form"):
            # Предзаполненные данные в зависимости от пользователя
            user_data = {
                "admin": {"name": "Администратор Системы", "email": "admin@company.com", "phone": "+7 (999) 000-00-01"},
                "manager": {"name": "Менеджер Отдела", "email": "manager@company.com", "phone": "+7 (999) 000-00-02"}, 
                "user": {"name": "Пользователь Системы", "email": "user@company.com", "phone": "+7 (999) 000-00-03"}
            }
            
            current_user_data = user_data.get(st.session_state['current_user'], 
                                            {"name": "Имя Фамилия", "email": "email@example.com", "phone": "+7 (999) 123-45-67"})
            
            name = st.text_input("Полное имя", value=current_user_data["name"])
            email = st.text_input("Email", value=current_user_data["email"])
            phone = st.text_input("Телефон", value=current_user_data["phone"])
            
            col_form1, col_form2 = st.columns(2)
            with col_form1:
                department = st.selectbox("Отдел", ["IT", "Продажи", "Маркетинг", "HR"])
            with col_form2:
                position = st.text_input("Должность", value="Специалист")
            
            bio = st.text_area("О себе", value="Расскажите о себе...")
            
            submitted = st.form_submit_button("💾 Сохранить изменения", type="primary")
            
            if submitted:
                st.success("✅ Профиль успешно обновлен!")
                # Здесь можно добавить сохранение в базу данных
    
    # Информация о роли
    st.markdown("---")
    st.markdown("### 🔐 Информация о доступе")
    
    role_info = {
        "admin": {
            "description": "Администратор системы",
            "permissions": ["Полный доступ ко всем функциям", "Управление пользователями", "Системные настройки", "Мониторинг"],
            "color": "red"
        },
        "manager": {
            "description": "Менеджер отдела", 
            "permissions": ["Панель управления", "Аналитика и отчеты", "Управление клиентами", "Операционные функции"],
            "color": "orange"
        },
        "user": {
            "description": "Пользователь системы",
            "permissions": ["Личный кабинет", "Просмотр профиля", "Основные функции"],
            "color": "green"
        }
    }
    
    current_role_info = role_info[st.session_state['user_role']]
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Роль:** {current_role_info['description']}")
        st.markdown(f"**Уровень доступа:** {st.session_state['user_role']}")
    
    with col2:
        st.markdown("**Доступные функции:**")
        for permission in current_role_info['permissions']:
            st.success(f"✅ {permission}")

with tab2:
    st.markdown("### 📊 Активность пользователя")
    
    # Статистика активности
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Дней в системе", "45", "5")
    
    with col2:
        st.metric("Всего действий", "1,234", "56")
    
    with col3:
        st.metric("Последний вход", "Сегодня")
    
    with col4:
        st.metric("Среднее время сессии", "25 мин", "3 мин")
    
    # График активности
    st.markdown("#### 📈 График активности за последние 14 дней")
    
    import random
    import datetime
    
    dates = [datetime.date.today() - datetime.timedelta(days=i) for i in range(14, 0, -1)]
    activities = [random.randint(0, 20) for _ in dates]
    
    chart_data = {"Дата": dates, "Количество действий": activities}
    st.area_chart(chart_data, x="Дата", y="Количество действий")
    
    # История последних действий
    st.markdown("#### 📋 Последние действия")
    
    actions_history = [
        {"time": "10:30", "action": "Вход в систему", "page": "Главная"},
        {"time": "10:25", "action": "Обновление профиля", "page": "Профиль"},
        {"time": "09:45", "action": "Просмотр отчета", "page": "Аналитика"},
        {"time": "09:30", "action": "Редактирование данных", "page": "Управление"},
        {"time": "09:15", "action": "Экспорт данных", "page": "Клиенты"}
    ]
    
    for action in actions_history:
        with st.container():
            col_time, col_action, col_page = st.columns([1, 3, 2])
            
            with col_time:
                st.markdown(f"**{action['time']}**")
            
            with col_action:
                st.markdown(action['action'])
            
            with col_page:
                st.markdown(f"`{action['page']}`")
            
            st.markdown("---")

with tab3:
    st.markdown("### ⚙️ Настройки аккаунта")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔔 Уведомления")
        
        email_notifications = st.checkbox("Email уведомления", value=True)
        push_notifications = st.checkbox("Push уведомления", value=True)
        sms_notifications = st.checkbox("SMS уведомления", value=False)
        
        st.markdown("#### 🎨 Интерфейс")
        
        theme = st.selectbox("Тема оформления", ["Светлая", "Темная", "Авто"])
        language = st.selectbox("Язык", ["Русский", "English"])
        timezone = st.selectbox("Часовой пояс", ["UTC+3 (Москва)", "UTC+0 (GMT)", "UTC+5 (Екатеринбург)"])
        
        if st.button("💾 Сохранить настройки"):
            st.success("Настройки сохранены!")
    
    with col2:
        st.markdown("#### 🔐 Безопасность")
        
        with st.form("security_form"):
            st.markdown("**Смена пароля**")
            current_password = st.text_input("Текущий пароль", type="password")
            new_password = st.text_input("Новый пароль", type="password")
            confirm_password = st.text_input("Подтвердите новый пароль", type="password")
            
            change_password = st.form_submit_button("🔑 Изменить пароль")
            
            if change_password:
                if new_password == confirm_password and len(new_password) > 0:
                    st.success("✅ Пароль успешно изменен!")
                else:
                    st.error("❌ Пароли не совпадают или пустые")
        
        st.markdown("**Сессии**")
        if st.button("🚪 Завершить все сессии"):
            st.warning("Все активные сессии завершены")
        
        st.markdown("**Двухфакторная аутентификация**")
        two_factor_enabled = st.checkbox("Включить 2FA", value=False)
        
        if two_factor_enabled:
            st.info("📱 Отсканируйте QR-код в приложении аутентификатора")
        
        st.markdown("#### 📊 Экспорт данных")
        
        if st.button("📥 Скачать мои данные"):
            st.success("Запрос на экспорт данных отправлен. Ссылка для скачивания будет отправлена на email.")
        
        if st.button("🗑️ Удалить аккаунт"):
            st.error("⚠️ Внимание! Это действие необратимо!")