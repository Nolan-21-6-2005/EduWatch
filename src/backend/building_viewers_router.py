from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from src.backend.building_panel_common import render_locations_panel

router = APIRouter()


@router.get("/locations/panel_viewer", response_class=HTMLResponse)
def locations_panel_viewer():
    return render_locations_panel(viewer=True)
