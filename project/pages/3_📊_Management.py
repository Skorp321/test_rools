import streamlit as st
import sys
import os

# Добавляем родительскую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import authenticate_user, check_page_access, show_access_denied, logout

st.set_page_config(page_title="Management", page_icon="📊")

# Проверка аутентификации
if not authenticate_user():
    st.stop()

# Проверка доступа к странице
if not check_page_access("Management"):
    show_access_denied()
    st.stop()

# Информация о пользователе в боковой панели
with st.sidebar:
    st.markdown(f"### Менеджер: {st.session_state['current_user']}")
    st.markdown(f"**Роль:** {st.session_state['user_role']}")
    
    if st.button("Выйти"):
        logout()
        st.switch_page("../main.py")
    
    st.markdown("---")
    st.markdown("### 📊 Панель управления")
    st.info("Доступ к аналитике и управлению")

# Основное содержимое страницы управления  
st.title("📊 Панель управления")
st.success("✅ Добро пожаловать в панель управления!")

# Общие метрики
st.markdown("### 📈 Ключевые показатели")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Выручка за месяц",
        value="₽125,430",
        delta="12,500"
    )

with col2:
    st.metric(
        label="Новые клиенты", 
        value="47",
        delta="5"
    )

with col3:
    st.metric(
        label="Конверсия",
        value="3.2%",
        delta="0.5%"
    )

with col4:
    st.metric(
        label="Средний чек",
        value="₽2,670",
        delta="-150"
    )

# Вкладки для разных разделов управления
tab1, tab2, tab3 = st.tabs(["📊 Аналитика", "👥 Клиенты", "⚡ Операции"])

with tab1:
    st.markdown("### Аналитика продаж")
    
    # Генерируем данные для графика
    import random
    import datetime
    
    dates = [datetime.date.today() - datetime.timedelta(days=i) for i in range(30, 0, -1)]
    sales = [random.randint(1000, 5000) for _ in dates]
    
    chart_data = {"Дата": dates, "Продажи (₽)": sales}
    st.line_chart(chart_data, x="Дата", y="Продажи (₽)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 Топ продуктов")
        products = {
            "Товар А": 1240,
            "Товар Б": 890, 
            "Товар В": 720,
            "Товар Г": 450,
            "Товар Д": 320
        }
        
        for product, sales in products.items():
            st.metric(product, f"₽{sales:,}")
    
    with col2:
        st.markdown("#### 🌍 Продажи по регионам")
        regions_data = {
            "Регион": ["Москва", "СПб", "Екатеринбург", "Казань", "Новосибирск"],
            "Продажи": [45000, 32000, 18000, 15000, 12000]
        }
        st.bar_chart(regions_data, x="Регион", y="Продажи")

with tab2:
    st.markdown("### Управление клиентами")
    
    # Фильтры
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox("Статус клиента", ["Все", "Активные", "Неактивные", "VIP"])
    
    with col2:
        region_filter = st.selectbox("Регион", ["Все", "Москва", "СПб", "Регионы"])
    
    with col3:
        period_filter = st.selectbox("Период", ["За месяц", "За квартал", "За год"])
    
    # Таблица клиентов
    st.markdown("#### Список клиентов")
    
    clients_data = {
        "Клиент": ["ООО Альфа", "ИП Иванов", "ООО Бета", "ООО Гамма"],
        "Статус": ["VIP", "Активный", "Активный", "Неактивный"],
        "Сумма покупок": ["₽125,000", "₽45,000", "₽78,000", "₽12,000"],
        "Последняя покупка": ["2024-01-18", "2024-01-15", "2024-01-10", "2023-12-20"]
    }
    
    st.dataframe(clients_data, use_container_width=True)
    
    # Действия с клиентами
    st.markdown("#### Быстрые действия")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📧 Отправить рассылку"):
            st.success("Рассылка запущена!")
    
    with col2:
        if st.button("📞 Запланировать звонки"):
            st.success("Звонки запланированы!")
    
    with col3:
        if st.button("📊 Экспорт данных"):
            st.success("Данные экспортированы!")

with tab3:
    st.markdown("### Операционное управление")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔧 Системные операции")
        
        if st.button("🔄 Обновить данные"):
            with st.spinner("Обновление данных..."):
                import time
                time.sleep(2)
                st.success("Данные обновлены!")
        
        if st.button("📊 Пересчитать метрики"):
            with st.spinner("Пересчет метрик..."):
                import time
                time.sleep(1)
                st.success("Метрики пересчитаны!")
        
        if st.button("🧹 Очистить кэш"):
            st.success("Кэш очищен!")
        
        if st.button("📋 Генерировать отчет"):
            st.success("Отчет сгенерирован!")
    
    with col2:
        st.markdown("#### ⚠️ Уведомления")
        
        notifications = [
            {"type": "warning", "message": "Низкий остаток товара А"},
            {"type": "info", "message": "Новый заказ от ООО Альфа"},
            {"type": "success", "message": "Платеж получен"},
            {"type": "error", "message": "Ошибка в системе оплаты"}
        ]
        
        for notif in notifications:
            if notif["type"] == "warning":
                st.warning(f"⚠️ {notif['message']}")
            elif notif["type"] == "info":
                st.info(f"ℹ️ {notif['message']}")
            elif notif["type"] == "success":
                st.success(f"✅ {notif['message']}")
            elif notif["type"] == "error":
                st.error(f"❌ {notif['message']}")