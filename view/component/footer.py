import streamlit as st

def show_footer():
    
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