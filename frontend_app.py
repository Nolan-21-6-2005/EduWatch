import streamlit as st

from utils.helper import load_file
from view.component.footer import show_footer
from view.component.topbar import show_topbar

import view.navigation as nt
import utils.config as cfg

st.set_page_config(
    page_title="EduWatch",
    layout="wide",
    initial_sidebar_state="expanded",
)

css = "\n".join(load_file(path) for path in cfg.css_files)
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# professor_id và role là trạng thái đăng nhập duy nhất cần giữ.
# Không cần session_state["page"] nữa vì st.navigation quản lý trang.
if "professor_id" not in st.session_state:
    st.session_state["professor_id"] = ""

if "role" not in st.session_state:
    st.session_state["role"] = ""


logged_in = bool(st.session_state["professor_id"]) and st.session_state["role"] in (0, 1, 2)

if logged_in:


    # Logo được đặt ở entrypoint, trước st.navigation().
    # st.logo() sẽ tự hiển thị logo trong sidebar và dùng icon_image khi sidebar thu gọn.
    if st.session_state["role"] == 0:
        st.logo(cfg.admin_logo_path)
    if st.session_state["role"] == 1:
        st.logo(cfg.supervision_logo_path)
    if st.session_state["role"] == 2:
        st.logo(cfg.security_logo_path)
    
    # Navigation phẳng: mỗi st.Page là một mục trực tiếp trong sidebar.
    pages = nt.get_pages_for_role(st.session_state["role"])
    
    pg = st.navigation(pages, position="sidebar", expanded=True)

    show_topbar(pg.title)

    # Footer nằm dưới menu navigation.
    show_footer()
else:
    # Khi chưa đăng nhập, chỉ cho phép đi giữa Đăng nhập và Đăng ký.
    pg = st.navigation(
        [nt.SIGN_IN_PAGE, nt.SIGN_UP_PAGE],
        position="hidden",
    )
    
pg.run()
