import streamlit as st

st.set_page_config(layout="wide", page_title="Quản lý tòa nhà")


st.markdown(
    """
    <div class="page-header">
        <div>
            <h1 class="page-header-title">Danh sách tòa nhà</h1>
            <p class="page-header-subtitle">Quản lý tòa nhà, phòng học và các góc camera từ dữ liệu SQLite của EduWatch.</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.iframe("http://localhost:8000/locations/panel", height=760)
