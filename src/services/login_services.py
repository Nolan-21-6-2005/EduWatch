from nicegui import app, ui
from src.database_query.auth import get_user_by_email

def login(username, password):
    if get_user_by_email(email):
        app.storage.user['authenticated'] = True
        app.storage.user['email'] = email
        return True
    return False
    
def logout():
    app.storage.user.update({'authenticated': False})
    ui.navigate.to('/login')


