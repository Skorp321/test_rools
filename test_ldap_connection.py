#!/usr/bin/env python3
"""
Простой тест подключения к LDAP серверу
"""

import ldap
import sys

def test_ldap_connection():
    try:
        # Подключение к LDAP серверу
        server = ldap.initialize('ldap://localhost:389')
        server.protocol_version = ldap.VERSION3
        
        # Аутентификация администратора
        server.simple_bind_s('cn=admin,dc=test,dc=local', 'admin')
        print("✅ Подключение к LDAP серверу успешно")
        
        # Поиск пользователей
        search_base = 'dc=test,dc=local'
        search_filter = '(objectClass=inetOrgPerson)'
        result = server.search_s(search_base, ldap.SCOPE_SUBTREE, search_filter)
        
        print(f"✅ Найдено пользователей: {len(result)}")
        for dn, attrs in result:
            if 'uid' in attrs:
                uid = attrs['uid'][0].decode('utf-8')
                cn = attrs.get('cn', [b''])[0].decode('utf-8')
                print(f"   - {uid}: {cn}")
        
        # Тест аутентификации пользователя
        test_user = 'uid=newton,ou=people,dc=test,dc=local'
        test_password = 'password'
        
        try:
            server.simple_bind_s(test_user, test_password)
            print(f"✅ Аутентификация пользователя newton успешна")
        except ldap.INVALID_CREDENTIALS:
            print(f"❌ Неверные учетные данные для newton")
        except Exception as e:
            print(f"❌ Ошибка аутентификации: {e}")
        
        server.unbind_s()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка подключения к LDAP: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Тестирование подключения к LDAP серверу...")
    success = test_ldap_connection()
    sys.exit(0 if success else 1)
