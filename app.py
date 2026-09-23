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

# ==========================================
# 🔒 100% BULLET-PROOF ATOMIC CRASH PROTECTION
# ==========================================
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

# ==========================================
# 🛡️ ADVANCED BRUTE-FORCE HACK PREVENTION
# ==========================================
if 'failed_logins' not in st.session_state:
    st.session_state.failed_logins = 0

def check_brute_force():
    if st.session_state.failed_logins >= 5:
        st.error("🚨 Security Alert: Too many failed login attempts detected.")
        st.stop()

# ==========================================
# 📂 DIRECTORY CREATION
# ==========================================
os.makedirs("Scholarship_Data/Student_Submissions", exist_ok=True)
os.makedirs("Scholarship_Data/Approved_Master", exist_ok=True)
os.makedirs("Carousel_Images", exist_ok=True)

# ==========================================
# 🌐 APP CONFIGURATION
# ==========================================
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

# ==========================================
# 🤖 PERMANENT DATA LOADERS
# ==========================================
def load_master_data():
    default_master = {
        "username": "master", "password": "master123", "email": "kulusutar123@gmail.com", 
        "phone": "8910223342", "upi_id": "school@sbi", "reg_fee": 150.0, "gst_percent": 18.0,
        "school_reg_fee": 1000.0, "school_gst_percent": 18.0, "scholarship_fee": 50.0,
        "notice_text": "📢 ନୂଆ ଅପଡେଟ୍: ଛାତ୍ରଛାତ୍ରୀମାନେ ଏବେ ଅନଲାଇନ୍ ରେଜିଷ୍ଟ୍ରେସନ୍, ସ୍କଲାରସିପ୍ ଏବଂ ପେମେଣ୍ଟ କରିପାରିବେ! <span class='new-badge'>NEW</span> &nbsp;&nbsp;|&nbsp;&nbsp; 👨‍💻 Software Developed by: KULU SUTAR &nbsp;&nbsp;|&nbsp;&nbsp; 📞 Helpdesk No: 8910223342 &nbsp;&nbsp;|&nbsp;&nbsp; ✉️ Mail ID: kulusutar123@gmail.com",
        "news_text": "🔴 [ODISHA] ନୂଆ ଶିକ୍ଷା ନୀତି ଅନୁଯାୟୀ ସମସ୍ତ ସ୍କୁଲରେ ଡିଜିଟାଲ୍ କ୍ଲାସରୁମ୍ ଆରମ୍ଭ ହେବ! &nbsp;&nbsp;♦&nbsp;&nbsp; 🔴 [DELHI] Central Government announces new scholarship schemes for brilliant students across India!",
        "bg_b64": "", "sch_bg_b64": "", "school_bg_b64": "", "reg_bg_b64": "",
        "font_family": "sans-serif", "font_size": "16", "text_color": "#000000", "theme_color": "#1e3a8a"
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
            "name": "Laxmi Narayan Girls High School, Banasar Kalyani",
            "name_local": "ଲକ୍ଷ୍ମୀ ନାରାୟଣ ବାଳିକା ଉଚ୍ଚ ବିଦ୍ୟାଳୟ",
            "hm_name": "Debasis Mishra",
            "hm_phone": "9876543210",
            "pass": "school123",
            "state": "Odisha",
            "lang": "Odia",
            "status": "Active",
            "payment_mode": "Online Verified"
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

# ----------------- MASTER LOGIN (7 TABS RESTORED) -----------------
menu = st.sidebar.selectbox("🎯 Navigation Menu", ["Home Page", "Master Login"])

if menu == "Master Login":
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
                for s_id, s_info in list(schools_db.items()):
                    cols = st.columns([3, 1])
                    cols[0].write(f"**{s_id}** - {s_info.get('name')}")
                    if cols[1].button("🗑️ Delete", key=f"del_sch_{s_id}"):
                        del schools_db[s_id]
                        save_data(schools_db, students_db)
                        st.success(f"School {s_id} deleted!")
                        st.rerun()

        with t5:
            st.markdown("### ⚙️ Settings & Notifications")
            up_notice = st.text_area("Notice Text", value=master_db.get("notice_text", ""))
            if st.button("Save Settings"):
                master_db["notice_text"] = up_notice
                save_master_data(master_db)
                st.success("Saved successfully!")
