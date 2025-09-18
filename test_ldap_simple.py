import streamlit as st
import subprocess
import json

def test_ldap_auth(username, password):
    """Простая функция аутентификации через ldapwhoami"""
    try:
        # Формируем DN пользователя
        user_dn = f"uid={username},ou=people,dc=test,dc=local"
        
        # Выполняем команду ldapwhoami для проверки аутентификации
        result = subprocess.run([
            'ldapwhoami', '-x', 
            '-H', 'ldap://localhost:389',
            '-D', user_dn,
            '-w', password
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            # Получаем информацию о пользователе
            user_info = get_user_info(username)
            return user_info
        else:
            return None
            
    except Exception as e:
        st.error(f"Ошибка аутентификации: {e}")
        return None

def get_user_info(username):
    """Получаем информацию о пользователе из LDAP"""
    try:
        # Выполняем поиск пользователя
        result = subprocess.run([
            'ldapsearch', '-x',
            '-H', 'ldap://localhost:389',
            '-D', 'cn=admin,dc=test,dc=local',
            '-w', 'admin',
            '-b', 'dc=test,dc=local',
            f'(uid={username})',
            'cn', 'mail', 'uid'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            # Парсим результат
            lines = result.stdout.split('\n')
            user_info = {'uid': username}
            
            for line in lines:
                if line.startswith('cn:'):
                    user_info['name'] = line.split(':', 1)[1].strip()
                elif line.startswith('mail:'):
                    user_info['email'] = line.split(':', 1)[1].strip()
                    
            return user_info
        else:
            return {'uid': username, 'name': username}
            
    except Exception as e:
        return {'uid': username, 'name': username}

def main():
    st.title("🔐 LDAP Авторизация (простая версия)")
    
    # Информация для входа
    st.info("**Тестовые учетные данные (локальный LDAP):**")
    st.write("**Логин:** newton, einstein, galileo")  
    st.write("**Пароль:** password")
    st.write("**LDAP сервер:** localhost:389")
    
    # Форма логина
    with st.form("login_form"):
        username = st.text_input("Логин", value="newton")
        password = st.text_input("Пароль", type="password", value="password")
        submit_button = st.form_submit_button("Войти")
        
        if submit_button:
            if username and password:
                with st.spinner("Проверка учетных данных..."):
                    user = test_ldap_auth(username, password)
                    
                if user:
                    st.success(f"Добро пожаловать, {user.get('name', username)}!")
                    st.json(user)
                else:
                    st.error("Ошибка авторизации - неверный логин или пароль")
                    st.warning("Убедитесь, что используете один из тестовых логинов: newton, einstein, galileo")
            else:
                st.error("Пожалуйста, введите логин и пароль")

if __name__ == "__main__":
    main()
