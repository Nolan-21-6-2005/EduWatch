from fastapi import APIRouter
from pydantic import BaseModel
from src.database_query.auth import signup
from sqlite3 import IntegrityError
import hashlib
import re

router = APIRouter()


class signupData(BaseModel):
    professor_id: str
    password: str
    role: int
    ho_ten: str
    ngay_sinh: str
    gioi_tinh: str
    email: str
    so_dien_thoai: str
    anh_dai_dien: str
    created_at: str
    status: int


def is_strong_password(password):
    return (
        len(password) >= 8
        and re.search(r"[A-Z]", password)
        and re.search(r"[a-z]", password)
        and re.search(r"[0-9]", password)
        and re.search(r'[!@#$%^&*(),.?":{}|<>]', password)
    )


@router.post("/signup")
def sign_up(data: signupData):
    if not is_strong_password(data.password):
        return {
            "success": False,
            "message": "Mật khẩu phải có ít nhất 8 ký tự, gồm chữ hoa, chữ thường, số và ký tự đặc biệt.",
        }

    try:
        password_hash = hashlib.sha256(data.password.encode()).hexdigest()

        signup(
            data.professor_id.strip(),
            password_hash,
            data.role,
            data.ho_ten.strip(),
            data.ngay_sinh,
            data.gioi_tinh,
            data.email.strip(),
            data.so_dien_thoai.strip(),
            data.anh_dai_dien,
            data.created_at,
            data.status,
        )

        return {
            "success": True,
            "message": "Đăng ký thành công",
        }

    except IntegrityError as e:
        error = str(e).lower()

        if "ma_giang_vien" in error:
            message = "Mã giảng viên đã tồn tại."
        elif "email" in error:
            message = "Email đã được sử dụng."
        else:
            message = "Thông tin đăng ký đã tồn tại hoặc không hợp lệ."

        return {
            "success": False,
            "message": message,
        }

    except Exception as e:
        print(f"Lỗi đăng ký: {e}")
        return {
            "success": False,
            "message": "Không thể tạo tài khoản. Vui lòng kiểm tra dữ liệu và thử lại.",
        }
