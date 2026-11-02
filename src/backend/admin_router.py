from fastapi import APIRouter, HTTPException

from src.database_query.admin import (
    get_users,
    reset_user_password,
    update_user_role,
    update_user_status,
)
from src.services.avatar_services import file_to_data_uri, resolve_avatar_path

router = APIRouter()


@router.get("/admin/users", response_model=list[dict])
def list_admin_users():
    result = []
    for user in get_users():
        result.append(
            {
                "id": user["id"],
                "name": user["ho_ten"],
                "phone": user["so_dien_thoai"] or "",
                "username": user["ma_giang_vien"],
                "role": int(user["role"] if user["role"] is not None else -1),
                "status": int(user["status"] or 0),
                "avatar": file_to_data_uri(resolve_avatar_path(user.get("anh_dai_dien"))),
            }
        )
    return result


@router.put("/admin/users/{user_id}/role")
def change_user_role(user_id: int, payload: dict):
    try:
        update_user_role(user_id, int(payload["role"]))
        return {"success": True, "id": user_id}
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/admin/users/{user_id}/status")
def change_user_status(user_id: int, payload: dict):
    try:
        status = int(payload["status"])
        if status not in {0, 1}:
            raise ValueError("Trạng thái tài khoản chỉ nhận 0 hoặc 1.")
        update_user_status(user_id, status)
        return {"success": True, "id": user_id, "status": status}
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/admin/users/{user_id}/password")
def change_user_password(user_id: int, payload: dict):
    try:
        reset_user_password(user_id, str(payload["password"]))
        return {"success": True, "id": user_id}
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
