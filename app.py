import streamlit as st
import sqlite3
import json
import os

st.set_page_config(page_title="School Home Portal - Ultimate Secure Edition", layout="wide")

DB_PATH = "database.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Students Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            roll TEXT PRIMARY KEY,
            name TEXT,
            fname TEXT,
            mname TEXT,
            dob TEXT,
            mobile TEXT,
            pan TEXT,
            apar TEXT,
            class_name TEXT,
            exam_type TEXT,
            slno TEXT,
            school TEXT,
            photo TEXT,
            total REAL,
            max_marks REAL,
            grade TEXT,
            status TEXT,
            subjects TEXT
        )
    ''')
    
    # Schools Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schools (
            id TEXT PRIMARY KEY,
            name TEXT,
            hm TEXT,
            mobile TEXT,
            state TEXT,
            email TEXT,
            pass TEXT,
            utr TEXT,
            status TEXT,
            upi TEXT,
            baseFee REAL,
            hasGst INTEGER,
            gstPct REAL
        )
    ''')
    
    # Default Schools Setup
    cursor.execute("SELECT COUNT(*) FROM schools")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO schools VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       ("155CB", "SRI BAIRAGI SARASWATI SISHU VIDYAMANDIR", "ANTARYAMI DAS", "9876543210", "Odisha", "school@gmail.com", "school123", "MANUAL", "Approved", "school155@upi", 500, 1, 18))
        cursor.execute("INSERT INTO schools VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       ("257CB", "LAXMI NARAYAN GIRLS HIGH SCHOOL", "HEADMASTER", "9876543211", "Odisha", "school2@gmail.com", "school456", "MANUAL2", "Approved", "school257@upi", 500, 1, 18))

    conn.commit()
    conn.close()

init_db()

# Render index.html interface
with open("index.html", "r", encoding="utf-8") as f:
    html_content = f.read()

st.components.v1.html(html_content, height=900, scrolling=True)
