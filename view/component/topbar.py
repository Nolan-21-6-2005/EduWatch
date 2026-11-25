import streamlit as st

from view.component.notification import notification_bell, notification_panel
from view.navigation import get_pages_for_role

SEARCH_KEY = "topbar_search"
SEARCH_TARGET_KEY = "_topbar_search_target"

# Tên hiển thị trong ô tìm kiếm cho những trang có tiêu đề điều hướng khác.
SEARCH_LABELS = {"profile": "Thông tin cá nhân"}


def _search_options(pages=None) -> dict:
    """Nhãn -> trang, lấy từ chính danh sách trang của role đang đăng nhập.

    Dùng đúng đối tượng st.Page của st.navigation nên không còn danh sách đường dẫn riêng
    (trước đây phải khớp tay với navigation.py cho từng role).
    """
    if pages is None:
        pages = get_pages_for_role(st.session_state.get("role"))
    options = {}
    for page in pages:
        label = SEARCH_LABELS.get(page.url_path, page.title)
        if label:
            options.setdefault(label, page)
    return options


def _on_search_select():
    """Callback của ô tìm kiếm: ghi nhớ trang được chọn rồi xóa ô để lần sau chọn lại được."""
    st.session_state[SEARCH_TARGET_KEY] = st.session_state.get(SEARCH_KEY)
    st.session_state[SEARCH_KEY] = None


def show_topbar(page_title="Trang chủ", pages=None):
    options = _search_options(pages)

    st.markdown(
        '<div class="ew-topbar-spacer"></div>',
        unsafe_allow_html=True,
    )

    with st.container(
        key="ew_topbar",
        horizontal=True,
        vertical_alignment="center",
    ):
        st.markdown(
            f"""
            <div class="ew-breadcrumb">
                <span class="ew-breadcrumb-home">EduWatch</span>
                <span class="ew-breadcrumb-separator">/</span>
                <span class="ew-breadcrumb-current">{page_title}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Ô tìm kiếm gốc của Streamlit (gõ để lọc, chọn để chuyển trang). Không dùng iframe nên
        # danh sách gợi ý luôn nằm trên cùng và nhận được click ở mọi role/trang.
        st.selectbox(
            "Tìm kiếm trang",
            list(options),
            index=None,
            placeholder="Tìm kiếm trang",
            key=SEARCH_KEY,
            label_visibility="collapsed",
            on_change=_on_search_select,
        )

        # Chuyển trang sau khi callback đã ghi nhận lựa chọn.
        target = st.session_state.pop(SEARCH_TARGET_KEY, None)
        if target in options:
            st.switch_page(options[target])

        st.html('<span class="ew-status ok">System Online</span>')

        notification_bell()    
            
        st.button(
            ":material/settings:",
            key="topbar_settings",
            help="Cài đặt",
        )
        
    notification_panel() 
