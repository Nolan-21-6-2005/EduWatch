import nicegui as ui
from view.component.sidebar import show_sidebar
from view.pages.signin import show_sign_in
from view.pages.signup import show_sign_up
from nicegui import app, ui

@ui.page('/')
def main_page():
    if not app.storage.user.get('authenticated', False):
        return ui.navigate.to('/login')
    show_sidebar()

@ui.page('/signin')
def signin_page():
    show_sign_in()

@ui.page('/signup')
def signup_page():
    show_sign_up()

if __name__ in {"__main__", "__mp_main__"}:
    # BẮT BUỘC: Cần secret để mã hóa session user
    ui.run(storage_secret='thanh_xuan_2026_eduwatch')
