import streamlit as st
from streamlit_ldap_authenticator import Authenticate

# Конфигурация подключения к локальному LDAP серверу
ldap_config = {
        "ldap": {
            "server_path": "ldap://localhost:389",
            "domain": "test.local",
            "search_base": "ou=people,dc=test,dc=local",
            "attributes": [
                "cn",
                "mail",
                "uidNumber",
            ],
            "use_ssl": True,
            },
            "session_state_names": {
                "user": "login_user",
                "remember_me": "login_remember_me",
            },
            "cookie": {
                "name": "login_session",
                "key": "login_session_key",
                "expiry_days": 1,
                "auto_renewal": True,
                "delay_sec": 0.1,
            },
        }
# Инициализация аутентификатора
authenticator = Authenticate(
    ldap_config['ldap'],
    ldap_config['session_state_names'],
    ldap_config['cookie'],
    )

def main():
    st.title("🔐 LDAP Авторизация (демо)")
    
    # Информация для входа
    st.info("**Тестовые учетные данные (локальный LDAP):**")
    st.write("**Логин:** newton, einstein, galileo")  
    st.write("**Пароль:** password")
    st.write("**LDAP сервер:** localhost:389")
    
    # Форма логина
    try:
        user = authenticator.login()
        
        if user:
            st.success(f"Добро пожаловать, {user.get('name', user.get('cn', 'Пользователь'))}!")
            st.json(user)  # покажем, что вернул LDAP (атрибуты)
        elif user is False:
            st.error("Ошибка авторизации - неверный логин или пароль")
            st.warning("Убедитесь, что используете один из тестовых логинов: newton, einstein, galileo")
        else:
            st.info("Введите учетные данные для входа")
            
    except Exception as e:
        st.error(f"Ошибка при инициализации аутентификатора: {e}")
        st.info("Попробуйте перезапустить приложение")

if __name__ == "__main__":
    main()
