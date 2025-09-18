#!/usr/bin/env python3
"""
Страница администрирования для просмотра попыток неавторизованного входа
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Добавляем путь к модулям проекта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import (
    get_unauthorized_login_attempts, 
    cleanup_old_unauthorized_attempts,
    get_user_sessions,
    get_user_sessions_stats,
    cleanup_old_user_sessions
)

def show_user_sessions_tab():
    """Отображение вкладки с информацией о сессиях пользователей"""
    st.header("👥 Сессии пользователей")
    
    # Боковая панель с фильтрами для сессий
    with st.sidebar:
        st.header("🔍 Фильтры сессий")
        
        # Фильтр по имени пользователя
        sessions_username_filter = st.text_input(
            "Имя пользователя (сессии)",
            placeholder="Введите имя пользователя для фильтрации",
            key="sessions_username_filter"
        )
        
        # Фильтр по количеству записей
        sessions_limit = st.slider(
            "Количество записей (сессии)",
            min_value=10,
            max_value=1000,
            value=100,
            step=10,
            key="sessions_limit"
        )
        
        # Фильтр по активности
        show_active_only = st.checkbox(
            "Только активные сессии",
            value=False,
            key="show_active_only"
        )
        
        # Кнопка очистки старых сессий
        st.header("🧹 Очистка сессий")
        sessions_days_to_keep = st.number_input(
            "Дней для хранения сессий",
            min_value=1,
            max_value=365,
            value=30,
            key="sessions_days_to_keep"
        )
        
        if st.button("🗑️ Очистить старые сессии", type="secondary", key="cleanup_sessions"):
            with st.spinner("Очистка старых сессий..."):
                deleted_count = cleanup_old_user_sessions(sessions_days_to_keep)
                st.success(f"Удалено {deleted_count} старых сессий")
                st.rerun()
    
    # Основной контент для сессий
    try:
        # Получение данных о сессиях
        with st.spinner("Загрузка данных о сессиях..."):
            sessions = get_user_sessions(
                username=sessions_username_filter if sessions_username_filter else None,
                limit=sessions_limit,
                active_only=show_active_only
            )
        
        if not sessions:
            st.info("📭 Нет записей сессий пользователей")
            return
        
        # Статистика по сессиям
        sessions_stats = get_user_sessions_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Всего сессий", sessions_stats['total_sessions'])
        
        with col2:
            st.metric("Активных сессий", sessions_stats['active_sessions'])
        
        with col3:
            st.metric("Уникальных пользователей", sessions_stats['unique_users'])
        
        with col4:
            st.metric("За последние 24ч", sessions_stats['recent_sessions'])
        
        # Таблица с данными о сессиях
        st.header("📊 Детальная информация о сессиях")
        
        # Подготовка данных для DataFrame
        sessions_df_data = []
        for session in sessions:
            status_icon = "🟢" if session['is_active'] else "🔴"
            status_text = "Активна" if session['is_active'] else "Неактивна"
            
            sessions_df_data.append({
                'ID': session['id'],
                'Пользователь': session['username'],
                'Статус': f"{status_icon} {status_text}",
                'IP адрес': session['ip_address'] or 'Не указан',
                'User Agent': session['user_agent'][:50] + '...' if session['user_agent'] and len(session['user_agent']) > 50 else session['user_agent'] or 'Не указан',
                'Создана': session['created_at'].strftime('%Y-%m-%d %H:%M:%S'),
                'Последняя активность': session['last_activity'].strftime('%Y-%m-%d %H:%M:%S') if session['last_activity'] else 'Не указана',
                'Session ID': session['session_id'][:20] + '...' if len(session['session_id']) > 20 else session['session_id']
            })
        
        sessions_df = pd.DataFrame(sessions_df_data)
        
        # Отображение таблицы сессий
        st.dataframe(
            sessions_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID": st.column_config.NumberColumn("ID", width="small"),
                "Пользователь": st.column_config.TextColumn("Пользователь", width="medium"),
                "Статус": st.column_config.TextColumn("Статус", width="small"),
                "IP адрес": st.column_config.TextColumn("IP адрес", width="medium"),
                "User Agent": st.column_config.TextColumn("User Agent", width="large"),
                "Создана": st.column_config.DatetimeColumn("Создана", width="medium"),
                "Последняя активность": st.column_config.DatetimeColumn("Последняя активность", width="medium"),
                "Session ID": st.column_config.TextColumn("Session ID", width="medium")
            }
        )
        
        # Анализ по пользователям (сессии)
        st.header("👥 Анализ сессий по пользователям")
        
        user_sessions_stats = {}
        for session in sessions:
            username = session['username']
            if username not in user_sessions_stats:
                user_sessions_stats[username] = {
                    'total_sessions': 0,
                    'active_sessions': 0,
                    'ips': set(),
                    'last_activity': session['last_activity'],
                    'first_session': session['created_at']
                }
            user_sessions_stats[username]['total_sessions'] += 1
            if session['is_active']:
                user_sessions_stats[username]['active_sessions'] += 1
            if session['ip_address']:
                user_sessions_stats[username]['ips'].add(session['ip_address'])
            if session['last_activity'] and (not user_sessions_stats[username]['last_activity'] or 
                                           session['last_activity'] > user_sessions_stats[username]['last_activity']):
                user_sessions_stats[username]['last_activity'] = session['last_activity']
            if session['created_at'] < user_sessions_stats[username]['first_session']:
                user_sessions_stats[username]['first_session'] = session['created_at']
        
        # Сортировка по количеству сессий
        sorted_user_sessions = sorted(user_sessions_stats.items(), key=lambda x: x[1]['total_sessions'], reverse=True)
        
        for username, stats in sorted_user_sessions[:10]:  # Топ 10 пользователей
            with st.expander(f"👤 {username} - {stats['total_sessions']} сессий ({stats['active_sessions']} активных)"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Всего сессий:** {stats['total_sessions']}")
                    st.write(f"**Активных сессий:** {stats['active_sessions']}")
                    st.write(f"**Уникальных IP:** {len(stats['ips'])}")
                with col2:
                    st.write(f"**Первая сессия:** {stats['first_session'].strftime('%Y-%m-%d %H:%M:%S')}")
                    if stats['last_activity']:
                        st.write(f"**Последняя активность:** {stats['last_activity'].strftime('%Y-%m-%d %H:%M:%S')}")
                    if stats['ips']:
                        st.write(f"**IP адреса:** {', '.join(list(stats['ips'])[:5])}")
        
        # Анализ по IP адресам (сессии)
        st.header("🌐 Анализ сессий по IP адресам")
        
        ip_sessions_stats = {}
        for session in sessions:
            ip = session['ip_address']
            if ip:
                if ip not in ip_sessions_stats:
                    ip_sessions_stats[ip] = {
                        'total_sessions': 0,
                        'active_sessions': 0,
                        'users': set(),
                        'last_activity': session['last_activity']
                    }
                ip_sessions_stats[ip]['total_sessions'] += 1
                if session['is_active']:
                    ip_sessions_stats[ip]['active_sessions'] += 1
                ip_sessions_stats[ip]['users'].add(session['username'])
                if session['last_activity'] and (not ip_sessions_stats[ip]['last_activity'] or 
                                               session['last_activity'] > ip_sessions_stats[ip]['last_activity']):
                    ip_sessions_stats[ip]['last_activity'] = session['last_activity']
        
        # Сортировка по количеству сессий
        sorted_ip_sessions = sorted(ip_sessions_stats.items(), key=lambda x: x[1]['total_sessions'], reverse=True)
        
        for ip, stats in sorted_ip_sessions[:10]:  # Топ 10 IP
            with st.expander(f"🌐 {ip} - {stats['total_sessions']} сессий ({stats['active_sessions']} активных)"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Всего сессий:** {stats['total_sessions']}")
                    st.write(f"**Активных сессий:** {stats['active_sessions']}")
                    st.write(f"**Уникальных пользователей:** {len(stats['users'])}")
                with col2:
                    if stats['last_activity']:
                        st.write(f"**Последняя активность:** {stats['last_activity'].strftime('%Y-%m-%d %H:%M:%S')}")
                    if stats['users']:
                        st.write(f"**Пользователи:** {', '.join(list(stats['users'])[:5])}")
        
    except Exception as e:
        st.error(f"❌ Ошибка при загрузке данных о сессиях: {e}")
        import traceback
        st.code(traceback.format_exc())

def show_unauthorized_logins_tab():
    """Отображение вкладки с попытками неавторизованного входа"""
    st.header("🔒 Попытки неавторизованного входа")
    
    # Боковая панель с фильтрами
    with st.sidebar:
        st.header("🔍 Фильтры попыток")
        
        # Фильтр по имени пользователя
        username_filter = st.text_input(
            "Имя пользователя",
            placeholder="Введите имя пользователя для фильтрации",
            key="unauthorized_username_filter"
        )
        
        # Фильтр по количеству записей
        limit = st.slider(
            "Количество записей",
            min_value=10,
            max_value=1000,
            value=100,
            step=10,
            key="unauthorized_limit"
        )
        
        # Кнопка очистки старых записей
        st.header("🧹 Очистка попыток")
        days_to_keep = st.number_input(
            "Дней для хранения записей",
            min_value=1,
            max_value=365,
            value=30,
            key="unauthorized_days_to_keep"
        )
        
        if st.button("🗑️ Очистить старые записи", type="secondary", key="cleanup_unauthorized"):
            with st.spinner("Очистка старых записей..."):
                deleted_count = cleanup_old_unauthorized_attempts(days_to_keep)
                st.success(f"Удалено {deleted_count} записей старше {days_to_keep} дней")
                st.rerun()
    
    # Основной контент
    try:
        # Получение данных
        with st.spinner("Загрузка данных..."):
            attempts = get_unauthorized_login_attempts(
                username=username_filter if username_filter else None,
                limit=limit
            )
        
        if not attempts:
            st.info("📭 Нет записей попыток неавторизованного входа")
            return
        
        # Статистика
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Всего попыток", len(attempts))
        
        with col2:
            unique_users = len(set(attempt['username'] for attempt in attempts))
            st.metric("Уникальных пользователей", unique_users)
        
        with col3:
            unique_ips = len(set(attempt['ip_address'] for attempt in attempts if attempt['ip_address']))
            st.metric("Уникальных IP", unique_ips)
        
        with col4:
            recent_attempts = len([a for a in attempts if 
                                 datetime.now() - a['attempted_at'].replace(tzinfo=None) < timedelta(hours=24)])
            st.metric("За последние 24ч", recent_attempts)
        
        # Таблица с данными
        st.header("📊 Детальная информация")
        
        # Подготовка данных для DataFrame
        df_data = []
        for attempt in attempts:
            df_data.append({
                'ID': attempt['id'],
                'Пользователь': attempt['username'],
                'IP адрес': attempt['ip_address'] or 'Не указан',
                'User Agent': attempt['user_agent'][:50] + '...' if attempt['user_agent'] and len(attempt['user_agent']) > 50 else attempt['user_agent'] or 'Не указан',
                'Время попытки': attempt['attempted_at'].strftime('%Y-%m-%d %H:%M:%S'),
                'Причина': attempt['reason']
            })
        
        df = pd.DataFrame(df_data)
        
        # Отображение таблицы
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID": st.column_config.NumberColumn("ID", width="small"),
                "Пользователь": st.column_config.TextColumn("Пользователь", width="medium"),
                "IP адрес": st.column_config.TextColumn("IP адрес", width="medium"),
                "User Agent": st.column_config.TextColumn("User Agent", width="large"),
                "Время попытки": st.column_config.DatetimeColumn("Время попытки", width="medium"),
                "Причина": st.column_config.TextColumn("Причина", width="large")
            }
        )
        
        # Анализ по пользователям
        st.header("👥 Анализ по пользователям")
        
        user_stats = {}
        for attempt in attempts:
            username = attempt['username']
            if username not in user_stats:
                user_stats[username] = {
                    'count': 0,
                    'ips': set(),
                    'last_attempt': attempt['attempted_at']
                }
            user_stats[username]['count'] += 1
            if attempt['ip_address']:
                user_stats[username]['ips'].add(attempt['ip_address'])
            if attempt['attempted_at'] > user_stats[username]['last_attempt']:
                user_stats[username]['last_attempt'] = attempt['attempted_at']
        
        # Сортировка по количеству попыток
        sorted_users = sorted(user_stats.items(), key=lambda x: x[1]['count'], reverse=True)
        
        for username, stats in sorted_users[:10]:  # Топ 10 пользователей
            with st.expander(f"👤 {username} - {stats['count']} попыток"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Количество попыток:** {stats['count']}")
                    st.write(f"**Уникальных IP:** {len(stats['ips'])}")
                with col2:
                    st.write(f"**Последняя попытка:** {stats['last_attempt'].strftime('%Y-%m-%d %H:%M:%S')}")
                    if stats['ips']:
                        st.write(f"**IP адреса:** {', '.join(list(stats['ips'])[:5])}")
        
        # Анализ по IP адресам
        st.header("🌐 Анализ по IP адресам")
        
        ip_stats = {}
        for attempt in attempts:
            ip = attempt['ip_address']
            if ip:
                if ip not in ip_stats:
                    ip_stats[ip] = {
                        'count': 0,
                        'users': set(),
                        'last_attempt': attempt['attempted_at']
                    }
                ip_stats[ip]['count'] += 1
                ip_stats[ip]['users'].add(attempt['username'])
                if attempt['attempted_at'] > ip_stats[ip]['last_attempt']:
                    ip_stats[ip]['last_attempt'] = attempt['attempted_at']
        
        # Сортировка по количеству попыток
        sorted_ips = sorted(ip_stats.items(), key=lambda x: x[1]['count'], reverse=True)
        
        for ip, stats in sorted_ips[:10]:  # Топ 10 IP
            with st.expander(f"🌐 {ip} - {stats['count']} попыток"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Количество попыток:** {stats['count']}")
                    st.write(f"**Уникальных пользователей:** {len(stats['users'])}")
                with col2:
                    st.write(f"**Последняя попытка:** {stats['last_attempt'].strftime('%Y-%m-%d %H:%M:%S')}")
                    if stats['users']:
                        st.write(f"**Пользователи:** {', '.join(list(stats['users'])[:5])}")
        
    except Exception as e:
        st.error(f"❌ Ошибка при загрузке данных: {e}")
        import traceback
        st.code(traceback.format_exc())

def main():
    """Главная функция приложения с вкладками"""
    st.set_page_config(
        page_title="Администрирование системы",
        page_icon="🔒",
        layout="wide"
    )
    
    st.title("🔒 Администрирование системы")
    
    # Создание вкладок
    tab1, tab2 = st.tabs(["🔒 Попытки неавторизованного входа", "👥 Сессии пользователей"])
    
    with tab1:
        show_unauthorized_logins_tab()
    
    with tab2:
        show_user_sessions_tab()

if __name__ == "__main__":
    main()
