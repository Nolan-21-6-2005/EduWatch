import re
import streamlit as st
from pathlib import Path

def load_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def getdatabase_path():
    BASE_DIR = Path(__file__).resolve().parent.parent 
    DB_PATH = BASE_DIR / "data_model" / "eduwatch.db"
    return DB_PATH
    
def getmodel_path():
    BASE_DIR = Path(__file__).resolve().parent.parent 
    MODEL_PATH = BASE_DIR / "AI_model" / "yolo_eduwatch.pt"
    return MODEL_PATH
        
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
        "resolved": "Đã xử lý", "completed": "Đã xử lý", "done": "Đã xử lý",
        "rejected": "Từ chối",
    }
    return aliases.get(text.lower(), text or "Chưa xác định")
