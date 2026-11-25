import re
from functools import lru_cache, wraps
from pathlib import Path


def _st_cached(func):
    """st.cache_data nạp muộn: backend FastAPI không cần (và không import) Streamlit."""
    state = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        if "fn" not in state:
            import streamlit as st

            state["fn"] = st.cache_data(func)
        return state["fn"](*args, **kwargs)

    return wrapper


@_st_cached
def load_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

@lru_cache(maxsize=None)
def getdatabase_path():
    BASE_DIR = Path(__file__).resolve().parent.parent 
    DB_PATH = BASE_DIR / "data_model" / "eduwatch.db"
    return DB_PATH

@lru_cache(maxsize=None)
def getmodel_path():
    BASE_DIR = Path(__file__).resolve().parent.parent 
    MODEL_PATH = BASE_DIR / "AI_model" / "yolo_eduwatch.pt"
    return MODEL_PATH

@_st_cached
def date_range_bounds(value):
    """Kết quả của st.date_input dạng khoảng -> (ngày bắt đầu, ngày kết thúc).

    Chưa chọn ngày nào -> (None, None), nghĩa là không lọc theo ngày.
    Mới chọn một ngày -> lọc đúng ngày đó.
    """
    if isinstance(value, (tuple, list)):
        if len(value) >= 2:
            return value[0], value[1]
        if len(value) == 1:
            return value[0], value[0]
        return None, None
    return (value, value) if value else (None, None)


def _room_number(room: str) -> str:
    """ND102 -> 102 (nếu không có số thì trả nguyên chuỗi)."""
    match = re.search(r"\d+", room)
    return match.group() if match else room

def _find_col(frame, candidates):
    return next((c for c in frame.columns if str(c).strip().lower() in candidates), None)

def _format_status(value):
    text = str(value or "").strip()
    aliases = {
        "pending": "Chờ xử lý", "waiting": "Chờ xử lý", "new": "Chờ xử lý",
        "processing": "Đang xử lý", "in_progress": "Đang xử lý",
        "resolved": "Đã xác nhận", "completed": "Đã xác nhận", "done": "Đã xác nhận",
        "rejected": "Đã hủy", "cancelled": "Đã hủy",
    }
    return aliases.get(text.lower(), text or "Chưa xác định")
