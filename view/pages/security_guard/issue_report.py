import streamlit as st

st.set_page_config(layout="wide", page_title="Báo cáo sự cố")


def show_issue_report():
    with st.container(border=True):
        st.markdown("<h3 style='margin-top:0;'>Thông tin sự cố</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2, gap="medium")
        with col1:
            st.selectbox("Tòa nhà", ["Giảng đường A", "Giảng đường B", "Giảng đường Nguyễn Đăng"])
        with col2:
            st.selectbox("Phòng", ["ND.202", "ND.206", "ND.102"])
        st.text_input("Loại sự cố", placeholder="Ví dụ: Camera offline, Mất nguồn...")
        st.text_area("Mô tả sự cố", placeholder="Mô tả chi tiết tình trạng sự cố kỹ thuật...", height=120)
        st.button(":material/send:  Gửi báo cáo", type="primary", width="stretch")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">Lịch sử báo cáo sự cố</h2>', unsafe_allow_html=True)

    st.markdown(
        """
        <table class="history-table">
            <thead>
                <tr>
                    <th>Thời gian gửi</th>
                    <th>Loại sự cố</th>
                    <th>Nội dung / Vị trí</th>
                    <th>Trạng thái xử lý</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>2026-05-16 08:34:30</td>
                    <td><strong>Camera offline</strong></td>
                    <td>Giảng đường Nguyễn Đăng - ND.202 - Camera offline: gggg</td>
                    <td><span class="status-badge-waiting">Chờ xử lý</span></td>
                </tr>
            </tbody>
        </table>
        """,
        unsafe_allow_html=True,
    )
