from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from src.database_query.buildings_manager import (
    add_building,
    add_camera,
    add_room,
    update_room_monitor_mode,
    get_locations,
    set_building_status,
    set_room_status,
    update_building,
    update_camera,
    update_camera_status,
    update_room,
)

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parents[2]
ASSET_DIR = BASE_DIR / "view" / "asset"
STYLE_DIR = BASE_DIR / "view" / "style"


def _locations_payload() -> list[dict]:
    return get_locations()


@router.get("/locations", response_model=list[dict])
def locations():
    return _locations_payload()


@router.get("/locations/panel", response_class=HTMLResponse)
def locations_panel():
    template = (ASSET_DIR / "buildings.html").read_text(encoding="utf-8")
    script = (ASSET_DIR / "buildings.js").read_text(encoding="utf-8")
    css = (STYLE_DIR / "buildings.css").read_text(encoding="utf-8")
    data = json.dumps(_locations_payload(), ensure_ascii=False).replace("</", "<\\/")
    page = (
        template
        .replace("__BUILDINGS_CSS__", css)
        .replace("__BUILDINGS_DATA__", data)
        .replace("__API_BASE__", "")
        .replace("__BUILDINGS_JS__", script)
    )
    return HTMLResponse(page)


@router.post("/locations/buildings")
def create_building(payload: dict):
    try:
        building_id = add_building(str(payload.get("name", "")))
        return {"id": building_id}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/locations/buildings/{building_id}")
def edit_building(building_id: int, payload: dict):
    try:
        update_building(building_id, str(payload.get("name", "")))
        if "status" in payload:
            set_building_status(building_id, int(payload["status"]))
        return {"id": building_id}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/locations/buildings/{building_id}/status")
def toggle_building(building_id: int, payload: dict):
    try:
        set_building_status(building_id, int(payload.get("status", 0)))
        return {"id": building_id, "status": int(payload.get("status", 0))}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/locations/rooms")
def create_room(payload: dict):
    try:
        room_id = add_room(int(payload["building_id"]), str(payload.get("name", "")))
        update_room_monitor_mode(room_id, int(payload.get("monitor_mode", 0)))
        return {"id": room_id, "monitor_mode": int(payload.get("monitor_mode", 0))}
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/locations/rooms/{room_id}")
def edit_room(room_id: int, payload: dict):
    try:
        update_room(room_id, int(payload["building_id"]), str(payload.get("name", "")))
        if "status" in payload:
            set_room_status(room_id, int(payload["status"]))
        if "monitor_mode" in payload:
            update_room_monitor_mode(room_id, int(payload["monitor_mode"]))
        return {"id": room_id}
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/locations/rooms/{room_id}/status")
def toggle_room(room_id: int, payload: dict):
    try:
        set_room_status(room_id, int(payload.get("status", 0)))
        return {"id": room_id, "status": int(payload.get("status", 0))}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/locations/cameras")
def create_camera(payload: dict):
    try:
        camera_id = add_camera(
            int(payload["room_id"]),
            str(payload.get("position", "")),
            str(payload.get("video_source", "")),
            int(payload.get("status", 1)),
        )
        return {"id": camera_id}
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/locations/cameras/{camera_id}")
def edit_camera(camera_id: int, payload: dict):
    try:
        update_camera(
            camera_id,
            int(payload["room_id"]),
            str(payload.get("position", "")),
            str(payload.get("video_source", "")),
            int(payload.get("status", 1)),
        )
        return {"id": camera_id}
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/locations/cameras/{camera_id}/status")
def toggle_camera(camera_id: int, payload: dict):
    try:
        update_camera_status(camera_id, int(payload.get("status", 0)))
        return {"id": camera_id, "status": int(payload.get("status", 0))}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
