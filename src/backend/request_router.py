"""API xác nhận / hủy báo cáo sự cố và biên bản (chỉ quản trị viên)."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.database_query import notifications as db

router = APIRouter()


class ReviewBody(BaseModel):
    admin_code: str


def _review(request_id: int, body: ReviewBody, approve: bool) -> dict:
    try:
        done = db.review_request(request_id, body.admin_code, approve)
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error))
    if not done:
        raise HTTPException(status_code=409, detail="Yêu cầu không tồn tại hoặc đã được xử lý trước đó.")
    return {"id": request_id, "status": "resolved" if approve else "rejected"}


@router.post("/requests/{request_id}/approve")
def approve_request(request_id: int, body: ReviewBody):
    """Xác nhận yêu cầu."""
    return _review(request_id, body, True)


@router.post("/requests/{request_id}/reject")
def reject_request(request_id: int, body: ReviewBody):
    """Hủy yêu cầu."""
    return _review(request_id, body, False)
