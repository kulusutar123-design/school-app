import streamlit as st
import streamlit.components.v1 as components
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.barcode import code128, qr, createBarcodeDrawing
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
import json
import os
import io
import datetime
import random
import urllib.parse
import urllib.request
import ssl
import html
import threading
import base64
import time
import requests

file_lock = threading.Lock()

def sanitize(text):
    if isinstance(text, str):
        return html.escape(text.strip())
    return text

def atomic_save(data, filename):
    with file_lock:
        try:
            temp_filename = filename + ".tmp"
            with open(temp_filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            os.replace(temp_filename, filename)
        except Exception as e:
            st.error(f"🚨 Security Alert: Failed to save {filename}. Error: {e}")

if 'failed_logins' not in st.session_state:
    st.session_state.failed_logins = 0

def check_brute_force():
    if st.session_state.failed_logins >= 5:
        st.error("🚨 Blocked due to repeated failed attempts.")
        st.stop()

os.makedirs("Scholarship_Data/Student_Submissions", exist_ok=True)
os.makedirs("Scholarship_Data/Approved_Master", exist_ok=True)
os.makedirs("Carousel_Images", exist_ok=True)

st.set_page_config(page_title="Advanced School Management System", layout="wide")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

SCHOOLS_FILE = "schools.json"
STUDENTS_FILE = "students.txt"
MASTER_FILE = "master.json"
SCHOLARSHIPS_FILE = "scholarships.json"
SCH_USERS_FILE = "sch_users.json"

STATE_LANG_MAP = {
    "Andhra Pradesh": "Telugu", "Arunachal Pradesh": "English", "Assam": "Assamese",
    "Bihar": "Hindi", "Chhattisgarh": "Hindi", "Goa": "Konkani",
    "Gujarat": "Gujarati", "Haryana": "Hindi", "Himachal Pradesh": "Hindi",
    "Jharkhand": "Hindi", "Karnataka": "Kannada", "Kerala": "Malayalam",
    "Madhya Pradesh": "Hindi", "Maharashtra": "Marathi", "Manipur": "English",
    "Meghalaya": "English", "Mizoram": "English", "Nagaland": "English",
    "Odisha": "Odia", "Punjab": "Punjabi", "Rajasthan": "Hindi",
    "Sikkim": "English", "Tamil Nadu": "Tamil", "Telangana": "Telugu",
    "Tripura": "Bengali", "Uttar Pradesh": "Hindi", "Uttarakhand": "Hindi",
    "West Bengal": "Bengali", "Delhi": "Hindi", "Jammu and Kashmir": "Urdu",
    "Ladakh": "English", "Puducherry": "Tamil", "Chandigarh": "Punjabi",
    "Andaman and Nicobar": "English", "Lakshadweep": "Malayalam", "Dadra & Nagar Haveli": "Gujarati"
}

def load_master_data():
    default_master = {
        "username": "master", "password": "master123", "email": "kulusutar123@gmail.com", 
        "phone": "8910223342", "upi_id": "school@sbi", "reg_fee": 150.0, "gst_percent": 18.0,
        "school_reg_fee": 1000.0, "school_gst_percent": 18.0, "scholarship_fee": 50.0,
        "notice_text": "📢 ନୂଆ ଅପଡେଟ୍: ଛାତ୍ରଛାତ୍ରୀମାନେ ଏବେ ଅନଲାଇନ୍ ରେଜିଷ୍ଟ୍ରେସନ୍, ସ୍କଲାରସିପ୍ ଏବଂ ପେମେଣ୍ଟ କରିପାରିବେ!",
        "news_text": "🔴 [ODISHA] ନୂଆ ଶିକ୍ଷା ନୀତି ଅନୁଯାୟୀ ସମସ୍ତ ସ୍କୁଲରେ ଡିଜିଟାଲ୍ କ୍ଲାସରୁମ୍ ଆରମ୍ଭ ହେବ!",
        "bg_b64": "", "font_family": "sans-serif", "font_size": "16", "text_color": "#000000", "theme_color": "#1e3a8a"
    }
    if os.path.exists(MASTER_FILE):
        try:
            with open(MASTER_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if content.strip():
                    m = json.loads(content)
                    for k, v in default_master.items():
                        if k not in m: m[k] = v
                    return m
        except Exception:
            pass
    return default_master

def save_master_data(data):
    atomic_save(data, MASTER_FILE)

def load_data():
    default_schools = {
        "SCH01": {
            "name": "Laxmi Narayan Girls High School",
            "hm_name": "Debasis Mishra",
            "hm_phone": "9876543210",
            "pass": "school123",
            "state": "Odisha",
            "lang": "Odia",
            "status": "Active",
            "pg_upi": "school@sbi"
        }
    }
    schools = dict(default_schools)
    students = {}

    if os.path.exists(SCHOOLS_FILE):
        try:
            with open(SCHOOLS_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if content.strip(): 
                    loaded = json.loads(content)
                    if isinstance(loaded, dict): schools.update(loaded)
        except Exception:
            pass
    return schools, students

def save_data(schools, students):
    atomic_save(schools, SCHOOLS_FILE)
    atomic_save(students, STUDENTS_FILE)

schools_db, students_db = load_data()
master_db = load_master_data()

menu = st.sidebar.selectbox("🎯 Navigation Menu", ["Home Page", "Master Login", "New School Registration"])

if menu == "Home Page":
    st.subheader("🏫 Welcome to Advanced School Management System")
    st.write("Use the sidebar to access Master Login, School Registrations, and Portals.")

elif menu == "Master Login":
    st.subheader("🔑 Master Administrator Portal")
    if not st.session_state.get('master_logged', False):
        m_user = st.text_input("Master Username")
        m_pass = st.text_input("Master Password", type="password")
        if st.button("Login"):
            if sanitize(m_user) == master_db.get("username") and m_pass == master_db.get("password"):
                st.session_state['master_logged'] = True
                st.rerun()
            else:
                st.error("ଭୁଲ୍ Master ID କିମ୍ବା Password!")
    else:
        if st.button("🔴 Logout"):
            st.session_state['master_logged'] = False
            st.rerun()

        t1, t2, t3, t4, t5, t6, t7 = st.tabs(["👁️ Schools", "💳 Payments", "🎓 Scholarships Verify", "🎓 Edit Students", "⚙️ Settings", "🏦 Gateway", "🖼️ Display & Backgrounds"])
        
        with t1:
            st.markdown("### 🏫 School Management Dashboard")
            with st.expander("⚙️ Master School Control Box", expanded=True):
                if schools_db:
                    for s_id, s_info in list(schools_db.items()):
                        cols_d = st.columns([3, 1])
                        cols_d[0].markdown(f"**{s_id}** - {s_info.get('name')} (Status: {s_info.get('status', 'Active')})")
                        if cols_d[1].button("🗑️ Delete", key=f"btn_del_safe_{s_id}"):
                            del schools_db[s_id]
                            if s_id in students_db: del students_db[s_id]
                            save_data(schools_db, students_db)
                            st.success(f"School {s_id} deleted successfully!")
                            time.sleep(0.3)
                            st.rerun()
                else:
                    st.info("No schools registered.")

        with t5:
            st.markdown("### ⚙️ Settings & Notifications")
            up_notice = st.text_area("Official Running Notification Text", value=master_db.get("notice_text", ""))
            up_news = st.text_area("Breaking Running News Text", value=master_db.get("news_text", ""))
            if st.button("Save Settings", key="m_set_save_all"):
                master_db["notice_text"] = up_notice
                master_db["news_text"] = up_news
                save_master_data(master_db)
                st.success("Settings updated successfully!")
                st.rerun()

        with t6:
            st.markdown("### 🏦 School Payment Gateway Setup (Master Control)")
            if schools_db:
                pg_school = st.selectbox("Select School", list(schools_db.keys()), key="m_gw_sch_sel")
                current_upi = schools_db[pg_school].get('pg_upi', 'school@sbi')
                sch_upi = st.text_input("School UPI ID", value=current_upi, key="m_gw_upi")
                if st.button("💾 Save School Gateway", key="m_gw_save"):
                    schools_db[pg_school]['pg_upi'] = sanitize(sch_upi)
                    save_data(schools_db, students_db)
                    st.success(f"Payment Gateway for {pg_school} successfully updated!")
            else:
                st.info("No schools available.")

        with t7:
            st.markdown("### 🖼️ Portal Backgrounds & Running Display Management")
            up_h_bg = st.file_uploader("Upload Home Page Background Image", type=['png', 'jpg', 'jpeg'], key="h_bg")
            if st.button("💾 Save Home Background", key="save_bgs"):
                if up_h_bg: 
                    master_db["bg_b64"] = base64.b64encode(up_h_bg.read()).decode('utf-8')
                    save_master_data(master_db)
                    st.success("Home Background Saved Successfully!")
                    st.rerun()
            
            st.markdown("#### Carousel Running Images Management")
            uploaded_carousel = st.file_uploader("Upload Images for Running Display", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True, key="m_carousel_up")
            if st.button("📤 Upload to Running Display", key="m_carousel_btn"):
                if uploaded_carousel:
                    for file in uploaded_carousel:
                        with open(os.path.join("Carousel_Images", file.name), "wb") as f:
                            f.write(file.getbuffer())
                    st.success("Images uploaded successfully!")
                    st.rerun()

st.markdown("---")
st.markdown("<div style='text-align: center; padding: 15px; background: linear-gradient(90deg, #1e3a8a, #9333ea); color: white; border-radius: 8px; font-weight: bold;'>👨‍💻 Software Developed by: KULU SUTAR | 📞 Mob: 8910223342 | ✉️ kulusutar123@gmail.com</div>", unsafe_allow_html=True)
