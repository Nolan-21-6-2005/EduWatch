import streamlit as st
from pathlib import Path
import sqlite3
import sys
import os
from modules import controller as ctr

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "model" / "eduwatch.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

tab1, tab2, tab3, tab4 = st.tabs(["Camera", "Rooms", "Buildings", "Users"])

with tab1:
    #CRUD bảng camera 
    if st.button("Thêm camera"):
        ctr.addCamera()
    if st.button("Cập nhật camera"):
        ctr.updateCamera()            
    #if st.button("Xóa phòng"):
    #Truy vấn bảng camera
    camera_table = cursor.execute("""
        SELECT * FROM Cameras
    """)
    st.data_editor(camera_table, num_rows="dynamic")
with tab2:
    #CRUD bảng phòng
    if st.button("Thêm phòng"):
        ctr.addRooms()
    if st.button("Cập nhật phòng"):
        ctr.updateRooms()            
    #if st.button("Xóa phòng"):    
    #Truy vấn bảng phòng
    rooms_table = cursor.execute("""
            SELECT * FROM Rooms
    """)
    st.data_editor(rooms_table, num_rows="dynamic")
with tab3:
    if st.button("Thêm tòa nhà"):
        ctr.addCamera()
    if st.button("Cập nhật tòa nhà"):
        ctr.updateCamera()            
    #if st.button("Xóa phòng"):
        #ctr.addBuildings()
                
    buildings_table = cursor.execute("""
        SELECT * FROM Buildings
    """)
    st.data_editor(buildings_table, num_rows="dynamic")
with tab4:
    users_table = cursor.execute("""
        SELECT * FROM Users
    """)
    st.data_editor(users_table, num_rows="dynamic")
conn.commit()
conn.close()
