import streamlit as st

def kpi_metric(kpi, header, caption, color):
    if color == "green":
        st.html(
        f'''
        <div class="ew-bottom-stat">
            <div class="ew-bottom-icon green">♣</div>
            <div>
                <span>{header}</span>
                <strong>{kpi}</strong>
                <small>{caption}</small>
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
                    <span>{header}</span>
                    <strong>{kpi}</strong>
                    <small>{caption}</small>
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
                    <span>{header}</span>
                    <strong>{kpi}</strong>
                    <small>{caption}</small>
                </div>
            </div>
            ''',
        )
