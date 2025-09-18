#!/bin/bash

# Скрипт для добавления тестовых пользователей в LDAP

# Добавляем организационное подразделение для пользователей
ldapadd -x -D "cn=admin,dc=test,dc=local" -w admin -H ldap://localhost:389 << EOF
dn: ou=people,dc=test,dc=local
objectClass: top
objectClass: organizationalUnit
ou: people
description: Users
EOF

# Добавляем пользователя einstein
ldapadd -x -D "cn=admin,dc=test,dc=local" -w admin -H ldap://localhost:389 << EOF
dn: uid=einstein,ou=people,dc=test,dc=local
objectClass: inetOrgPerson
objectClass: posixAccount
objectClass: top
cn: Albert Einstein
sn: Einstein
uid: einstein
uidNumber: 1000
gidNumber: 1000
homeDirectory: /home/einstein
loginShell: /bin/bash
mail: einstein@test.local
userPassword: password
EOF

# Добавляем пользователя newton
ldapadd -x -D "cn=admin,dc=test,dc=local" -w admin -H ldap://localhost:389 << EOF
dn: uid=newton,ou=people,dc=test,dc=local
objectClass: inetOrgPerson
objectClass: posixAccount
objectClass: top
cn: Isaac Newton
sn: Newton
uid: newton
uidNumber: 1001
gidNumber: 1000
homeDirectory: /home/newton
loginShell: /bin/bash
mail: newton@test.local
userPassword: password
EOF

# Добавляем пользователя galileo
ldapadd -x -D "cn=admin,dc=test,dc=local" -w admin -H ldap://localhost:389 << EOF
dn: uid=galileo,ou=people,dc=test,dc=local
objectClass: inetOrgPerson
objectClass: posixAccount
objectClass: top
cn: Galileo Galilei
sn: Galilei
uid: galileo
uidNumber: 1002
gidNumber: 1000
homeDirectory: /home/galileo
loginShell: /bin/bash
mail: galileo@test.local
userPassword: password
EOF

echo "Пользователи добавлены в LDAP сервер!"
