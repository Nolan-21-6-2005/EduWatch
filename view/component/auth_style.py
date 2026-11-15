"""
CSS dùng chung cho trang đăng nhập / đăng ký.

Lưu ý: st.html lọc HTML bằng DOMPurify và sẽ XÓA CẢ KHỐI <style> nếu bên trong có ký tự "<"
(kể cả trong chú thích CSS). Vì vậy không ghi thẻ HTML trong CSS.

Streamlit bản mới không còn dùng data-baseweb="input" cho ô nhập (ô nhập giờ là
data-testid="stTextInputRootElement"), nên mọi selector ở đây bám theo data-testid.
"""

import base64
from pathlib import Path
from functools import lru_cache

BASE_DIR = Path(__file__).resolve().parents[2]
LOGIN_COVER = BASE_DIR / "view" / "asset" / "login_cover.jpg"

# Font hệ thống
FONT_FAMILY = '"Be Vietnam Pro", "Segoe UI", system-ui, sans-serif'
FONT_IMPORT = (
    "@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro"
    ":wght@400;500;600;700;800&display=swap');"
)


@lru_cache(maxsize=1)
def cover_image_data_uri() -> str:
    """Ảnh bìa trang đăng nhập dưới dạng data URI (đọc một lần, dùng lại cho mọi lần rerun)."""
    encoded = base64.b64encode(LOGIN_COVER.read_bytes()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def base_css() -> str:
    """Ẩn giao diện mặc định của Streamlit, đặt nền và font cho trang auth."""
    return f"""
    {FONT_IMPORT}

    header[data-testid="stHeader"],
    [data-testid="stSidebar"],
    [data-testid="stSidebarCollapsedControl"] {{
        display: none !important;
    }}

    .stApp {{
        background: #f7f9f8 !important;
    }}

    .stApp *:not([data-testid="stIconMaterial"]):not(.ew-icon) {{
        font-family: {FONT_FAMILY};
    }}

    /* Icon Material của Streamlit giữ nguyên font riêng */
    [data-testid="stIconMaterial"] {{
        font-family: "Material Symbols Rounded" !important;
    }}

    /* Icon Material dùng trong HTML tự viết: thẻ span có class ew-icon, nội dung là tên icon */
    .ew-icon {{
        font-family: "Material Symbols Rounded" !important;
        font-weight: 400;
        font-style: normal;
        line-height: 1;
        letter-spacing: normal;
        text-transform: none;
        white-space: nowrap;
        font-feature-settings: "liga";
        -webkit-font-feature-settings: "liga";
        font-variation-settings: "FILL" 0, "wght" 500;
        user-select: none;
    }}
    """


def field_css(
    scope: str,
    *,
    height: int = 56,
    font_size: int = 17,
    label_size: int = 15,
    radius: int = 14,
    button_height: int = 60,
    button_font: int = 19,
    icon_size: int = 24,
) -> str:
    """
    Style cho ô nhập, ô ngày, ô chọn, checkbox và nút bên trong container `scope`
    (vd: ".st-key-login-form"). Ô nhập có nền xám bo góc, chữ và nút đủ lớn.
    """
    s = scope
    box = (
        f'{s} [data-testid="stTextInputRootElement"], '
        f'{s} [data-testid="stDateInputField"], '
        f'{s} [data-testid="stSelectbox"] [role="group"]'
    )
    box_focus = (
        f'{s} [data-testid="stTextInputRootElement"]:focus-within, '
        f'{s} [data-testid="stDateInputField"]:focus-within, '
        f'{s} [data-testid="stSelectbox"] [role="group"]:focus-within'
    )
    return f"""
    /* ---------- nhãn ---------- */
    {s} [data-testid="stWidgetLabel"] p {{
        color: #526057 !important;
        font-size: {label_size}px !important;
        font-weight: 700 !important;
        margin-bottom: 4px !important;
    }}

    /* ---------- khung ô nhập / ô ngày / ô chọn ---------- */
    {box} {{
        min-height: {height}px !important;
        align-items: center !important;
        background: #e1e3e2 !important;
        border: 1px solid #e1e3e2 !important;
        border-radius: {radius}px !important;
        box-shadow: none !important;
    }}

    {box_focus} {{
        background: #edf8f2 !important;
        border-color: #43bd77 !important;
        box-shadow: 0 0 0 3px rgba(76, 166, 107, 0.12) !important;
    }}

    /* ---------- chữ trong ô ---------- */
    {s} [data-testid="stTextInputField"],
    {s} [data-testid="stSelectbox"] input,
    {s} [data-testid="stDateInputField"] [data-type] {{
        color: #26312b !important;
        font-size: {font_size}px !important;
        -webkit-text-fill-color: #26312b !important;
    }}

    {s} [data-testid="stTextInputField"]::placeholder,
    {s} [data-testid="stSelectbox"] input::placeholder {{
        color: #6b7870 !important;
        -webkit-text-fill-color: #6b7870 !important;
        opacity: 1 !important;
    }}

    {s} [data-testid="stDateInputField"] [data-placeholder="true"] {{
        color: #6b7870 !important;
        -webkit-text-fill-color: #6b7870 !important;
    }}

    /* ---------- icon trong ô ---------- */
    {s} [data-testid="stTextInputIcon"] [data-testid="stIconMaterial"] {{
        color: #718078 !important;
        font-size: {icon_size}px !important;
    }}

    /* ---------- checkbox ---------- */
    {s} [data-testid="stCheckbox"] label p {{
        color: #4ca66b !important;
        font-size: {max(label_size - 1, 14)}px !important;
        font-weight: 700 !important;
    }}

    /* ---------- nút ---------- */
    {s} [data-testid="stButton"] > button {{
        min-height: {button_height}px !important;
        border-radius: {radius}px !important;
    }}

    {s} [data-testid="stButton"] > button p {{
        font-size: {button_font}px !important;
        font-weight: 800 !important;
        letter-spacing: 0.01em;
    }}

    {s} [data-testid="stButton"] > button[kind="primary"] {{
        background: #4ca66b !important;
        border: 1px solid #4ca66b !important;
        box-shadow: 0 10px 20px rgba(76, 166, 107, 0.18) !important;
    }}

    {s} [data-testid="stButton"] > button[kind="primary"] p {{
        color: #ffffff !important;
    }}

    {s} [data-testid="stButton"] > button[kind="primary"]:hover {{
        background: #4ca66b !important;
        border-color: #4ca66b !important;
    }}

    {s} [data-testid="stButton"] > button[kind="secondary"] {{
        background: #ffffff !important;
        border: 2px solid #4ca66b !important;
        box-shadow: none !important;
    }}

    {s} [data-testid="stButton"] > button[kind="secondary"] p {{
        color: #28ad66 !important;
    }}

    {s} [data-testid="stButton"] > button[kind="secondary"]:hover {{
        background: #f1fbf5 !important;
        border-color: #25a960 !important;
    }}
    """
