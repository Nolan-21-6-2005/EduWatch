from nicegui import ui
from view.component.sidebar import show_sidebar
from view.component.header import show_header
from view.pages.detector import show_detector

def show_dashboard():
    # Sử dụng no-wrap để Sidebar không bị nhảy dòng
    with ui.row().classes("w-full h-screen no-wrap m-0 p-0 overflow-hidden"):
        
        # 1. Khởi tạo Sidebar (Trong này đã bao gồm việc tạo content_panels)
        # Nhưng chúng ta cần chỉnh lại sidebar.py một chút (xem bước 2)
        panels = show_sidebar()
        
        # 2. Vùng bên phải (Header + Nội dung)
        with ui.column().classes("flex-grow h-full overflow-hidden bg-gray-50"):
            show_header()
            
            # Thay vì .add(panels), bạn chỉ cần di chuyển panels vào đây bằng cách gán lại parent
            panels.move(ui.context.slot.parent) 
            panels.classes("flex-grow w-full")
