import streamlit as st
import requests


def request_signup(
    professor_id,
    role,
    password,
    ho_ten,
    ngay_sinh,
    gioi_tinh,
    email,
    so_dien_thoai,
    anh_dai_dien,
    created_at,
    status,
):
    try:
        response = requests.post(
            "http://localhost:8000/signup",
            json={
                "professor_id": professor_id,
                "password": password,
                "role": role,
                "ho_ten": ho_ten,
                "ngay_sinh": str(ngay_sinh),
                "gioi_tinh": gioi_tinh,
                "email": email,
                "so_dien_thoai": so_dien_thoai,
                "anh_dai_dien": anh_dai_dien,
                "created_at": created_at,
                "status": status,
            },
            timeout=10,
        )

        response.raise_for_status()
        data = response.json()

        if data.get("success"):
            st.success(data.get("message", "Đăng ký thành công."))
            st.switch_page("view/pages/auth/sign_in.py")
            return True

        st.error(data.get("message", "Đăng ký không thành công."))
        return False

    except requests.RequestException as e:
        st.error(f"Không thể kết nối đến máy chủ: {e}")
        return False

    except ValueError:
        st.error("Phản hồi từ máy chủ không đúng định dạng.")
        return False
