import time
from nicegui import ui
from src.services.detection_service import detector

def show_detector():
    ui.add_css("style.css")
    
    # Khởi tạo biến rỗng trước để tránh lỗi UnboundLocalError khi hàm toggle gọi
    status_label = None
    status_label_sub = None
    
    # ===== 1. ĐỊNH NGHĨA LOGIC TRƯỚC =====
    def toggle_ai(e):
        if e.value:
            detector.activate()
            if status_label: status_label.set_text("Đang hoạt động")
            if status_label_sub: status_label_sub.set_text("Đang hoạt động")
            ui.notify("Đã bật nhận diện AI", type="info")
        else:
            detector.deactivate()
            if status_label: status_label.set_text("Đã tạm dừng")
            if status_label_sub: status_label_sub.set_text("Đã tạm dừng")
            ui.notify("Đã tắt nhận diện AI", type="warning")
            
    # ===== 2. XÂY DỰNG GIAO DIỆN (CHÚ Ý CÁC KHỐI WITH) =====
    with ui.row().classes("w-full h-full no-wrap gap-6"):
        
        # ===== LEFT: CAMERA AREA =====
        with ui.column().classes("w-[70%] h-full"):

            # Khối Tiêu đề
            with ui.row().classes("w-full justify-between items-end mb-6"):
                with ui.column().classes("gap-1"):
                    ui.label("Giảng đường Nguyễn Đăng - P.102").classes("text-3xl font-black text-gray-900")
                    ui.label("Phòng học đang trong ca thi số 2").classes("text-sm text-gray-400")

                ui.button("Chế độ nhiều camera", icon="grid_view").props('outline color="green"').classes("rounded-xl")

            # 🟥 Grid Camera (Chỉ chứa đúng 4 ô camera)
            with ui.grid(columns=2).classes("w-full gap-5"):

                # Ô CAMERA 01 (Luồng chạy thực tế tích hợp Tải lại tự động)
                with ui.card().classes("p-0 overflow-hidden rounded-xl relative shadow-sm w-full"):
                    camera_view = ui.image('/video_feed').classes("w-full h-auto")
                    # Định kỳ làm mới nguồn ảnh loại bỏ cache
                    ui.timer(0.03, lambda: camera_view.set_source(f'/video_feed?t={time.time()}'))

                    with ui.row().classes("absolute top-3 left-3 right-3 justify-between items-center w-[95%]"):
                        ui.label("Cam 01 - Trực tiếp").classes("bg-black/50 text-white text-xs px-2 py-1 rounded")

                # Ô CAMERA 02
                with ui.card().classes("p-0 overflow-hidden rounded-xl relative shadow-sm"):
                    ui.interactive_image('https://picsum.photos/id/237/600/400').classes("w-full h-auto")
                    with ui.row().classes("absolute top-3 left-3 justify-between w-full pr-6"):
                        ui.label("Cam 02 - Góc sau").classes("bg-black/50 text-white text-xs px-2 py-1 rounded")
            
                # Ô CAMERA 03
                with ui.card().classes("p-0 overflow-hidden rounded-xl relative shadow-sm"):
                    ui.interactive_image('https://picsum.photos/id/238/600/400').classes("w-full h-auto")
                    with ui.row().classes("absolute top-3 left-3 justify-between w-full pr-6"):
                        ui.label("Cam 03 - Dự phòng").classes("bg-black/50 text-white text-xs px-2 py-1 rounded")
                
                # Ô CAMERA 04 (Tương tự Cam 1 bằng thẻ HTML img)
                with ui.card().classes("p-0 overflow-hidden rounded-xl relative shadow-sm w-full"):
                    ui.html('<img src="/video_feed" class="w-full h-auto object-cover" />')

            # 🟩 THANH ĐIỀU KHIỂN PHÍA DƯỚI (Đã tách độc lập ra ngoài lưới Grid Camera)
            with ui.row().classes("w-full justify-between items-center bg-white p-4 rounded-xl shadow-sm mt-4"):
                
                # Nhãn hiển thị trạng thái động
                status_label = ui.label("Đang hoạt động" if detector.is_active() else "Đã tạm dừng").classes("text-sm text-gray-500")

                # Cụm công tắc và Nhãn AI Network bên phải
                with ui.row().classes("items-center gap-4"):
                    with ui.column().classes("gap-0 items-end"):
                        ui.label("TRÍ TUỆ NHÂN TẠO").classes("text-xs font-bold text-green-600")
                        status_label_sub = ui.label("Đang hoạt động" if detector.is_active() else "Đã tạm dừng").classes("text-xs text-gray-400")
                    
                    # Nút gạt Switch gọi hàm
                    ui.switch(value=detector.is_active(), on_change=toggle_ai).props("color=green")
                
        # ===== RIGHT: VIOLATION LOGS =====
        with ui.column().classes("w-[30%] h-full bg-white rounded-3xl p-5 border border-gray-100 overflow-y-auto"):
            ui.label("NHẬT KÝ VI PHẠM MỚI NHẤT").classes("text-xs font-black text-gray-400 tracking-widest mb-6")

            for _ in range(3):
                with ui.column().classes("w-full p-4 bg-gray-50 rounded-2xl mb-4 border border-gray-100"):
                    ui.label("14:30:05").classes("text-xs font-mono text-gray-400")
                    ui.label("Sử dụng tài liệu trái phép").classes("text-sm font-bold text-red-700 mb-3")
                    ui.image("https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=300").classes("rounded-xl mb-4 h-28 object-cover")

                    with ui.row().classes("w-full gap-2"):
                        ui.button("Xác nhận").props("flat dense").classes("bg-green-600 text-white flex-1 rounded-xl")
                        ui.button("Báo sai").props("flat dense").classes("bg-gray-200 text-gray-600 flex-1 rounded-xl")
