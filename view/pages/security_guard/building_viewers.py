from view.pages.location_page_common import render_location_page

render_location_page(
    title="Danh sách tòa nhà",
    subtitle="Chọn tòa nhà, phòng học và góc camera để xem dữ liệu từ SQLite của EduWatch.",
    page_title="Danh sách tòa nhà",
    panel_url="http://localhost:8000/locations/panel_viewer",
)
