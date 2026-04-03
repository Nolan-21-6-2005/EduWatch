import streamlit as st
import sqlite3
import sys

sys.path.append('/var/home/namson/Webdevelopment/model')
conn = sqlite3.connect("database.db")
cursor = conn.cursor()
    
log_table = cursor.execute("""
    SELECT * FROM violation_logs
""")
    
st.table(log_table)
conn.commit()
conn.close()
