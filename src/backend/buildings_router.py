from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

import src.database_query.buildings_manager as bdm
from src.backend.building_panel_common import render_locations_panel

router = APIRouter()


@router.get("/locations", response_model=list[dict])
def locations():
    result = bdm.get_locations()
    return result


@router.get("/locations/panel", response_class=HTMLResponse)
def locations_panel():
    return render_locations_panel(viewer=False)


@router.post("/locations/buildings")
def create_building(payload: dict):
    try:
        building_id = bdm.add_building(str(payload.get("name", "")))
        return {"id": building_id}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/locations/buildings/{building_id}")
def edit_building(building_id: int, payload: dict):
    try:
        bdm.update_building(building_id, str(payload.get("name", "")))
        if "status" in payload:
            bdm.set_building_status(building_id, int(payload["status"]))
        return {"id": building_id}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/locations/buildings/{building_id}/status")
def toggle_building(building_id: int, payload: dict):
    try:
        bdm.set_building_status(building_id, int(payload.get("status", 0)))
        return {"id": building_id, "status": int(payload.get("status", 0))}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/locations/rooms")
def create_room(payload: dict):
    try:
        room_id = bdm.add_room(int(payload["building_id"]), str(payload.get("name", "")))
        bdm.update_room_monitor_mode(room_id, int(payload.get("monitor_mode", 0)))
        return {"id": room_id, "monitor_mode": int(payload.get("monitor_mode", 0))}
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/locations/rooms/{room_id}")
def edit_room(room_id: int, payload: dict):
    try:
        bdm.update_room(room_id, int(payload["building_id"]), str(payload.get("name", "")))
        if "status" in payload:
            bdm.set_room_status(room_id, int(payload["status"]))
        if "monitor_mode" in payload:
            bdm.update_room_monitor_mode(room_id, int(payload["monitor_mode"]))
        return {"id": room_id}
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/locations/rooms/{room_id}/status")
def toggle_room(room_id: int, payload: dict):
    try:
        bdm.set_room_status(room_id, int(payload.get("status", 0)))
        return {"id": room_id, "status": int(payload.get("status", 0))}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/locations/cameras")
def create_camera(payload: dict):
    try:
        camera_id = bdm.add_camera(
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
        bdm.update_camera(
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
        bdm.update_camera_status(camera_id, int(payload.get("status", 0)))
        return {"id": camera_id, "status": int(payload.get("status", 0))}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
