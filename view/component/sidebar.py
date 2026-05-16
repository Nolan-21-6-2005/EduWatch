from nicegui import app, ui  # Thêm app vào đây
from view.pages.detector import show_detector
from view.pages.logs import show_logs
from view.component.footer import show_footer

def show_sidebar():
    ui.add_head_html("""
    <style>
        .menu-button {
            justify-content: flex-start !important;
            text-transform: none !important;
            font-weight: 500 !important;
            border-radius: 12px !important;
            padding: 12px 16px !important;
            color: #4B5563 !important;
            width: 100% !important;
            margin-bottom: 8px !important;
        }
        .active-menu {
            background-color: #DCFCE7 !important;
            color: #15803D !important;
            font-weight: 600 !important;
        }
        .main-panels {
            background-color: transparent !important;
        }
    </style>
    """)

    # Lấy thông tin user từ storage (sử dụng .get() kèm giá trị mặc định để tránh lỗi nếu chưa đăng nhập)
    user_fullname = app.storage.user.get('fullname', 'Chưa đăng nhập')
    user_role = app.storage.user.get('role', 'User') 

    # Sidebar Container
    with ui.element("div").classes("w-72 h-screen border-r bg-white p-6 flex flex-col flex-none"):
        # Logo
        with ui.element("div").classes("bg-green-100 p-4 rounded-xl mb-10"):
            ui.label("EduWatch VNUA").classes("text-lg font-bold text-green-700")

        # Khởi tạo Panels
        content_panels = ui.tab_panels(value='giamsat').props('animated=false').classes("main-panels")

        def handle_click(name):
            content_panels.value = name
            for btn, b_name in menu_buttons:
                if b_name == name:
                    btn.classes(add='active-menu')
                else:
                    btn.classes(remove='active-menu')

        menu_buttons = []
        with ui.column().classes("w-full flex-grow gap-0"):
            b1 = ui.button("Giám sát trực tiếp", icon="videocam", on_click=lambda: handle_click('giamsat')).classes("menu-button active-menu")
            menu_buttons.append((b1, 'giamsat'))
            
            b2 = ui.button("Nhật ký vi phạm", icon="history", on_click=lambda: handle_click('nhatky')).classes("menu-button")
            menu_buttons.append((b2, 'nhatky'))
            
            b3 = ui.button("Thống kê báo cáo", icon="analytics", on_click=lambda: handle_click('thongke')).classes("menu-button")
            menu_buttons.append((b3, 'thongke'))
            
            b4 = ui.button("Yêu cầu hệ thống", icon="settings", on_click=lambda: handle_click('yeucau')).classes("menu-button")
            menu_buttons.append((b4, 'yeucau'))

        show_footer()

    # Định nghĩa nội dung Panels
    with content_panels:
        with ui.tab_panel('giamsat').classes('p-6 bg-gray-50'):
            show_detector()
        with ui.tab_panel('nhatky').classes('p-6 bg-gray-50'):
            show_logs()
        with ui.tab_panel('thongke').classes('p-6 bg-gray-50'):
            ui.label("Nội dung Thống kê")
        with ui.tab_panel('yeucau').classes('p-6 bg-gray-50'):
            ui.label("Nội dung Hệ thống")

    return content_panels
