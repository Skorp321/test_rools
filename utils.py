

PAGE_PERMISSIONS = {
    "Главная": ["admin", "user"],
    "Админка": ["admin"],

}

def has_access(page_name, user_role):
    """Проверка доступа к странице"""
    return user_role in PAGE_PERMISSIONS.get(page_name, [])