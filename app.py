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
        st.error("🚨 Blocked due to repeated failed attempts. Too many incorrect passwords.")
        st.stop()

def send_real_sms(mobile_or_email, otp_code, student_name="User"):
    target = str(mobile_or_email).strip()
    clean_mob = "".join([c for c in target if c.isdigit()])
    if len(clean_mob) == 10:
        clean_mob = "91" + clean_mob
    
    wa_msg = f"Hello {student_name}, your Verification OTP for School Management System is: *{otp_code}*."
    encoded_msg = urllib.parse.quote(wa_msg)
    wa_link = f"https://api.whatsapp.com/send?phone={clean_mob}&text={encoded_msg}" if clean_mob else None
    
    st.success(f"✅ OTP Generated for: **{target}**")
    st.info(f"📲 [SYSTEM OTP DISPLAY] Verification OTP: **{otp_code}**")
    return True

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
    "West Bengal": "Bengali", "Delhi": "Hindi", "Jammu and Kashmir": "Urdu"
}

def load_master_data():
    default_master = {
        "username": "master", "password": "master123", "email": "kulusutar123@gmail.com", 
        "phone": "8910223342", "upi_id": "school@sbi", "reg_fee": 150.0, "gst_percent": 18.0,
        "notice_text": "📢 ସ୍ୱାଗତମ୍! ଅନଲାଇନ୍ ରେଜିଷ୍ଟ୍ରେସନ୍ ଜାରି ରହିଛି।", "news_text": "🔴 [ODISHA] ନୂଆ ଶିକ୍ଷା ନୀତି ଅନୁଯାୟୀ ସମସ୍ତ ସ୍କୁଲରେ ଡିଜିଟାଲ୍ କ୍ଲାସରୁମ୍ ଆରମ୍ଭ ହେବ!"
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
            "pg_upi": "school@sbi"
        }
    }
    default_students = {
        "SCH01": {
            "175CB0078": {
                "name": "ALOKTIKA MISHRA",
                "name_local": "ଆଲୋକତିକା ମିଶ୍ର",
                "gender": "Female",
                "category": "General",
                "pen_no": "21182142821",
                "apaar_no": "704082184322",
                "father_name": "DEBASIS MISHRA",
                "mother_name": "SAROJINI MISHRA",
                "dob": "14-02-2011",
                "class": "10",
                "batch": "2025-2026",
                "pub_date": "22-09-2026",
                "subjects": {
                    "First Language Odia": {"full": 100.0, "obt": 90.0},
                    "Second Language English": {"full": 100.0, "obt": 67.0},
                    "Mathematics": {"full": 100.0, "obt": 66.0}
                },
                "total_full": 300.0, "total_obt": 223.0, "percentage": 74.33,
                "result": "PASS", "grade": "B1", "status": "Approved"
            }
        }
    }
    schools = dict(default_schools)
    students = dict(default_students)

    if os.path.exists(SCHOOLS_FILE):
        try:
            with open(SCHOOLS_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if content.strip(): 
                    loaded = json.loads(content)
                    if isinstance(loaded, dict): schools.update(loaded)
        except Exception:
            pass

    if os.path.exists(STUDENTS_FILE):
        try:
            with open(STUDENTS_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if content.strip(): 
                    loaded = json.loads(content)
                    if isinstance(loaded, dict):
                        for s_k, s_v in loaded.items():
                            if s_k not in students: students[s_k] = s_v
                            else: students[s_k].update(s_v)
        except Exception:
            pass

    return schools, students

def save_data(schools, students):
    atomic_save(schools, SCHOOLS_FILE)
    atomic_save(students, STUDENTS_FILE)

schools_db, students_db = load_data()
master_db = load_master_data()

menu_items = ["Home Page", "Master Login", "School Login"]
menu = st.sidebar.selectbox("🎯 Navigation Menu", menu_items)

if menu == "HomePage" or menu == "Home Page":
    st.subheader("🏫 Welcome to Advanced School Management System")
    st.write("Please select your portal from the sidebar menu to login or register.")

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
        st.success("Welcome Master Admin! All systems operating securely.")

elif menu == "School Login":
    st.subheader("🏫 School Portal Login")
    if 'school_logged_id' not in st.session_state:
        s_login_state = st.selectbox("📍 Select State", list(STATE_LANG_MAP.keys()), index=18)
        s_id = st.text_input("School ID")
        s_pass = st.text_input("School Password", type="password")
        
        if st.button("Login as School"):
            s_id_clean = sanitize(s_id)
            if s_id_clean in schools_db:
                sch_entry = schools_db[s_id_clean]
                if sch_entry.get("pass") == s_pass:
                    st.session_state['school_logged_id'] = s_id_clean
                    st.success("Login Successful!")
                    st.rerun()
                else:
                    st.error("❌ ଭୁଲ୍ Password!")
            else:
                st.error("❌ ଏହି School ID ମିଳିଲା ନାହିଁ!")
    else:
        cur_school = st.session_state['school_logged_id']
        sch_data = schools_db[cur_school]
        st.info(f"🏫 **School Dashboard** | ID: {cur_school} | {sch_data['name']}")
        if st.button("🔴 Logout School"):
            del st.session_state['school_logged_id']
            st.rerun()
        
        t_list, t_add = st.tabs(["📋 My Students", "➕ Add Student"])
        with t_list:
            st.markdown("### My Registered Students")
            cur_students = students_db.get(cur_school, {})
            for r_no, s_info in cur_students.items():
                st.write(f"Roll: **{r_no}** | Name: **{s_info.get('name')}**")
            if not cur_students:
                st.info("No students found.")

st.markdown("---")
st.markdown("<div style='text-align: center; padding: 15px; background: linear-gradient(90deg, #1e3a8a, #9333ea); color: white; border-radius: 8px; font-weight: bold;'>👨‍💻 Software Developed by: KULU SUTAR | 📞 Mob: 8910223342 | ✉️ kulusutar123@gmail.com</div>", unsafe_allow_html=True)
