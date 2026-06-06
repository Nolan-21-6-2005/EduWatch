import streamlit as st

st.set_page_config(layout="wide", page_title="Quản lý người dùng")

def show_user():

    st.subheader("Quản lý người dùng")
    st.caption(
        "Theo dõi tài khoản EduWatch VNUA. Admin có thể đổi vai trò hoặc khóa tài khoản."
    )

    users = [
        {
            "id": 1,
            "name": "Bảo vệ Nguyễn Đăng",
            "phone": "0900000003",
            "username": "BV01",
            "role": "Bảo vệ",
        },
        {
            "id": 2,
            "name": "Nguyễn Văn A",
            "phone": "0900000002",
            "username": "GV123",
            "role": "Giảng viên",
        },
        {
            "id": 3,
            "name": "Admin VNUA",
            "phone": "0900000001",
            "username": "AD01",
            "role": "Admin",
        },
    ]

    # Header
    header = st.columns([0.6, 2.2, 1.8, 1.5, 1.2, 1.5, 1])

    headers = [
        "STT",
        "Họ tên",
        "SĐT",
        "Tài khoản",
        "Chi tiết",
        "Vai trò",
        "Tùy chọn",
    ]

    for col, title in zip(header, headers):
        with col:
            st.caption(f"**{title}**")

    # Rows
    for user in users:

        with st.container(border=True):

            cols = st.columns([0.6, 2.2, 1.8, 1.5, 1.2, 1.5, 1])

            cols[0].write(user["id"])
            cols[1].write(user["name"])
            cols[2].write(user["phone"])
            cols[3].write(user["username"])

            with cols[4]:
                if st.button(
                    "Chi tiết",
                    key=f"detail_{user['id']}"
                ):
                    st.session_state.selected_user = user

            with cols[5]:
                role = st.selectbox(
                    "Role",
                    ["Bảo vệ", "Giảng viên", "Admin"],
                    index=[
                        "Bảo vệ",
                        "Giảng viên",
                        "Admin",
                    ].index(user["role"]),
                    label_visibility="collapsed",
                    key=f"role_{user['id']}"
                )

            with cols[6]:

                with st.popover("⋮"):

                    st.button(
                        "Khóa tài khoản",
                        key=f"lock_{user['id']}"
                    )

                    st.button(
                        "Đặt lại mật khẩu",
                        key=f"reset_{user['id']}"
                    )

                    st.button(
                        "Xóa",
                        key=f"delete_{user['id']}"
                    )
