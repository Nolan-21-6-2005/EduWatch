import streamlit as st

option = st.selectbox(
    "Lọc theo tòa nhà", (
        "Giảng đường Cơ điện cũ", 
        "Giảng đường Cơ điện mới", 
        "Giảng đường Giảng đường A",
        "Giảng đường Giảng đường B",
        "Giảng đường Giảng đường C",
        "Giảng đường Nguyễn Đăng",
        "Giảng đường Giảng đường E"
    ),
)

building_map = {
    "Giảng đường Cơ điện cũ": 1,
    "Giảng đường Cơ điện mới": 2,
    "Giảng đường Giảng đường A": 3,
    "Giảng đường Giảng đường B": 4,
    "Giảng đường Giảng đường C": 5,
    "Giảng đường Nguyễn Đăng": 6,
    "Giảng đường Giảng đường E": 7
}