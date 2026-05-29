import streamlit as st
from streamlit_searchbox import st_searchbox
import wikipedia

logo = "view/asset/eduwatch_logo.png"

def show_header():
    def search_wikipedia(searchterm: str) -> list:
        # search wikipedia for the searchterm
        return wikipedia.search(searchterm) if searchterm else []
    st.markdown("""
    <style>
        /* Chỉnh lại khoảng đệm của vùng chứa nội dung chính */
        .block-container {
            padding-left: 1rem !important;  /* Khoảng cách lề trái */
            padding-right: 1rem !important; /* Khoảng cách lề phải */
            max-width: 100% !important;     /* Đảm bảo độ rộng tối đa 100% */
        }
        
        /* Ẩn thanh header mặc định của Streamlit */
        [data-testid="stHeader"] {
            display: none;
        }
        
        /* Giảm khoảng trống phía trên cùng */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
        }
        
        /* Nếu bạn có lỡ tay viết code st.sidebar, 
           đoạn này sẽ ẩn luôn cả vùng sidebar đó */
        [data-testid="stSidebar"] {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)    
    col1, col2, col3 = st.columns([6, 3, 1])
    with col1:
        col1, col2 = st.columns([2, 5])
        with col1:
            st.image(logo)
            # pass search function and other options as needed
        with col2:
            selected_value = st_searchbox(
            search_wikipedia,
            placeholder="Search Wikipedia... ",
            key="my_key",
        )
    with col3:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.button("", icon=":material/notifications:")
        with col2:
            st.button("", icon=":material/settings:")
    
    
