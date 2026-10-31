import streamlit as st

st.set_page_config(layout="wide", page_title="Trạng thái thiết bị")


select_col1, select_col2 = st.columns(2, gap="medium")
with select_col1:
    building = st.selectbox(
        "Tòa nhà",
        ["Chọn tòa nhà", "Giảng đường A", "Giảng đường B", "Giảng đường Nguyễn Đăng"],
        index=0,
    )
with select_col2:
    room = st.selectbox("Phòng", ["Chọn phòng", "ND.202", "ND.206", "ND.102"], index=0)

rows = [
    ("Cam 01 - Bàn giáo viên", "rtsp://192.168.1.101/stream1", "Hoạt động", "Vừa xong", True),
    ("Cam 02 - Cuối lớp", "rtsp://192.168.1.102/stream1", "Hoạt động", "1 phút trước", True),
    ("Cam 03 - Cửa chính", "rtsp://192.168.1.103/stream1", "Hoạt động", "3 phút trước", True),
    ("Cam 04 - Cửa phụ", "rtsp://192.168.1.104/stream1", "Mất kết nối", "Mất tín hiệu", False),
]

if building == "Chọn tòa nhà" or room == "Chọn phòng":
    st.markdown(
        """
        <div class="ew-table-wrap">
            <div class="empty-state-container">Chọn phòng để xem trạng thái camera.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

body = "".join(
    f"""
    <tr>
        <td><span class="ew-primary-text">{name}</span></td>
        <td>{source}</td>
        <td><span class="ew-status {'ok' if online else 'off'}">{status}</span></td>
        <td>{last}</td>
    </tr>
    """
    for name, source, status, last, online in rows
)

st.markdown(
    f"""
    <div class="ew-table-wrap">
        <table class="ew-table">
            <thead>
                <tr>
                    <th>Tên camera</th>
                    <th>Nguồn camera</th>
                    <th>Trạng thái</th>
                    <th>Cập nhật lần cuối</th>
                </tr>
            </thead>
            <tbody>{body}</tbody>
        </table>
    </div>
    """,
    unsafe_allow_html=True,
)
