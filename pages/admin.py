import streamlit as st
import controller as ctr
import sqlite3
import sys

sys.path.append('/var/home/namson/Webdevelopment/modules')
conn = sqlite3.connect("database.db")
cursor = conn.cursor()
tab1, tab2, tab3, tab4 = st.tabs(["Camera", "Rooms", "Buildings", "Users"])

with tab1:
    if st.button("Thêm camera"):
        ctr.addCamera()
    camera_table = cursor.execute("""
        SELECT * FROM camera
    """)
    st.table(camera_table)
with tab2:
    if st.button("Thêm phòng"):
        ctr.addRooms()
    rooms_table = cursor.execute("""
        SELECT * FROM rooms
    """)
    st.table(rooms_table)
with tab3:
    if st.button("Thêm tòa nhà"):
        ctr.addBuildings()
    buildings_table = cursor.execute("""
        SELECT * FROM buildings
    """)
    st.table(buildings_table)
with tab4:
    users_table = cursor.execute("""
        SELECT * FROM users
    """)
    st.table(users_table)
conn.commit()
conn.close()
