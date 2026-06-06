import streamlit as st
import datetime
import pandas as pd
from helper.script_loader import load_file

st.set_page_config(layout="wide", page_title="EduWatch VNUA Admin")

def show_report():
    # --- Cấu hình trang ---
    backdground_color = st.get_option("theme.backgroundColor")

    css = load_file("view/style/style.css")
    
    st.markdown(f"""
        <style>
            {css}
        </style>
    """, unsafe_allow_html=True)
    
    data = [
        {
            "Tòa nhà": "Giảng đường A",
            "Phòng học": "ND.202",
            "Số vi phạm phòng thường": 3,
            "Số vi phạm phòng thi": 1,
        },
        
        {
            "Tòa nhà": "Giảng đường B",
            "Phòng học": "ND.206",
            "Số vi phạm phòng thường": 1,
            "Số vi phạm phòng thi": 4,
        },
        
        {
            "Tòa nhà": "Giảng đường Nguyễn Đăng",
            "Phòng học": "ND.202",
            "Số vi phạm phòng thường": 2,
            "Số vi phạm phòng thi": 0,
        },
        
        {
            "Tòa nhà": "Tòa nhà trung tâm",
            "Phòng học": "ND.206",
            "Số vi phạm phòng thường": 0,
            "Số vi phạm phòng thi": 2,
        },
    ]

    
    # --- MAIN CONTENT (Khu vực nội dung chính phía bên phải) ---
    # Tiêu đề trang chính và cụm nút Xuất file
    title_col1, title_col2 = st.columns([3, 1])

    with title_col1:
        st.title("Thống kê báo cáo")
    with title_col2:
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            st.button(":material/picture_as_pdf: XUẤT PDF", width="content", type="primary")
        with btn_col2:
            st.button(":material/table_view: EXCEL", width="content")


    # Khu vực 2 thẻ thông báo vi phạm (Thống kê nhanh)
    st.markdown("<br>", unsafe_allow_html=True)
    m1, m2 = st.columns(2)

    df = pd.DataFrame(data)
    
    with m1:
        with st.container(border = True):
            st.metric(
                "Vi phạm phòng thường",
                df["Số vi phạm phòng thường"].sum()
            )

    with m2:
        with st.container(border = True):
            st.metric(
                "Vi phạm phòng thi",
                df["Số vi phạm phòng thi"].sum()
            )


    # Thanh Bộ lọc Tìm kiếm theo ngày
    filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 4])

    with filter_col1:
        # Set mặc định ngày 27/05/2026 như trong hình
        d = st.date_input(
            "Ngày báo cáo", datetime.date(2026, 5, 27), label_visibility="collapsed"
        )

    with filter_col2:
        st.button(":material/search: TÌM KIẾM", type="primary")


    st.dataframe(
        df,
        width="stretch",
        hide_index=True,
        column_config={
            "Tòa nhà": st.column_config.TextColumn(
                width="medium"
            ),
            "Phòng học": st.column_config.TextColumn(
                width="small"
            ),
            "Số vi phạm phòng thường": st.column_config.NumberColumn(
                format="%d"
            ),
            "Số vi phạm phòng thi": st.column_config.NumberColumn(
                format="%d"
            ),
        }
    )

    
