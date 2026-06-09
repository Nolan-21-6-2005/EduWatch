from fastapi import FastAPI
#from src.services.camera_services import
from fastapi.middleware.cors import CORSMiddleware
from src.backend.login_router import router as login_router
from src.backend.signup_router import router as signup_router
from src.backend.camera_router import router as camera_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(login_router)
app.include_router(signup_router)
app.include_router(camera_router)

