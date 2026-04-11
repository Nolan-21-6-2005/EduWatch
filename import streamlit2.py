import streamlit as st
import cv2
import tempfile
from ultralytics import YOLO
from datetime import datetime
import pandas as pd
import os
import hashlib
import time

# ================== CONFIG ==================
st.set_page_config(page_title="AI Security Manager Pro", layout="wide")

USER_FILE = "users.csv"

# ================== INIT FILE ==================
if not os.path.exists(USER_FILE):
    df = pd.DataFrame(columns=[
        "fullname", "gender", "dob", "phone",
        "email", "username", "password"
    ])
    df.to_csv(USER_FILE, index=False)

# ================== HASH ==================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ================== REGISTER ==================
def register_user(fullname, gender, dob, phone, email, username, password):
    df = pd.read_csv(USER_FILE)

    if email in df["email"].values:
        return False, "Email đã tồn tại!"

    if username in df["username"].values:
        return False, "Username đã tồn tại!"

    if len(password) < 6:
        return False, "Mật khẩu phải >= 6 ký tự!"

    new_user = pd.DataFrame({
        "fullname": [fullname],
        "gender": [gender],
        "dob": [str(dob)],
        "phone": [phone],
        "email": [email],
        "username": [username],
        "password": [hash_password(password)]
    })

    df = pd.concat([df, new_user], ignore_index=True)
    df.to_csv(USER_FILE, index=False)

    return True, "Đăng ký thành công!"

# ================== LOGIN ==================
def login(user_input, password):
    df = pd.read_csv(USER_FILE)
    hashed = hash_password(password)

    user = df[
        ((df["email"] == user_input) | (df["username"] == user_input)) &
        (df["password"] == hashed)
    ]

    return not user.empty

# ================== SESSION ==================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = ""

if "violation_logs" not in st.session_state:
    st.session_state.violation_logs = []

# ================== LOGIN PAGE ==================
if not st.session_state.logged_in:

    st.title("🔐 AI Security System")

    menu = st.radio("Chọn chức năng", ["Đăng nhập", "Đăng ký"])

    # ===== ĐĂNG KÝ =====
    if menu == "Đăng ký":
        fullname = st.text_input("Họ và tên")
        gender = st.selectbox("Giới tính", ["Nam", "Nữ", "Khác"])
        dob = st.date_input("Ngày sinh")
        phone = st.text_input("Số điện thoại")
        email = st.text_input("Email")
        username = st.text_input("Tên người dùng")
        password = st.text_input("Mật khẩu", type="password")

        if st.button("Đăng ký"):
            success, msg = register_user(
                fullname, gender, dob, phone, email, username, password
            )
            if success:
                st.success(msg)
            else:
                st.error(msg)

    # ===== ĐĂNG NHẬP =====
    else:
        user_input = st.text_input("Email hoặc Username")
        password = st.text_input("Mật khẩu", type="password")

        if st.button("Đăng nhập"):
            if login(user_input, password):
                st.session_state.logged_in = True
                st.session_state.user = user_input
                st.success("Đăng nhập thành công!")
                st.rerun()
            else:
                st.error("Sai thông tin!")

    st.stop()

# ================== LOAD MODEL ==================
model = YOLO("ybest.pt")

# ================== SIDEBAR ==================
with st.sidebar:
    st.success(f"👋 Xin chào {st.session_state.user}")

    page = st.radio("Menu", ["Giám sát", "Quản lý user"])

    if st.button("Đăng xuất"):
        st.session_state.logged_in = False
        st.rerun()

# ================== PAGE: QUẢN LÝ USER ==================
if page == "Quản lý user":
    st.title("📋 Quản lý người dùng")

    df = pd.read_csv(USER_FILE)

    # Ẩn password
    st.dataframe(df.drop(columns=["password"]))

    # --- Tìm kiếm ---
    search = st.text_input("🔍 Tìm username")
    if search:
        result = df[df["username"].str.contains(search)]
        st.dataframe(result.drop(columns=["password"]))

    # --- Xóa ---
    delete_user = st.text_input("Username cần xóa")
    if st.button("Xóa user"):
        df = df[df["username"] != delete_user]
        df.to_csv(USER_FILE, index=False)
        st.success("Đã xóa!")

    # --- Cập nhật ---
    edit_user = st.text_input("Username cần sửa")
    new_phone = st.text_input("SĐT mới")

    if st.button("Cập nhật"):
        df.loc[df["username"] == edit_user, "phone"] = new_phone
        df.to_csv(USER_FILE, index=False)
        st.success("Đã cập nhật!")

# ================== PAGE: GIÁM SÁT ==================
elif page == "Giám sát":

    with st.sidebar:
        mode = st.radio("Chế độ", ["Giảng đường", "Phòng thi"])
        selected_cam = st.selectbox(
            "Camera",
            ["Phòng 101", "Phòng 102", "Phòng 103", "Phòng 104"]
        )
        uploaded_video = st.file_uploader("Upload video", type=['mp4', 'avi'])
        run_btn = st.button("Bắt đầu")

    col1, col2 = st.columns([7, 3])

    with col1:
        st.subheader(f"🎥 Camera: {selected_cam}")
        frame_placeholder = st.empty()

    with col2:
        st.subheader("🚨 Nhật ký vi phạm")
        log_placeholder = st.empty()

    if run_btn and uploaded_video is not None:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_video.read())

        cap = cv2.VideoCapture(tfile.name)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            results = model(frame, conf=0.5)

            annotated = results[0].plot()
            display = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)

            frame_placeholder.image(display, channels="RGB")

            for box in results[0].boxes:
                class_id = int(box.cls[0])
                label = model.names[class_id]

                if (mode == "Phòng thi" and label == "cell phone") or \
                   (mode == "Giảng đường" and label == "person"):

                    log = {
                        "Giờ": datetime.now().strftime("%H:%M:%S"),
                        "Camera": selected_cam,
                        "Vi phạm": label
                    }

                    st.session_state.violation_logs.insert(0, log)

                    df_logs = pd.DataFrame(st.session_state.violation_logs).head(10)
                    log_placeholder.table(df_logs)

            time.sleep(0.03)

        cap.release()
        st.success("✅ Xử lý xong video!")