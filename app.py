from view.pages.dashboard import show_dashboard
from view.pages.signin import show_sign_in
from view.pages.signup import show_sign_up
from src.services.detection_service import gen_frames
from fastapi.responses import StreamingResponse
from nicegui import app, ui

@ui.page('/')
def main_page():
    if not app.storage.user.get('authenticated', False):
        return ui.navigate.to('/signin')
    show_dashboard()

@ui.page('/signin')
def signin_page():
    show_sign_in()

@ui.page('/signup')
def signup_page():
    show_sign_up()

@app.get('/video_feed')
def video_feed():
    return StreamingResponse(
        gen_frames(), 
        media_type='multipart/x-mixed-replace; boundary=frame'
    )

if __name__ in {"__main__", "__mp_main__"}:
    # BẮT BUỘC: Cần secret để mã hóa session user
    ui.run(storage_secret='thanh_xuan_2026_eduwatch')
