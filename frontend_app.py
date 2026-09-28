import streamlit as st

from helper.script_loader import load_file
from view.component.footer import show_footer
from view.component.topbar import show_topbar
from view.navigation import SIGN_IN_PAGE, SIGN_UP_PAGE, get_pages_for_role


st.set_page_config(
    page_title="EduWatch",
    layout="wide",
    initial_sidebar_state="expanded",
)

css_files = [
    "view/style/global.css",
    "view/style/auth.css",
    "view/style/camera_stream.css",
    "view/style/security.css",
    "view/style/admin_stream.css",
    "view/style/layout.css",
    "view/style/responsive.css",
    "view/style/topbar.css",
    "view/style/detector.css",
]
css = "\n".join(load_file(path) for path in css_files)
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# professor_id và role là trạng thái đăng nhập duy nhất cần giữ.
# Không cần session_state["page"] nữa vì st.navigation quản lý trang.
if "professor_id" not in st.session_state:
    st.session_state["professor_id"] = ""

if "role" not in st.session_state:
    st.session_state["role"] = ""


logged_in = bool(st.session_state["professor_id"]) and st.session_state["role"] in (0, 1, 2)

if logged_in:

    show_topbar()

    # Logo được đặt ở entrypoint, trước st.navigation().
    # st.logo() sẽ tự hiển thị logo trong sidebar và dùng icon_image khi sidebar thu gọn.
    logo_path = "view/asset/eduwatch_logo.png"
    icon_path = "view/asset/eduwatch_icon.png"
    st.logo(logo_path, size="large", icon_image=icon_path)

    # Navigation phẳng: mỗi st.Page là một mục trực tiếp trong sidebar.
    pages = get_pages_for_role(st.session_state["role"])
    pg = st.navigation(pages, position="sidebar", expanded=True)

    # Footer nằm dưới menu navigation.
    show_footer()
else:
    # Khi chưa đăng nhập, chỉ cho phép đi giữa Đăng nhập và Đăng ký.
    pg = st.navigation(
        [SIGN_IN_PAGE, SIGN_UP_PAGE],
        position="hidden",
    )
pg.run()
