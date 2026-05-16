from nicegui import app, ui
from src.services.login_services import logout

def show_footer():
    # Lấy thông tin user từ storage (sử dụng .get() kèm giá trị mặc định để tránh lỗi nếu chưa đăng nhập)
    user_fullname = app.storage.user.get('fullname', 'Chưa đăng nhập')
    user_role = app.storage.user.get('role', 'User') 
    # Footer User (Đã được chuyển thành dữ liệu động)
    # Footer User (Phương án 2: Chữ + Icon nằm hàng riêng)
    ui.separator().classes("my-4")
        
    with ui.column().classes("w-full p-2 gap-3"):
        # Hàng nút bấm đăng xuất (chiếm 100% chiều ngang, bo góc nhẹ)
        ui.button("Đăng xuất", icon="logout", on_click=logout) \
            .props("flat rounded dense") \
            .classes("w-full text-gray-500 hover:text-red-600 hover:bg-red-50 text-xs font-medium justify-start")
        
        # Hàng thông tin cá nhân
        with ui.row().classes("items-center gap-3 no-wrap"):
            ui.avatar("person", color="grey-2", text_color="black")
            with ui.column().classes("gap-0"):
                ui.label(str(user_role).upper()).classes("text-sm font-bold text-gray-700")
                ui.label(user_fullname.upper()).classes("text-xs text-gray-400")
            
