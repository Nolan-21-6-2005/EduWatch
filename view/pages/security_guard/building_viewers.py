from utils.config import API_BASE
from view.pages.location_page_common import render_location_page

render_location_page(
    title="Danh sách tòa nhà",
    page_title="Danh sách tòa nhà",
    panel_url=f"{API_BASE}/locations/panel_viewer",
)
