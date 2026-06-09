import streamlit as st
import traceback
import requests


def request_signup(professor_id, role, password, 
                   ho_ten, ngay_sinh, gioi_tinh, 
                   email, so_dien_thoai, anh_dai_dien, 
                   created_at, status):

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
                "status": status
            }
        )
        
        data = response.json()

        st.write("Status:", response.status_code)
        st.write("Text:", response.text)

        st.write("JSON:", data)
        
        if data["success"]:
            st.session_state["page"] = "login"
            st.rerun()
        else:
            st.error("Lỗi")
    except Exception as e:
        st.code(traceback.format_exc())
