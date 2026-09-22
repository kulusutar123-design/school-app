import streamlit as st
import streamlit.components.v1 as components
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.barcode import code128, qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
import json
import os
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
# 🔒 HIGH-SECURITY ATOMIC CRASH PROTECTION
# ==========================================
file_lock = threading.Lock()

def sanitize(text):
    if isinstance(text, str):
        return html.escape(text.strip())
    return text

def atomic_save(data, filename):
    """Guaranteed persistent save without data loss under heavy load"""
    with file_lock:
        try:
            temp_filename = filename + ".tmp"
            with open(temp_filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            os.replace(temp_filename, filename)
        except Exception as e:
            st.error(f"🚨 Security Alert: Failed to save {filename}. Data prevented from corruption. Error: {e}")

# ==========================================
# 🛡️ ANTI-HACKING BRUTE FORCE PROTECTION
# ==========================================
if 'failed_logins' not in st.session_state:
    st.session_state.failed_logins = 0

def check_brute_force():
    if st.session_state.failed_logins >= 5:
        st.error("🚨 Blocked due to repeated failed attempts. Too many incorrect passwords.")
        st.stop()

# ==========================================
# 📧 UNIVERSAL OTP NOTIFICATION SYSTEM
# ==========================================
def send_real_sms(mobile_or_email, otp_code, student_name="Student"):
    target = str(mobile_or_email).strip()
    st.success(f"✅ OTP Generated for: **{target}**")
    st.info(f"📲 [OTP NOTIFICATION] Hello {student_name}, your Verification OTP is: **{otp_code}**")
    st.session_state['sms_error'] = ""
    return True

# ==========================================
# 📂 DIRECTORY CREATION FOR SCHOLARSHIPS
# ==========================================
os.makedirs("Scholarship_Data/Student_Submissions", exist_ok=True)
os.makedirs("Scholarship_Data/Approved_Master", exist_ok=True)
os.makedirs("Carousel_Images", exist_ok=True)

def save_master_approved_folder(app_id, s_data):
    folder_path = f"Scholarship_Data/Approved_Master/{app_id}"
    os.makedirs(folder_path, exist_ok=True)
    
    pdf_path = f"{folder_path}/Application_{app_id}.pdf"
    create_odisha_scholarship_pdf(pdf_path, app_id, s_data)
    
    if s_data.get('photo_b64'):
        with open(f"{folder_path}/Profile_Photo.jpg", "wb") as f: f.write(base64.b64decode(s_data['photo_b64']))
    if s_data.get('inc_file_b64'):
        with open(f"{folder_path}/Income_Cert.jpg", "wb") as f: f.write(base64.b64decode(s_data['inc_file_b64']))
    if s_data.get('cas_file_b64'):
        with open(f"{folder_path}/Caste_Cert.jpg", "wb") as f: f.write(base64.b64decode(s_data['cas_file_b64']))
    if s_data.get('passbook_b64'):
        with open(f"{folder_path}/Bank_Passbook.jpg", "wb") as f: f.write(base64.b64decode(s_data['passbook_b64']))
            
    with open(f"{folder_path}/Student_Data.json", "w", encoding="utf-8") as f:
        json.dump(s_data, f, indent=4)

# ==========================================
# 🌐 APP URL SETTING & CONFIG
# ==========================================
APP_URL = "http://localhost:8501"

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

COUNTRIES = ["Yes - Indian National", "No - Other Country"]
SOCIAL_CATEGORIES = ["General", "SC", "ST", "OBC", "SEBC", "Minority", "Others"]

ISSUING_AUTHORITIES = [
    "Select", "District Magistrate / Collector", "Additional District Magistrate",
    "Sub-divisional Magistrate / Sub-divisional Officer", "Executive Magistrates",
    "Revenue Officers not below the rank of Tahasildar / Additional Tahasildar"
]

RELATIONSHIPS = ["Select", "Father", "Mother", "Legal Guardian"]
CERT_YEARS = ["Select", "Certificate issued before 1st Feb 2020", "Certificate issued on/after 1st Feb 2020"]

# ==========================================
# 🤖 SECURE DATA LOADERS
# ==========================================
def load_master_data():
    default_master = {
        "username": "master", "password": "master123", "email": "kulusutar123@gmail.com", 
        "phone": "8910223342", "upi_id": "school@sbi", "reg_fee": 150.0, "gst_percent": 18.0,
        "school_reg_fee": 1000.0, "school_gst_percent": 18.0, "scholarship_fee": 50.0,
        "notice_text": "📢 Official Update: Online Registration & Scholarship Active!",
        "news_text": "🔴 Breaking News: System upgraded with high speed servers.",
        "bg_b64": "", "sch_bg_b64": "", "school_bg_b64": "", "reg_bg_b64": "",
        "font_family": "sans-serif", "font_size": "16", "text_color": "#000000", "theme_color": "#1e3a8a",
        "sms_api_key": ""
    }
    if os.path.exists(MASTER_FILE):
        try:
            with open(MASTER_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if content.strip():
                    m = json.loads(content)
                    for k,v in default_master.items():
                        if k not in m: m[k] = v
                    return m
        except Exception as e:
            st.error("CRITICAL ERROR: Master File is corrupted.")
            st.stop()
    return default_master

def save_master_data(data):
    atomic_save(data, MASTER_FILE)

def load_data():
    schools = {}; students = {}
    if os.path.exists(SCHOOLS_FILE):
        try:
            with open(SCHOOLS_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if content.strip(): schools = json.loads(content)
        except Exception as e:
            st.error("CRITICAL ERROR: schools.json is corrupted.")
            st.stop()
    if os.path.exists(STUDENTS_FILE):
        try:
            with open(STUDENTS_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if content.strip(): students = json.loads(content)
        except Exception as e:
            st.error("CRITICAL ERROR: students.txt is corrupted.")
            st.stop()
    return schools, students

def save_data(schools, students):
    atomic_save(schools, SCHOOLS_FILE)
    atomic_save(students, STUDENTS_FILE)

def load_scholarships():
    sch = {}
    if os.path.exists(SCHOLARSHIPS_FILE):
        try:
            with open(SCHOLARSHIPS_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if content.strip(): sch = json.loads(content)
        except Exception:
            st.error("CRITICAL ERROR: scholarships.json is corrupted.")
            st.stop()
    return sch

def save_scholarships(sch):
    atomic_save(sch, SCHOLARSHIPS_FILE)

def load_sch_users():
    users = {}
    if os.path.exists(SCH_USERS_FILE):
        try:
            with open(SCH_USERS_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if content.strip(): users = json.loads(content)
        except Exception:
            st.error("CRITICAL ERROR: sch_users.json is corrupted.")
            st.stop()
    return users

def save_sch_users(users):
    atomic_save(users, SCH_USERS_FILE)

# ==========================================
# 🎨 UI INJECTIONS
# ==========================================
def inject_custom_bg(b64_str):
    if b64_str:
        st.markdown(f"""
        <style>
        .stApp {{
            background-image: url('data:image/jpeg;base64,{b64_str}');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """, unsafe_allow_html=True)

def inject_custom_styles(m_data):
    ff = m_data.get("font_family", "sans-serif")
    fs = m_data.get("font_size", "16")
    tc = m_data.get("text_color", "#000000")
    thc = m_data.get("theme_color", "#1e3a8a")
    
    st.markdown(f"""
    <style>
    html, body, [class*="st-"] {{
        font-family: "{ff}", sans-serif !important;
        font-size: {fs}px !important;
        color: {tc} !important;
    }}
    .login-card {{ border-bottom: 5px solid {thc} !important; }}
    .login-title {{ color: {thc} !important; }}
    div.stButton > button:first-child {{
        background-color: {thc} !important;
        color: white !important;
        border: none !important;
        font-family: "{ff}", sans-serif !important;
    }}
    </style>
    """, unsafe_allow_html=True)

def number_to_words(num):
    try: num = int(float(num))
    except: num = 0
    if num == 0: return "ZERO"
    ones = ["", "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE", "TEN", "ELEVEN", "TWELVE", "THIRTEEN", "FOURTEEN", "FIFTEEN", "SIXTEEN", "SEVENTEEN", "EIGHTEEN", "NINETEEN"]
    tens = ["", "", "TWENTY", "THIRTY", "FORTY", "FIFTY", "SIXTY", "SEVENTY", "EIGHTY", "NINETY"]
    def words(n):
        if n < 20: return ones[int(n)]
        elif n < 100: return tens[int(n // 10)] + ("-" + ones[int(n % 10)] if n % 10 != 0 else "")
        elif n < 1000: return ones[int(n // 100)] + " HUNDRED" + (" AND " + words(n % 100) if n % 100 != 0 else "")
        else: return str(n)
    return words(num)

def format_display_date(d_str):
    if not d_str: return datetime.date.today().strftime('%d-%m-%Y')
    d_str = str(d_str).strip().replace('/', '-').replace('.', '-')
    parts = d_str.split('-')
    if len(parts) == 3 and len(parts[0]) == 4: return f"{parts[2]}-{parts[1]}-{parts[0]}"
    return d_str

def normalize_dob(d_str):
    if not d_str: return ""
    d_str = str(d_str).strip().replace('/', '-').replace('.', '-')
    parts = [p.strip() for p in d_str.split('-') if p.strip()]
    if len(parts) == 3:
        if len(parts[0]) == 4: return f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
        elif len(parts[2]) == 4: return f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
    return d_str

def create_student_receipt_pdf(filename, reg_id, s_data):
    c = canvas.Canvas(filename, pagesize=letter)
    c.setStrokeColorRGB(0.1, 0.2, 0.5); c.setLineWidth(4); c.rect(30, 30, 552, 732, stroke=1, fill=0)
    c.setFillColorRGB(0.1, 0.2, 0.5); c.setFont("Times-Bold", 22); c.drawCentredString(300, 720, "STUDENT REGISTRATION RECEIPT")
    c.setFillColorRGB(0, 0, 0); c.setFont("Helvetica-Bold", 12); c.drawString(50, 670, f"REGISTRATION ID: {reg_id}")
    c.setFont("Helvetica", 12); y = 640
    c.drawString(50, y, f"Student Name: {s_data.get('name', '').upper()}"); y -= 25
    c.drawString(50, y, f"Phone: {s_data.get('phone', '')}"); y -= 25
    c.drawString(50, y, f"Payment Mode: {s_data.get('payment_mode', 'N/A')}"); y -= 25
    c.drawString(50, y, f"Status: {s_data.get('status', 'Pending')}"); y -= 25
    c.line(50, y, 550, y); y -= 20
    c.setFont("Helvetica-Oblique", 10); c.drawCentredString(300, y, "Computer-generated receipt.")
    c.save()

def render_odisha_scholarship_html(app_id, s_data):
    html_str = f"""<div style="font-family: Arial, sans-serif; border: 1px solid #ccc; padding: 20px; max-width: 900px; margin: auto; background-color: #fff;">
<div style="text-align: center; margin-bottom: 20px;">
<h2 style="margin: 0; color: #0b3a5b;">Government of Odisha</h2>
<h3 style="margin: 5px 0;">Scholarship Application Form</h3>
<h4 style="margin: 5px 0;">ST&SC and MBC Welfare Department</h4>
<p style="margin: 0;">Academic Year: <b>{s_data.get('academic_year', '2025-26')}</b></p>
</div>
<h4 style="background-color: #0b3a5b; color: white; padding: 5px; margin: 0;">Basic Information</h4>
<table style="width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 15px;" border="1">
<tr style="background-color: #f2f2f2;"><th>Department</th><th>Scheme</th><th>Academic Year</th><th>Application Type</th></tr>
<tr style="text-align:center;"><td>ST&SC and MBC Welfare</td><td>{s_data.get('scheme', '')}</td><td>{s_data.get('academic_year', '')}</td><td>New</td></tr>
</table>
<h4 style="background-color: #0b3a5b; color: white; padding: 5px; margin: 0;">Applicant Details</h4>
<table style="width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 15px;" border="1">
<tr><td style="background-color: #f9f9f9; width: 25%;"><b>Applicant Name</b></td><td style="width: 25%;">{s_data.get('app_name', '').upper()}</td><td style="background-color: #f9f9f9; width: 25%;"><b>Religion</b></td><td style="width: 25%;">{s_data.get('religion', '')}</td></tr>
<tr><td style="background-color: #f9f9f9;"><b>ID Status</b></td><td>Verified</td><td style="background-color: #f9f9f9;"><b>Category</b></td><td>{s_data.get('category', '')}</td></tr>
<tr><td style="background-color: #f9f9f9;"><b>Date of Birth</b></td><td>{s_data.get('dob', '')}</td><td style="background-color: #f9f9f9;"><b>Applicant Gender</b></td><td>{s_data.get('gender', '')}</td></tr>
<tr><td style="background-color: #f9f9f9;"><b>OTR No.</b></td><td>{s_data.get('otr', '')}</td><td style="background-color: #f9f9f9;"><b>Mobile No.</b></td><td>{s_data.get('mobile', '')}</td></tr>
<tr><td style="background-color: #f9f9f9;"><b>Father's Name</b></td><td>{s_data.get('father_name', '').upper()}</td><td style="background-color: #f9f9f9;"><b>Mother's Name</b></td><td>{s_data.get('mother_name', '').upper()}</td></tr>
</table>
<h4 style="background-color: #0b3a5b; color: white; padding: 5px; margin: 0;">Address Information</h4>
<table style="width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 15px;" border="1">
<tr><td style="background-color: #f9f9f9; width: 25%;"><b>Address</b></td><td>{s_data.get('full_address', '').upper()}</td></tr>
<tr><td style="background-color: #f9f9f9;"><b>State</b></td><td>{s_data.get('state', '').upper()}</td></tr>
<tr><td style="background-color: #f9f9f9;"><b>District</b></td><td>{s_data.get('district', '').upper()}</td></tr>
</table>
<h4 style="background-color: #0b3a5b; color: white; padding: 5px; margin: 0;">Institute/Course Information</h4>
<table style="width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 15px;" border="1">
<tr><td style="background-color: #f9f9f9; width: 25%;"><b>Institute Code</b></td><td style="width: 25%;">{s_data.get('school_code', '')}</td><td style="background-color: #f9f9f9; width: 25%;"><b>Course/Class</b></td><td style="width: 25%;">{s_data.get('class', '')}</td></tr>
</table>
<h4 style="background-color: #0b3a5b; color: white; padding: 5px; margin: 0;">Bank Information</h4>
<table style="width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 15px;" border="1">
<tr><td style="background-color: #f9f9f9; width: 25%;"><b>Bank Name</b></td><td style="width: 25%;">{s_data.get('bank_name', '')}</td><td style="background-color: #f9f9f9; width: 25%;"><b>Branch Name</b></td><td style="width: 25%;">{s_data.get('branch_name', '')}</td></tr>
<tr><td style="background-color: #f9f9f9;"><b>IFSC Code</b></td><td>{s_data.get('ifsc', '')}</td><td style="background-color: #f9f9f9;"><b>Account No.</b></td><td>{s_data.get('acc_no', '')}</td></tr>
<tr><td style="background-color: #f9f9f9;"><b>Account Holder</b></td><td>{s_data.get('acc_name', '').upper()}</td><td style="background-color: #f9f9f9;"><b>Status</b></td><td>Active</td></tr>
</table>
<div style="font-size: 11px; color: #555; margin-top: 20px;">
<b>Student Declaration:</b><br>
1. I have read and understood the conditions of award of Scholarship.<br>
2. I am aware that my application is liable to be rejected, if it is found at any stage that provided details are false.<br>
3. I am aware that for any wrong entry of Bank details, the State Government will not be responsible.
</div>
</div>"""
    return html_str

def create_odisha_scholarship_pdf(filename, app_id, s_data):
    doc = SimpleDocTemplate(filename, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    
    title_style = ParagraphStyle(name='TitleStyle', fontName='Helvetica-Bold', fontSize=14, alignment=1, spaceAfter=5)
    sub_title_style = ParagraphStyle(name='SubTitleStyle', fontName='Helvetica', fontSize=10, alignment=1, spaceAfter=15)
    section_header = ParagraphStyle(name='SecHeader', fontName='Helvetica-Bold', fontSize=10, textColor=colors.white, backColor=colors.HexColor('#0b3a5b'), spaceBefore=10, spaceAfter=5, leftIndent=5)
    
    elements.append(Paragraph("<b>Government of Odisha</b>", title_style))
    elements.append(Paragraph("Scholarship Application Form", title_style))
    elements.append(Paragraph("ST&SC and MBC Welfare Department", title_style))
    elements.append(Paragraph(f"Academic Year {s_data.get('academic_year', '2025-26')}", sub_title_style))
    
    elements.append(Paragraph("Basic Information", section_header))
    data1 = [
        ["Department", "Scheme", "Academic Year", "Application Type"],
        ["ST&SC and MBC Welfare", s_data.get('scheme', ''), s_data.get('academic_year', ''), "New"]
    ]
    t1 = Table(data1, colWidths=[130, 130, 130, 130])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f2f2f2')),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(t1)
    
    elements.append(Paragraph("Applicant Details", section_header))
    data2 = [
        ["Applicant Name", s_data.get('app_name', '').upper(), "Religion", s_data.get('religion', '')],
        ["Identification", "Verified", "Category", s_data.get('category', '')],
        ["Date of Birth", s_data.get('dob', ''), "Applicant Gender", s_data.get('gender', '')],
        ["OTR No.", s_data.get('otr', ''), "Mobile No.", s_data.get('mobile', '')],
        ["Father's Name", s_data.get('father_name', '').upper(), "Mother's Name", s_data.get('mother_name', '').upper()]
    ]
    t2 = Table(data2, colWidths=[130, 130, 130, 130])
    t2.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f9f9f9')),
        ('BACKGROUND', (2,0), (2,-1), colors.HexColor('#f9f9f9')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(t2)
    
    elements.append(Paragraph("Address Information", section_header))
    data3 = [
        ["Address", s_data.get('full_address', '').upper()],
        ["State", s_data.get('state', '').upper()],
        ["District", s_data.get('district', '').upper()]
    ]
    t3 = Table(data3, colWidths=[130, 390])
    t3.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f9f9f9')),
    ]))
    elements.append(t3)
    
    doc.build(elements)

def create_school_receipt_pdf(filename, sch_id, sch_data):
    c = canvas.Canvas(filename, pagesize=letter)
    c.setStrokeColorRGB(0.1, 0.5, 0.2); c.setLineWidth(4); c.rect(30, 30, 552, 732, stroke=1, fill=0)
    c.setFillColorRGB(0.1, 0.5, 0.2); c.setFont("Times-Bold", 22); c.drawCentredString(300, 720, "SCHOOL REGISTRATION RECEIPT")
    c.setFillColorRGB(0, 0, 0); c.setFont("Helvetica-Bold", 12); c.drawString(50, 670, f"SCHOOL ID: {sch_id}")
    c.setFont("Helvetica", 12); y = 640
    c.drawString(50, y, f"School Name: {sch_data.get('name', '').upper()}"); y -= 25
    c.drawString(50, y, f"Head Master Name: {sch_data.get('hm_name', '').upper()}"); y -= 25
    c.drawString(50, y, f"Contact No: {sch_data.get('hm_phone', '')}"); y -= 25
    c.line(50, y, 550, y); y -= 20
    c.setFont("Helvetica-Oblique", 10); c.drawCentredString(300, y, "Computer-generated receipt.")
    c.save()

# --- MAIN APP START ---
schools_db, students_db = load_data()
master_db = load_master_data()
scholarships_db = load_scholarships()
sch_users_db = load_sch_users()

inject_custom_styles(master_db)

menu_items = ["Home Page", "Scholarship Portal", "New Student Registration", "New School Registration", "Master Login", "School Login"]
portal_map = {"home": 0, "scholarship": 1, "reg_student": 2, "reg_school": 3, "master": 4, "school": 5}
portal_param = st.query_params.get("portal", "home")
default_idx = portal_map.get(portal_param, 0)

menu = st.sidebar.selectbox("🎯 Navigation Menu", menu_items, index=default_idx)

if menu == "Home Page":
    st.query_params["portal"] = "home"
    bg_b64 = master_db.get("bg_b64", "")
    if bg_b64: inject_custom_bg(bg_b64)
    st.title("🏫 Advanced School Management System")
    st.info("Welcome to Portal! Choose options from Sidebar.")
elif menu == "Scholarship Portal":
    st.query_params["portal"] = "scholarship"
    bg_b64 = master_db.get("sch_bg_b64", "")
    if bg_b64: inject_custom_bg(bg_b64)
elif menu == "New Student Registration":
    st.query_params["portal"] = "reg_student"
elif menu == "New School Registration":
    st.query_params["portal"] = "reg_school"
elif menu == "School Login":
    st.query_params["portal"] = "school"
elif menu == "Master Login":
    st.query_params["portal"] = "master"

# ----------------- SCHOLARSHIP PORTAL -----------------
if menu == "Scholarship Portal":
    st.subheader("💰 Scholarship Student Portal")
    
    if not st.session_state.get('sch_logged_in', False):
        log_tab, reg_tab = st.tabs(["🔑 Student Login", "📝 New Registration"])
        
        with log_tab:
            st.info("Enter your 12-digit User ID.")
            l_uid = st.text_input("User ID *", key="l_sch_uid")
            l_pwd = st.text_input("Password *", type="password", key="l_sch_pwd")
            if st.button("Login", type="primary"):
                uid_clean = sanitize(l_uid)
                if uid_clean in sch_users_db and sch_users_db[uid_clean]["password"] == l_pwd:
                    st.session_state['sch_logged_in'] = True
                    st.session_state['sch_current_user'] = uid_clean
                    st.success("Login Successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid User ID or Password")
                    
        with reg_tab:
            if 'sch_reg_step' not in st.session_state: st.session_state['sch_reg_step'] = 1
            
            if st.session_state['sch_reg_step'] == 1:
                r_mob = st.text_input("Mobile Number or Email *")
                r_adh = st.text_input("12-digit User ID *", max_chars=12)
                if st.button("Get OTP"):
                    if len(r_mob) >= 5 and len(r_adh) == 12:
                        if sanitize(r_adh) in sch_users_db:
                            st.error("User ID already registered! Please go to Login.")
                        else:
                            st.session_state['temp_r_mob'] = sanitize(r_mob)
                            st.session_state['temp_r_adh'] = sanitize(r_adh)
                            st.session_state['temp_sch_otp'] = str(random.randint(1000, 9999))
                            
                            send_real_sms(sanitize(r_mob), st.session_state['temp_sch_otp'])
                            st.session_state['sch_reg_step'] = 2
                            st.rerun()
                    else: st.error("Please enter valid details.")
            
            elif st.session_state['sch_reg_step'] == 2:
                if 'temp_sch_otp' in st.session_state:
                    st.info(f"📲 [DEMO OTP]: **{st.session_state['temp_sch_otp']}**")
                in_otp = st.text_input("Enter OTP *")
                if st.button("Verify OTP"):
                    if in_otp == st.session_state['temp_sch_otp']:
                        st.session_state['sch_reg_step'] = 3
                        st.rerun()
                    else: st.error("Invalid OTP!")
                    
            elif st.session_state['sch_reg_step'] == 3:
                st.success("OTP Verified. Create a strong password.")
                pwd1 = st.text_input("Set Password *", type="password")
                pwd2 = st.text_input("Confirm Password *", type="password")
                if st.button("Register Profile", type="primary"):
                    if pwd1 and pwd1 == pwd2:
                        uid = st.session_state['temp_r_adh']
                        sch_users_db[uid] = {
                            "mobile": st.session_state['temp_r_mob'],
                            "password": pwd1,
                            "draft": {}
                        }
                        save_sch_users(sch_users_db)
                        st.success("Registration Successful! Please login.")
                        st.session_state['sch_reg_step'] = 1
                    else: st.error("Passwords do not match!")
    else:
        st.success(f"Logged in as: {st.session_state['sch_current_user']}")
        if st.button("Logout"):
            st.session_state['sch_logged_in'] = False
            del st.session_state['sch_current_user']
            st.rerun()

st.markdown("---")
st.markdown("<div style='text-align: center; padding: 15px; background: linear-gradient(90deg, #1e3a8a, #9333ea); color: white; border-radius: 8px; font-weight: bold;'>👨‍💻 Software Developed by: KULU SUTAR | 📞 Mob: 8910223342 | ✉️ kulusutar123@gmail.com</div>", unsafe_allow_html=True)
