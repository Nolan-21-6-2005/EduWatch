from __future__ import annotations

import base64
import re
import uuid
from pathlib import Path

from utils.config import AVATAR_DIR, DATA_DIR


def resolve_avatar_path(relative_path: str | None) -> Path:
    """Resolve a stored avatar path, with the project's default avatar as fallback."""
    candidates: list[Path] = []

    if relative_path:
        cleaned = relative_path.replace("\\", "/")
        if cleaned.startswith(("data_model/", "data/")):
            candidates.append(DATA_DIR.parent / cleaned)
        else:
            candidates.append(Path(cleaned))
            candidates.append(DATA_DIR / "avatar" / Path(cleaned).name)

    candidates.extend(
        [
            DATA_DIR / "avatar" / "default.jpg",
            DATA_DIR / "avatar" / "default.png",
        ]
    )

    for path in candidates:
        if path.exists() and path.is_file():
            return path

    return candidates[-1]


def file_to_data_uri(path: Path | None) -> str:
    if path is None or not path.exists():
        return ""

    mime = {
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }.get(path.suffix.lower(), "image/jpeg")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def save_avatar(uploaded_file, user_code: str) -> str:
    suffix = Path(uploaded_file.name).suffix.lower() or ".png"
    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise ValueError("Ảnh đại diện chỉ hỗ trợ JPG, JPEG, PNG hoặc WEBP.")

    AVATAR_DIR.mkdir(parents=True, exist_ok=True)
    safe_code = re.sub(r"[^A-Za-z0-9_-]+", "_", user_code).strip("_") or "user"
    file_name = f"avatar_{safe_code}_{uuid.uuid4().hex[:10]}{suffix}"
    path = AVATAR_DIR / file_name
    path.write_bytes(uploaded_file.getbuffer())
    return f"data_model/avatar/{file_name}"
