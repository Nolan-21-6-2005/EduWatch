from streamlit_option_menu import option_menu
from view.component.footer import show_footer
from view.style.style_option_menu import OPTION_MENU_STYLES
import streamlit as st

def get_security_selection():
    top = st.container()
    bottom = st.container()
        
    with top:
        selected = option_menu(
            None, [
                "Giám sát an ninh", "Trạng thái thiết bị", "Báo cáo sự cố"
            ],
            icons = [
                'shield-check', 'cpu', 'exclamation-triangle'
            ], 
            menu_icon="cast", 
            default_index=0,
            styles = OPTION_MENU_STYLES,
        )
        
    with bottom:
        st.markdown("---")

        show_footer()
    return selected

