import streamlit as st
from textwrap import dedent

from src.frontend.login_request import request_login


# ============================================================
# LOGIN PAGE
# ============================================================

def show_sign_in():

    # ========================================================
    # PAGE CSS
    # ========================================================

    st.html(
        dedent(
            """
            <style>

            /* ============================================================
               1. HIDE STREAMLIT DEFAULT UI
               ============================================================ */

            header[data-testid="stHeader"] {
                display: none !important;
            }

            [data-testid="stSidebar"] {
                display: none !important;
            }

            [data-testid="stSidebarCollapsedControl"] {
                display: none !important;
            }


            /* ============================================================
               2. MAIN PAGE
               ============================================================ */

            [data-testid="stMainBlockContainer"] {
                max-width: 1360px !important;

                margin-left: auto !important;
                margin-right: auto !important;

                padding-top: 108px !important;
                padding-bottom: 70px !important;

                padding-left: 28px !important;
                padding-right: 28px !important;
            }


            /* ============================================================
               3. LOGIN LAYOUT
               ============================================================ */

            .st-key-login-shell {
                width: 100% !important;
            }

            .st-key-login-shell > div > [data-testid="stHorizontalBlock"] {
                width: 100% !important;

                gap: 105px !important;

                align-items: flex-start !important;

                /* FIX: Streamlit pre-computes each column's flex-basis assuming
                   its own default (smaller) gap. Overriding gap to 105px makes
                   column1 + column2 + gap exceed the container width, so the
                   default `flex-wrap: wrap` kicks in and the columns stack
                   vertically instead of sitting side by side. Forcing nowrap
                   (and letting flex-shrink do its job) keeps them in one row. */
                flex-wrap: nowrap !important;
            }

            .st-key-login-shell > div > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
                /* Columns default to min-width: auto, which can also block
                   shrinking enough to fit once nowrap is forced above. */
                min-width: 0 !important;
            }


            /* ============================================================
               4. LEFT BANNER
               ============================================================ */

            .login-banner {
                width: 100%;

                padding: 0;

                box-sizing: border-box;

                background: transparent;

                color: #202622;
            }


            /* ============================================================
               5. BRAND
               ============================================================ */

            .login-brand {
                display: flex;

                align-items: center;

                gap: 14px;

                margin-bottom: 34px;
            }


            .login-brand-icon {
                width: 56px;
                height: 56px;

                flex-shrink: 0;

                display: flex;

                align-items: center;
                justify-content: center;

                background: #35bd73;

                color: #ffffff;

                border-radius: 11px;

                box-shadow:
                    0 9px 18px rgba(45, 187, 109, 0.22);
            }


            .login-brand-icon svg {
                width: 35px;
                height: 35px;

                display: block;
            }


            .login-brand-text {
                color: #32bd73;

                font-size: 32px;

                line-height: 1;

                font-weight: 800;

                letter-spacing: -0.04em;
            }


            /* ============================================================
               6. MAIN BANNER TITLE
               ============================================================ */

            .login-banner h1 {
                margin: 0 0 23px 0 !important;

                color: #1d211f !important;

                font-size: 53px !important;

                line-height: 1.13 !important;

                font-weight: 800 !important;

                letter-spacing: -0.048em !important;
            }


            .login-banner h1 .green-text {
                color: #35bd73;
            }


            /* ============================================================
               7. DESCRIPTION
               ============================================================ */

            .login-banner-description {
                max-width: 615px;

                margin: 0;

                color: #526057;

                font-size: 20px;

                line-height: 1.72;

                font-weight: 450;
            }


            /* ============================================================
               8. IMAGE PLACEHOLDER
               ============================================================ */

            .login-media {
                width: 100%;

                height: 452px;

                margin-top: 37px;

                border-radius: 22px;

                background: #d0d0d0;

                display: flex;

                align-items: center;
                justify-content: center;

                overflow: hidden;

                color: #222222;

                font-size: 15px;

                box-shadow:
                    0 18px 35px rgba(37, 51, 44, 0.13);
            }


            /* ============================================================
               9. LOGIN CARD
               ============================================================ */

            .st-key-login-form {
                width: 100% !important;

                min-height: 783px !important;

                padding: 55px 55px 52px !important;

                box-sizing: border-box;

                background: #ffffff;

                border-radius: 27px;

                box-shadow:
                    0 25px 60px rgba(39, 61, 51, 0.10),
                    0 10px 28px rgba(39, 61, 51, 0.06);
            }


            /* ============================================================
               10. LOGIN TITLE
               ============================================================ */

            .login-form-title {
                margin: 0 0 14px 0;

                color: #1d211f;

                text-align: center;

                font-size: 34px;

                line-height: 1.2;

                font-weight: 800;

                letter-spacing: -0.04em;
            }


            .login-form-subtitle {
                margin: 0 0 51px 0;

                color: #526057;

                text-align: center;

                font-size: 20px;

                line-height: 1.4;

                font-weight: 450;
            }


            /* ============================================================
               11. INPUT LABEL
               ============================================================ */

            .st-key-login-form [data-testid="stWidgetLabel"] p {
                color: #526057 !important;

                font-size: 16px !important;

                font-weight: 700 !important;

                margin-bottom: 8px !important;
            }


            /* ============================================================
               12. INPUT
               ============================================================ */

            .st-key-login-form [data-baseweb="input"] > div {
                min-height: 64px !important;

                background: #e1e3e2 !important;

                border: 1px solid #e1e3e2 !important;

                border-radius: 14px !important;

                box-shadow: none !important;
            }


            .st-key-login-form [data-baseweb="input"] > div:focus-within {
                background: #edf8f2 !important;

                border-color: #43bd77 !important;

                box-shadow:
                    0 0 0 3px rgba(45, 187, 109, 0.10) !important;
            }


            .st-key-login-form [data-baseweb="input"] input {
                color: #26312b !important;

                font-size: 17px !important;
            }


            .st-key-login-form [data-baseweb="input"] input::placeholder {
                color: #202622 !important;

                opacity: 1 !important;
            }


            /* ============================================================
               13. INPUT ICON
               ============================================================ */

            .st-key-login-form [data-baseweb="input"] svg {
                color: #718078 !important;
            }


            /* ============================================================
               14. REMEMBER / FORGOT PASSWORD
               ============================================================ */

            .login-forgot {
                padding-top: 8px;

                color: #32bd73;

                text-align: right;

                font-size: 15px;

                font-weight: 700;
            }


            .st-key-login-form .stCheckbox {
                margin-top: 4px;
            }


            .st-key-login-form .stCheckbox label {
                align-items: center !important;
            }


            .st-key-login-form .stCheckbox label p {
                color: #32bd73 !important;

                font-size: 15px !important;

                font-weight: 700 !important;
            }


            /* ============================================================
               15. LOGIN BUTTON
               ============================================================ */

            .st-key-login-form .stButton {
                width: 100%;

                margin-top: 23px;
            }


            .st-key-login-form .stButton > button {
                width: 100% !important;

                min-height: 69px !important;

                border-radius: 14px !important;

                font-size: 18px !important;

                font-weight: 800 !important;

                letter-spacing: 0.01em;
            }


            .st-key-login-form .stButton > button[kind="primary"] {
                background: #35bd73 !important;

                border-color: #35bd73 !important;

                color: #ffffff !important;

                box-shadow:
                    0 10px 20px rgba(45, 187, 109, 0.18) !important;
            }


            .st-key-login-form .stButton > button[kind="primary"]:hover {
                background: #2db56d !important;

                border-color: #2db56d !important;
            }


            /* ============================================================
               16. DIVIDER
               ============================================================ */

            .login-divider {
                display: flex;

                align-items: center;

                gap: 17px;

                margin: 27px 0 24px;

                color: #78837c;

                font-size: 14px;

                font-weight: 700;
            }


            .login-divider-line {
                height: 1px;

                flex: 1;

                background: #e4e8e5;
            }


            /* ============================================================
               17. SIGN UP BUTTON
               ============================================================ */

            .st-key-login-form .stButton > button[kind="secondary"] {
                background: #ffffff !important;

                border: 2px solid #32bd73 !important;

                color: #28ad66 !important;

                min-height: 70px !important;
            }


            .st-key-login-form .stButton > button[kind="secondary"]:hover {
                background: #f1fbf5 !important;

                border-color: #25a960 !important;

                color: #25a960 !important;
            }


            /* ============================================================
               18. MOBILE / TABLET
               ============================================================ */

            @media (max-width: 1100px) {

                [data-testid="stMainBlockContainer"] {
                    padding-top: 55px !important;
                    padding-bottom: 50px !important;

                    padding-left: 20px !important;
                    padding-right: 20px !important;
                }


                .st-key-login-shell > div > [data-testid="stHorizontalBlock"] {
                    gap: 45px !important;
                }


                .login-banner h1 {
                    font-size: 45px !important;
                }


                .login-brand-text {
                    font-size: 28px;
                }


                .login-media {
                    height: 350px;
                }


                .st-key-login-form {
                    min-height: auto !important;

                    padding: 45px 35px !important;
                }
            }


            @media (max-width: 800px) {

                [data-testid="stMainBlockContainer"] {
                    padding-top: 35px !important;
                }


                .st-key-login-shell > div > [data-testid="stHorizontalBlock"] {
                    flex-direction: column !important;

                    /* FIX: nowrap above must be relaxed again on mobile,
                       otherwise the two columns would be forced onto one
                       cramped row instead of stacking as intended here. */
                    flex-wrap: wrap !important;

                    gap: 40px !important;
                }


                .login-banner h1 {
                    font-size: 42px !important;
                }


                .login-media {
                    height: 300px;
                }


                .st-key-login-form {
                    width: 100% !important;

                    padding: 42px 30px !important;
                }
            }


            @media (max-width: 500px) {

                .login-brand-icon {
                    width: 50px;
                    height: 50px;
                }


                .login-brand-icon svg {
                    width: 31px;
                    height: 31px;
                }


                .login-brand-text {
                    font-size: 25px;
                }


                .login-banner h1 {
                    font-size: 36px !important;
                }


                .login-banner-description {
                    font-size: 17px;
                }


                .login-media {
                    height: 240px;
                }


                .st-key-login-form {
                    padding: 35px 22px !important;

                    border-radius: 22px;
                }


                .login-form-title {
                    font-size: 28px;
                }


                .login-form-subtitle {
                    font-size: 17px;

                    margin-bottom: 40px;
                }
            }

            </style>
            """
        )
    )


    # ========================================================
    # MAIN LOGIN CONTAINER
    # ========================================================

    with st.container(key="login-shell"):

        left, right = st.columns(
            [1.08, 0.92],
            gap="small",
        )


        # ====================================================
        # LEFT SIDE
        # ====================================================

        with left:

            st.html(
                dedent(
                    """
                    <div class="login-banner">

                        <!-- BRAND -->
                        <div class="login-brand">

                            <div class="login-brand-icon">

                                <svg
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    xmlns="http://www.w3.org/2000/svg"
                                >

                                    <path
                                        d="M3 9L12 4L21 9L12 14L3 9Z"
                                        stroke="currentColor"
                                        stroke-width="1.8"
                                        stroke-linejoin="round"
                                    />

                                    <path
                                        d="M7 11.2V16.2C7 16.2 9.2 19 12 19C14.8 19 17 16.2 17 16.2V11.2"
                                        stroke="currentColor"
                                        stroke-width="1.8"
                                        stroke-linejoin="round"
                                    />

                                    <path
                                        d="M21 9V14"
                                        stroke="currentColor"
                                        stroke-width="1.8"
                                        stroke-linecap="round"
                                    />

                                </svg>

                            </div>


                            <div class="login-brand-text">
                                EduWatch VNUA
                            </div>

                        </div>


                        <!-- MAIN TITLE -->

                        <h1>
                            Kiến tạo tương lai<br>

                            <span class="green-text">
                                số hóa giáo dục
                            </span>
                        </h1>


                        <!-- DESCRIPTION -->

                        <p class="login-banner-description">
                            Hệ thống giám sát và quản lý đào tạo hiện đại
                            dành cho giảng viên Học viện Nông nghiệp Việt Nam.
                        </p>


                        <!-- IMAGE -->

                        <div class="login-media">
                            img
                        </div>

                    </div>
                    """
                )
            )


        # ====================================================
        # RIGHT SIDE
        # ====================================================

        with right:

            with st.container(key="login-form"):

                # ------------------------------------------------
                # TITLE
                # ------------------------------------------------

                st.html(
                    """
                    <div class="login-form-title">
                        ĐĂNG NHẬP HỆ THỐNG
                    </div>
                    """
                )


                # ------------------------------------------------
                # SUBTITLE
                # ------------------------------------------------

                st.html(
                    """
                    <div class="login-form-subtitle">
                        Cổng thông tin Giám sát Đào tạo
                    </div>
                    """
                )


                # ------------------------------------------------
                # USERNAME
                # ------------------------------------------------

                professor_id = st.text_input(
                    "Tên đăng nhập",
                    placeholder="Nhập mã số người dùng",
                    icon=":material/person:",
                )


                # ------------------------------------------------
                # PASSWORD
                # ------------------------------------------------

                password = st.text_input(
                    "Mật khẩu",
                    type="password",
                    placeholder="••••••••",
                    icon=":material/lock:",
                )


                # ------------------------------------------------
                # REMEMBER / FORGOT
                # ------------------------------------------------

                remember_col, forgot_col = st.columns(
                    [1, 1],
                    gap="small",
                )


                with remember_col:

                    st.checkbox(
                        "Ghi nhớ",
                        value=False,
                    )


                with forgot_col:

                    st.html(
                        """
                        <div class="login-forgot">
                            Quên mật khẩu?
                        </div>
                        """
                    )


                # ------------------------------------------------
                # LOGIN BUTTON
                # ------------------------------------------------

                sign_in = st.button(
                    "ĐĂNG NHẬP",
                    width="stretch",
                    type="primary",
                )


                # ------------------------------------------------
                # DIVIDER
                # ------------------------------------------------

                st.html(
                    """
                    <div class="login-divider">

                        <span class="login-divider-line"></span>

                        <span>HOẶC</span>

                        <span class="login-divider-line"></span>

                    </div>
                    """
                )


                # ------------------------------------------------
                # SIGN UP BUTTON
                # ------------------------------------------------

                sign_up = st.button(
                    "Tạo tài khoản mới",
                    width="stretch",
                    type="secondary",
                )


    # ========================================================
    # LOGIN ACTION
    # ========================================================

    if sign_in:

        request_login(
            professor_id,
            password,
        )


    # ========================================================
    # SIGN UP ACTION
    # ========================================================

    if sign_up:

        st.switch_page(
            "view/pages/auth/sign_up.py"
        )


# ============================================================
# RUN
# ============================================================

show_sign_in()
