import streamlit as st

def kpi_metric(kpi, color):
    if color == "green":
        st.html(
        f'''
        <div class="ew-bottom-stat">
            <div class="ew-bottom-icon green">♣</div>
            <div>
                <span>Tổng log dự đoán</span>
                <strong>{kpi}</strong>
                <small>Số log đã dự đoán</small>
            </div>
        </div>
        ''',
        )
    if color == "blue":
        st.html(
            f'''
            <div class="ew-bottom-stat">
                <div class="ew-bottom-icon blue">◆</div>
                <div>
                    <span>Giảng viên</span>
                    <strong>{kpi}</strong>
                    <small>Tài khoản giảng viên</small>
                </div>
            </div>
            ''',
        )
    if color == "orange":
        st.html(
            f'''
            <div class="ew-bottom-stat">
                <div class="ew-bottom-icon orange">◇</div>
                <div>
                    <span>Bảo vệ</span>
                    <strong>{kpi}</strong>
                    <small>Tài khoản bảo vệ</small>
                </div>
            </div>
            ''',
        )