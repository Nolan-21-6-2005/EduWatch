# Giữ tương thích nếu project còn sử dụng streamlit-option-menu ở nơi khác.
# Phong cách đồng bộ với giao diện Medcare: nền trắng, bo góc mềm,
# trạng thái chọn dùng xanh dương, màu nhận diện chính vẫn là xanh EduWatch.
OPTION_MENU_STYLES = {
    "container": {
        "padding": "4px!important",
        "background-color": "transparent",
    },
    "icon": {
        "font-size": "18px",
        "color": "#7B8794",
    },
    "nav-link": {
        "font-size": "14px",
        "text-align": "left",
        "margin": "3px 0px",
        "padding": "10px 12px",
        "border-radius": "11px",
        "background-color": "transparent",
        "color": "#687483",
    },
    "nav-link-selected": {
        "background-color": "#EDF4FF",
        "color": "#3478F6",
    },
}
