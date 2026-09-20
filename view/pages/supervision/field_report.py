import streamlit as st

st.set_page_config(layout="wide", page_title="Xuất biên bản ca thi")


def show_report():
    st.markdown(
        """
        <div class="page-header">
            <div>
                <h1 class="page-header-title">Xuất biên bản ca thi</h1>
                <p class="page-header-subtitle">Tạo biên bản từ thông tin ca thi và ghi chú của giám sát.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, form_center, _ = st.columns([1, 2, 1])
    with form_center:
        with st.container(border=True):
            st.text_input("Môn thi", value="Tin học đại cương")
            st.text_input("Phòng thi", value="Giảng đường Nguyễn Đăng - ND.202")
            st.text_area(
                "Ghi chú giáo viên",
                value="Danh sách vi phạm do giáo viên ghi nhận và xác nhận trong ca thi.",
                height=120,
            )
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            btn1, btn2 = st.columns(2, gap="small")
            btn1.button(":material/picture_as_pdf:  Xuất biên bản PDF", use_container_width=True, type="primary", key="ex_pdf")
            btn2.button(":material/table_view:  Xuất Excel", use_container_width=True, key="ex_excel")
