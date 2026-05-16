from nicegui import app, ui
from src.database_query.auth import get_user_by_email

def login(email, password):
    result = get_user_by_email(email, password)
    if result and result.get("success") == True:
        app.storage.user['authenticated'] = True
        app.storage.user['email'] = result.get("email")
        app.storage.user['fullname'] = result.get("fullname")
        app.storage.user['role'] = result.get("role")
        return True
    return False
    
def logout():
    app.storage.user.update({'authenticated': False})
    ui.navigate.to('/signin')


