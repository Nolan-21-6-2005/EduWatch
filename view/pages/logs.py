import time
from nicegui import ui
# Import các hàm tương tác cơ sở dữ liệu SQLite
from src.database.db_manager import get_all_logs, update_log_status

def show_logs():
    ui.add_css("style.css")
    
    # Biến trạng thái lưu bản ghi đang được giám thị click chọn
    selected_log_id = None

    # Khối bao quát toàn trang
    with ui.column().classes("w-full h-full p-6 gap-6 bg-slate-50"):
        
        # ===== ROW 1: HEADER TRANG =====
        with ui.row().classes("w-full justify-between items-center bg-white p-4 rounded-2xl shadow-sm"):
            with ui.column().classes("gap-1"):
                ui.label("TRUNG TÂM DỮ LIỆU VI PHẠM CA THI").classes("text-2xl font-black text-gray-900")
                ui.label("Hệ thống lưu trữ và phê duyệt bằng chứng nhận diện từ AI").classes("text-sm text-gray-400")
            
            # Bộ đếm tổng số log hiện có trong SQLite
            badge_total = ui.badge("0 mục ghi nhận", color="blue").classes("px-4 py-2 text-sm rounded-xl font-bold")

        # ===== ROW 2: KHU VỰC QUẢN LÝ CHÍNH (CHIA LÀM 2 CỘT) =====
        with ui.row().classes("w-full h-[calc(100vh-180px)] no-wrap gap-6 items-start"):
            
            # --- CỘT TRÁI (65%): BẢNG CƠ SỞ DỮ LIỆU ĐỘNG (AG GRID) ---
            with ui.column().classes("w-[65%] h-full bg-white rounded-3xl p-5 shadow-sm border border-gray-100"):
                
                # Thanh công cụ: Tìm kiếm và Lọc dữ liệu nhanh giống Obsidian Base
                with ui.row().classes("w-full mb-4 gap-3 items-center"):
                    ui.icon("search").classes("text-gray-400 text-xl")
                    search_input = ui.input(placeholder="Tìm kiếm theo hành vi, mã phòng, trạng thái...").props("dense outlined").classes("flex-1 rounded-xl")
                    
                    # Các nút lọc nhanh mẫu
                    ui.button("Tất cả", color="gray").props("flat dense")
                    ui.button("⏳ Chờ duyệt", color="orange").props("flat dense")
                    ui.button("✅ Đã xác nhận", color="green").props("flat dense")

                # Cấu hình các cột hiển thị trong bảng dữ liệu
                column_defs = [
                    {'headerName': 'ID', 'field': 'id', 'width': 70, 'sortable': True, 'checkboxSelection': True},
                    {'headerName': 'Thời gian', 'field': 'time', 'width': 110, 'sortable': True},
                    {'headerName': 'Hành vi vi phạm', 'field': 'type', 'width': 180, 'filter': True},
                    {'headerName': 'Độ tin cậy AI', 'field': 'confidence', 'width': 120, 'sortable': True},
                    {'headerName': 'Trạng thái xử lý', 'field': 'status', 'width': 140, 'filter': True}
                ]

                # Đọc dữ liệu từ SQLite nạp vào Grid ban đầu
                initial_data = get_all_logs()
                badge_total.set_text(f"{len(initial_data)} mục ghi nhận")

                # Khởi tạo bảng lưới AG Grid kích thước lớn rộng rãi
                grid = ui.aggrid({
                    'columnDefs': column_defs,
                    'rowData': initial_data,
                    'rowSelection': 'single',
                    'pagination': True,          # Bật tính năng phân trang nếu dữ liệu quá nhiều
                    'paginationPageSize': 10     # Mỗi trang hiển thị tối đa 10 dòng
                }).classes("w-full h-[calc(100%-60px)] text-sm")

            # --- CỘT PHẢI (35%): PROPERTIES PANEL (CHI TIẾT BẢN GHI) ---
            with ui.column().classes("w-[35%] h-full bg-white rounded-3xl p-6 shadow-sm border border-gray-100 flex flex-col justify-between"):
                
                with ui.column().classes("w-full gap-4"):
                    ui.label("THUỘC TÍNH BẢN GHI (PROPERTIES)").classes("text-xs font-black text-gray-400 tracking-widest mb-2")
                    
                    # Khung hiển thị ảnh bằng chứng vi phạm khổ lớn cực rõ nét
                    with ui.card().classes("w-full p-0 overflow-hidden rounded-2xl border shadow-inner bg-black/5 flex justify-center items-center h-48"):
                        evidence_img = ui.image("https://placehold.co/600x400?text=Chua+Chon+Bao+Cao").classes("w-full h-full object-contain")

                    ui.separator()

                    # Danh sách các thuộc tính (Properties Fields) mô phỏng Obsidian
                    with ui.row().classes("w-full justify-between items-center py-1"):
                        with ui.row().classes("items-center gap-2 text-gray-400 text-sm"):
                            ui.icon("gavel")
                            ui.label("Loại hành vi:")
                        detail_type = ui.label("---").classes("font-black text-red-600 text-sm")

                    with ui.row().classes("w-full justify-between items-center py-1"):
                        with ui.row().classes("items-center gap-2 text-gray-400 text-sm"):
                            ui.icon("analytics")
                            ui.label("Độ chính xác AI:")
                        detail_conf = ui.label("---").classes("font-bold text-gray-700 text-sm")
                        
                    with ui.row().classes("w-full justify-between items-center py-1"):
                        with ui.row().classes("items-center gap-2 text-gray-400 text-sm"):
                            ui.icon("schedule")
                            ui.label("Mốc thời gian:")
                        detail_time = ui.label("---").classes("font-mono text-gray-600 text-sm")

                # Cụm nút chức năng duyệt trạng thái cố định ở đáy cột phải
                with ui.column().classes("w-full gap-2 mt-4"):
                    
                    def change_status(status_text):
                        nonlocal selected_log_id
                        if selected_log_id:
                            # 1. Cập nhật trạng thái mới vào file SQLite
                            update_log_status(selected_log_id, status_text)
                            ui.notify(f"Đã cập nhật bản ghi #{selected_log_id} thành {status_text}", type="success")
                            
                            # 2. Truy vấn lại SQLite và reload bảng trên giao diện
                            updated_data = get_all_logs()
                            grid.options['rowData'] = updated_data
                            grid.update()
                            badge_total.set_text(f"{len(updated_data)} mục ghi nhận")

                    with ui.row().classes("w-full gap-3"):
                        ui.button("Xác nhận vi phạm", icon="check_circle", on_click=lambda: change_status("✅ Xác nhận")).props("flat").classes("bg-green-600 text-white flex-1 rounded-xl font-bold py-2 shadow-sm text-sm")
                        ui.button("Báo sai / Bỏ qua", icon="cancel", on_click=lambda: change_status("❌ Báo sai")).props("flat").classes("bg-gray-100 text-gray-600 flex-1 rounded-xl font-medium py-2 text-sm")

            # --- SỰ KIỆN TƯƠNG TÁC GIỮA BẢNG VÀ KHUNG CHI TIẾT ---
            def on_row_select(e):
                nonlocal selected_log_id
                if e.args.get('selected'):
                    data = e.args.get('data')
                    selected_log_id = data['id']
                    
                    # Đẩy thông tin từ dòng được chọn sang panel thuộc tính bên phải
                    detail_type.set_text(data['type'])
                    detail_conf.set_text(data['confidence'])
                    detail_time.set_text(data['time'])
                    
                    # Kiểm tra và render đường dẫn ảnh bằng chứng thực tế
                    if data.get('evidence_path'):
                        evidence_img.set_source(data['evidence_path'])
                    else:
                        evidence_img.set_source("https://placehold.co/600x400?text=Khong+Co+Anh+Bieu+Mau")
            
            # Gắn sự kiện click dòng cho bảng lưới
            grid.on('rowSelected', on_row_select)

            # Cơ chế đồng bộ: Cứ mỗi 5 giây, quét SQLite tự động tải thêm dữ liệu nếu camera bên kia vừa bắn lỗi về
            def auto_refresh():
                current_logs = get_all_logs()
                grid.options['rowData'] = current_logs
                grid.update()
                badge_total.set_text(f"{len(current_logs)} mục ghi nhận")
                
            ui.timer(5.0, auto_refresh)
