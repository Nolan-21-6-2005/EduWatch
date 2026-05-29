from streamlit_option_menu import option_menu
from view.style.style_option_menu import OPTION_MENU_STYLES
import streamlit as st

def get_selection():
    top = st.container()
    bottom = st.container()
        
    with top:
        selected = option_menu(
            None, [
                "Giám sát trực tiếp", "Quản lý người dùng", "Thống kê báo cáo", 'Settings'
            ],
            icons = [
                'camera-video', 'journal', 'bar-chart', 'gear'
            ], 
            menu_icon="cast", 
            default_index=0,
            styles = OPTION_MENU_STYLES,
        )
    with bottom:
        st.markdown("---")

        col1, col2 = st.columns([1, 3])
        with col1:
            st.image("data_model/avatar/avatar.jpg", width=50)
        
        with col2:
            email = st.session_state['email']
            role = st.session_state['role']
            st.markdown(email)
            st.caption(role)

    signout = st.button("Đăng xuất")
    if signout:
        st.session_state['page'] = 'login'
        st.rerun()
    return selected

