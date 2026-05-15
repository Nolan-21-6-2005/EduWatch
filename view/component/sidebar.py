import nicegui as ui
from view.pages.detector import show_detector

def show_sidebar():
    with ui.row().classes('w-full no-wrap'):
        # Cột bên trái: Thanh Tab dọc
        with ui.tabs().props('vertical').classes('w-1/4') as tabs:
            detector = ui.tab('Giám sát trực tiếp', icon='videocam')
            logs_tab = ui.tab('Nhật ký vi phạm', icon='history')
            report_tab = ui.tab('Nhật ký vi phạm', icon='report')
            settings_tab = ui.tab('Cài đặt', icon='settings')

        # Cột bên phải: Nội dung tương ứng
        with ui.tab_panels(tabs, value=camera_tab).classes('w-3/4'):
            with ui.tab_panel(camera_tab):
                show_detector()
            
            with ui.tab_panel(history_tab):
                ui.label('Danh sách Alert từ AlertManager').classes('text-h4')
            
            with ui.tab_panel(settings_tab):
                ui.label('Cấu hình hệ thống').classes('text-h4')
