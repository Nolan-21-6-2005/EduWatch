import streamlit as st
from view.pages.auth.sign_in import show_sign_in
from view.pages.auth.sign_up import show_sign_up
from view.dashboards.admin import show_admin_dashboard
from view.dashboards.supervision import show_supervision_dashboard
from view.dashboards.security_guard import show_security_dashboard 

st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed"
)

if 'email' not in st.session_state:
    st.session_state['email'] = ''

if 'role' not in st.session_state:
    st.session_state['role'] = ''

if 'page' not in st.session_state:
    st.session_state['page'] = 'login'

if st.session_state['page'] == 'login':
    show_sign_in()
elif st.session_state['page'] == 'dashboard':
    match st.session_state['role']:
        case 0: show_admin_dashboard()
        case 1: show_supervision_dashboard()
        case 2: show_security_dashboard()
elif st.session_state['page'] == 'signup':
    show_sign_up()
else:
    st.error("Page not found")
