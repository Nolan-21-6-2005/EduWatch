from __future__ import annotations

from src.database_query.profile import (
    get_user_by_code,
    get_user_by_id,
    phone_exists,
    update_password,
    update_profile_contact,
    verify_password,
)
from src.services.avatar_services import (
    file_to_data_uri,
    resolve_avatar_path,
    save_avatar,
)


def role_name(role: int | None) -> str:
    return {
        0: "Quản trị viên",
        1: "Giám sát",
        2: "An ninh",
    }.get(role, "Người dùng")



__all__ = [
    "file_to_data_uri",
    "get_user_by_code",
    "get_user_by_id",
    "phone_exists",
    "resolve_avatar_path",
    "role_name",
    "save_avatar",
    "update_password",
    "update_profile_contact",
    "verify_password",
]
