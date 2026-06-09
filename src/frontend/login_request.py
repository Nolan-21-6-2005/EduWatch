import streamlit as st
import traceback
import requests

def request_login(professor_id, password):
    try:
        response = requests.post(
            "http://localhost:8000/login", 
            json={
                "professor_id": professor_id, 
                "password": password
            }
        )

        data = response.json()
        if data["success"]:
            st.session_state["professor_id"] = data["professor_id"]
            st.session_state["page"] = "dashboard"
            st.session_state["role"] = data["role"]
            st.rerun()
        else:
            st.error("Sai thông tin đăng nhập")
    except Exception as e:
        st.code(traceback.format_exc())