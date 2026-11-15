from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.backend.login_router import router as login_router
from src.backend.admin_router import router as admin_router
from src.backend.signup_router import router as signup_router
from src.backend.camera_router import router as camera_router
from src.backend.violation_router import router as violation_router
from src.backend.request_router import router as request_router
from src.backend.buildings_router import router as buildings_router
from src.backend.building_viewers_router import router as building_viewers_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "null",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(login_router)
app.include_router(admin_router)
app.include_router(signup_router)
app.include_router(camera_router)
app.include_router(violation_router)
app.include_router(request_router)

# Ảnh bằng chứng được phục vụ qua URL để bảng nhật ký không phải nhúng base64
# (data URL của st.iframe bị trình duyệt chặn khi vượt khoảng 2 MB).
EVIDENCE_DIR = Path(__file__).resolve().parent / "data_model" / "evidence"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/evidence", StaticFiles(directory=EVIDENCE_DIR), name="evidence")
app.include_router(buildings_router)
app.include_router(building_viewers_router)

