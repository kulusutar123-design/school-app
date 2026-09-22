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
        st.error("🚨 Blocked due to repeated failed attempts. Too many wrong passwords entered.")
        st.stop()

# ==========================================
# 📱 WHATSAPP & SCREEN OTP GATEWAY
# ==========================================
def send_real_sms(mobile_or_email, otp_code, student_name="Student"):
    target = str(mobile_or_email).strip()
    
    clean_mob = "".join([c for c in target if c.isdigit()])
    if len(clean_mob) == 10:
        clean_mob = "91" + clean_mob
        
    message = f"Hello {student_name}, your Registration/Login OTP for School Management System is: *{otp_code}*."
    encoded_msg = urllib.parse.quote(message)
    wa_link = f"https://api.whatsapp.com/send?phone={clean_mob}&text={encoded_msg}"
    
    st.session_state['latest_otp'] = otp_code
    st.session_state['whatsapp_link'] = wa_link
    
    st.success(f"✅ OTP Generated for: **{target}**")
    if len(clean_mob) >= 10:
        st.markdown(f"<a href='{wa_link}' target='_blank' style='background-color:#25D366; color:white; padding:10px 20px; border-radius:6px; text-decoration:none; font-weight:bold; display:inline-block; margin-bottom:10px;'>💬 Send OTP via WhatsApp</a>", unsafe_allow_html=True)
    st.info(f"📲 **[DIRECT SCREEN OTP]**: Use OTP code: **{otp_code}**")
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
        "notice_text": "📢 Notice: Online registration, scholarship, and result portal active! | Helpdesk: 8910223342",
        "news_text": "🔴 Breaking News: Digital classes and new scholarship guidelines announced!",
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
        except Exception:
            return default_master
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
        except Exception:
            pass
    if os.path.exists(STUDENTS_FILE):
        try:
            with open(STUDENTS_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if content.strip(): students = json.loads(content)
        except Exception:
            pass
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
            pass
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
            pass
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
    masked_adh = "[Aadhaar Redacted]"
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
<tr><td style="background-color: #f9f9f9;"><b>ID Status</b></td><td>{masked_adh}</td><td style="background-color: #f9f9f9;"><b>Category</b></td><td>{s_data.get('category', '')}</td></tr>
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
<tr><td style="background-color: #f9f9f9;"><b>Account Holder</b></td><td>{s_data.get('acc_name', '').upper()}</td><td style="background-color: #f9f9f9;"><b>Seeded</b></td><td>Yes</td></tr>
</table>
</div>"""
    return html_str

def create_odisha_scholarship_pdf(filename, app_id, s_data):
    doc = SimpleDocTemplate(filename, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    
    title_style = ParagraphStyle(name='TitleStyle', fontName='Helvetica-Bold', fontSize=14, alignment=1, spaceAfter=5)
    section_header = ParagraphStyle(name='SecHeader', fontName='Helvetica-Bold', fontSize=10, textColor=colors.white, backColor=colors.HexColor('#0b3a5b'), spaceBefore=10, spaceAfter=5, leftIndent=5)
    
    elements.append(Paragraph("<b>Government of Odisha</b>", title_style))
    elements.append(Paragraph("Scholarship Application Form", title_style))
    
    elements.append(Paragraph("Applicant Details", section_header))
    masked_adh = "[Aadhaar Redacted]"
    
    data2 = [
        ["Applicant Name", s_data.get('app_name', '').upper(), "Religion", s_data.get('religion', '')],
        ["Identity", masked_adh, "Category", s_data.get('category', '')],
        ["Date of Birth", s_data.get('dob', ''), "Gender", s_data.get('gender', '')],
        ["OTR No.", s_data.get('otr', ''), "Mobile", s_data.get('mobile', '')]
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
    doc.build(elements)

def create_school_receipt_pdf(filename, sch_id, sch_data):
    c = canvas.Canvas(filename, pagesize=letter)
    c.setStrokeColorRGB(0.1, 0.5, 0.2); c.setLineWidth(4); c.rect(30, 30, 552, 732, stroke=1, fill=0)
    c.setFillColorRGB(0.1, 0.5, 0.2); c.setFont("Times-Bold", 22); c.drawCentredString(300, 720, "SCHOOL REGISTRATION RECEIPT")
    c.setFillColorRGB(0, 0, 0); c.setFont("Helvetica-Bold", 12); c.drawString(50, 670, f"SCHOOL ID: {sch_id}")
    c.setFont("Helvetica", 12); y = 640
    c.drawString(50, y, f"School Name: {sch_data.get('name', '').upper()}"); y -= 25
    c.drawString(50, y, f"Head Master: {sch_data.get('hm_name', '').upper()}"); y -= 25
    c.drawString(50, y, f"Contact No: {sch_data.get('hm_phone', '')}"); y -= 25
    c.save()

def generate_result_card_html(school_name_en, school_name_loc, st_data, roll_no, s_lang):
    disp_dob = format_display_date(st_data.get('dob', ''))
    tot_obt = st_data.get('total_obt', 0)
    w_tot_en = number_to_words(tot_obt)
    s_name_en = st_data.get('name', 'N/A').upper()
    b_col = "#963f98"
    
    html_str = f"""<div style='font-family: serif; border: 2px solid {b_col}; padding: 25px; background-color: #fef9f7;'>
<div style='text-align: center; color: {b_col};'>
<h1 style='margin: 0;'>{school_name_en}</h1>
<h3>ANNUAL EXAMINATION - {st_data.get('batch', '2025-2026')}</h3>
<p style='font-weight: bold; text-decoration: underline;'>CERTIFICATE-CUM-MARK SHEET</p>
</div>
<table style='width: 100%; font-size: 14px; margin-top: 15px;'>
<tr><td><b>NAME:</b> {s_name_en}</td><td><b>ROLL NO:</b> {roll_no}</td></tr>
<tr><td><b>DOB:</b> {disp_dob}</td><td><b>CLASS:</b> {st_data.get('class', '')}</td></tr>
<tr><td><b>TOTAL MARKS:</b> {tot_obt}</td><td><b>GRADE:</b> {st_data.get('grade', '')}</td></tr>
</table>
<div style='text-align: center; margin-top: 15px;'><b>( {w_tot_en} )</b></div>
</div>"""
    return html_str

def create_pdf(filename, school_name, st_data, roll_no):
    disp_dob = format_display_date(st_data.get('dob', ''))
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFillColorRGB(0.59, 0.25, 0.60)
    c.setFont("Times-Bold", 18); c.drawCentredString(300, 720, school_name.upper())
    c.setFont("Helvetica-Bold", 12); c.drawCentredString(300, 695, "ANNUAL EXAMINATION")
    c.drawString(50, 635, f"ROLL NO: {roll_no}")
    c.drawString(50, 600, f"NAME: {st_data.get('name', '').upper()}")
    c.drawString(50, 565, f"DOB: {disp_dob}")
    c.drawString(50, 530, f"TOTAL MARKS: {st_data.get('total_obt', 0)}")
    c.drawString(50, 495, f"GRADE: {st_data.get('grade', '')}")
    c.save()

# --- MAIN APP START ---
schools_db, students_db = load_data()
master_db = load_master_data()
scholarships_db = load_scholarships()
sch_users_db = load_sch_users()

inject_custom_styles(master_db)

menu_items = ["Home Page", "Scholarship Portal", "New Student Registration", "New School Registration", "Master Login", "School Login", "Results"]
portal_map = {"home": 0, "scholarship": 1, "reg_student": 2, "reg_school": 3, "master": 4, "school": 5, "student": 6}
portal_param = st.query_params.get("portal", "home")
default_idx = portal_map.get(portal_param, 0)

menu = st.sidebar.selectbox("🎯 Navigation Menu", menu_items, index=default_idx)

if menu == "Home Page":
    st.query_params["portal"] = "home"
elif menu == "Scholarship Portal":
    st.query_params["portal"] = "scholarship"
elif menu == "New Student Registration":
    st.query_params["portal"] = "reg_student"
elif menu == "New School Registration":
    st.query_params["portal"] = "reg_school"
elif menu == "School Login":
    st.query_params["portal"] = "school"
elif menu == "Master Login":
    st.query_params["portal"] = "master"
elif menu == "Results":
    st.query_params["portal"] = "student"

classes_list = [str(i) for i in range(1, 11)]
batches_list = [f"{y}-{y+1}" for y in range(2020, 2051)]

# ----------------- HOME PAGE -----------------
if menu == "Home Page":
    st.markdown("""
    <div style='background: rgba(15, 23, 42, 0.85); padding: 25px; border-radius: 12px; border: 2px solid #38bdf8; text-align: center; color: white;'>
        <h2>🏫 Welcome to Advanced School Management System</h2>
        <p style='color: #fbbf24; font-size: 18px;'>Connecting Students, Teachers & Administration Seamlessly</p>
    </div>
    <br>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1: 
        st.markdown("<a href='?portal=scholarship' target='_self' style='display:block; padding:20px; background:#fff; border-radius:8px; border:1px solid #cbd5e1; text-align:center; text-decoration:none;'><h3>💰 Scholarship Portal</h3><p style='color:#64748b;'>Apply Now</p></a><br>", unsafe_allow_html=True)
        st.markdown("<a href='?portal=master' target='_self' style='display:block; padding:20px; background:#fff; border-radius:8px; border:1px solid #cbd5e1; text-align:center; text-decoration:none;'><h3>🏛️ Master Login</h3><p style='color:#64748b;'>Admin Portal</p></a>", unsafe_allow_html=True)
    with c2: 
        st.markdown("<a href='?portal=reg_student' target='_self' style='display:block; padding:20px; background:#fff; border-radius:8px; border:1px solid #cbd5e1; text-align:center; text-decoration:none;'><h3>👨‍🎓 New Student Reg.</h3><p style='color:#64748b;'>Apply for admission</p></a><br>", unsafe_allow_html=True)
        st.markdown("<a href='?portal=school' target='_self' style='display:block; padding:20px; background:#fff; border-radius:8px; border:1px solid #cbd5e1; text-align:center; text-decoration:none;'><h3>🏫 School Login</h3><p style='color:#64748b;'>School Portal</p></a>", unsafe_allow_html=True)
    with c3: 
        st.markdown("<a href='?portal=reg_school' target='_self' style='display:block; padding:20px; background:#fff; border-radius:8px; border:1px solid #cbd5e1; text-align:center; text-decoration:none;'><h3>🏫 New School Reg.</h3><p style='color:#64748b;'>Register institution</p></a><br>", unsafe_allow_html=True)
        st.markdown("<a href='?portal=student' target='_self' style='display:block; padding:20px; background:#fff; border-radius:8px; border:1px solid #cbd5e1; text-align:center; text-decoration:none;'><h3>🎓 Check Results</h3><p style='color:#64748b;'>Download Rank Card</p></a>", unsafe_allow_html=True)

# ----------------- SCHOLARSHIP PORTAL -----------------
elif menu == "Scholarship Portal":
    c_h, c_t = st.columns([1, 8])
    with c_h:
        if st.button("🏠 Home", key="sch_home"): st.query_params["portal"] = "home"; st.rerun()
    with c_t: st.subheader("💰 Scholarship Student Portal")
    
    sch_fee = float(master_db.get("scholarship_fee", 50.0))

    if not st.session_state.get('sch_logged_in', False):
        log_tab, reg_tab = st.tabs(["🔑 Student Login", "📝 New Registration"])
        
        with log_tab:
            stu_log_mode = st.radio("Choose Action", ["Login", "Forgot Password"], key="stu_log_mode")
            if stu_log_mode == "Login":
                check_brute_force()
                l_uid = st.text_input("User ID *", key="l_sch_uid")
                l_pwd = st.text_input("Password *", type="password", key="l_sch_pwd")
                if st.button("Login", type="primary"):
                    uid_clean = sanitize(l_uid)
                    if uid_clean in sch_users_db and sch_users_db[uid_clean]["password"] == l_pwd:
                        st.session_state.failed_logins = 0
                        st.session_state['sch_logged_in'] = True
                        st.session_state['sch_current_user'] = uid_clean
                        st.success("Login Successful!")
                        st.rerun()
                    else:
                        st.session_state.failed_logins += 1
                        st.error("❌ Invalid User ID or Password")
            elif stu_log_mode == "Forgot Password":
                f_uid = st.text_input("Enter your User ID", key="f_sch_uid")
                if st.button("Send OTP", key="f_sch_send"):
                    if sanitize(f_uid) in sch_users_db:
                        otp_code = str(random.randint(1000, 9999))
                        st.session_state['sch_f_otp'] = otp_code
                        st.session_state['sch_f_uid'] = sanitize(f_uid)
                        reg_mob = sch_users_db[sanitize(f_uid)]["mobile"]
                        send_real_sms(reg_mob, otp_code)
                    else:
                        st.error("User ID not found in records!")
                        
                if 'sch_f_otp' in st.session_state:
                    entered_otp = st.text_input("Enter 4-digit OTP", key="f_sch_otp_inp")
                    if st.button("Verify OTP", key="f_sch_ver"):
                        if entered_otp == st.session_state['sch_f_otp']:
                            st.success("OTP Verified! You can now reset your password.")
                            st.session_state['sch_otp_verified'] = True
                        else:
                            st.error("Invalid OTP!")
                            
                if st.session_state.get('sch_otp_verified', False):
                    new_s_pass = st.text_input("New Password", type="password", key="f_sch_np")
                    c_s_pass = st.text_input("Confirm New Password", type="password", key="f_sch_cnp")
                    if st.button("Save New Password", key="f_sch_save"):
                        if new_s_pass and new_s_pass == c_s_pass:
                            target_uid = st.session_state['sch_f_uid']
                            sch_users_db[target_uid]["password"] = new_s_pass
                            save_sch_users(sch_users_db)
                            st.success("Password successfully updated! Please switch to 'Login'.")
                            del st.session_state['sch_f_otp']
                            del st.session_state['sch_otp_verified']
                            del st.session_state['sch_f_uid']
                        else:
                            st.error("Passwords do not match!")
                    
        with reg_tab:
            if 'sch_reg_step' not in st.session_state: st.session_state['sch_reg_step'] = 1
            
            if st.session_state['sch_reg_step'] == 1:
                r_mob = st.text_input("Mobile Number or Email *", key="r_mob_input")
                r_adh = st.text_input("12-digit User / Registration ID *", max_chars=12, key="r_adh_input")
                if st.button("Get OTP", key="sch_get_otp_btn"):
                    if len(r_mob) >= 5 and len(r_adh) == 12:
                        if sanitize(r_adh) in sch_users_db:
                            st.error("ID already registered! Please go to Login.")
                        else:
                            gen_otp = str(random.randint(1000, 9999))
                            st.session_state['temp_r_mob'] = sanitize(r_mob)
                            st.session_state['temp_r_adh'] = sanitize(r_adh)
                            st.session_state['temp_sch_otp'] = gen_otp
                            
                            send_real_sms(sanitize(r_mob), gen_otp)
                            st.session_state['sch_reg_step'] = 2
                            st.rerun()
                    else: 
                        st.error("Please enter valid Mobile/Email and 12-digit ID.")
            
            elif st.session_state['sch_reg_step'] == 2:
                st.info(f"Target: **{st.session_state.get('temp_r_mob')}**")
                if 'whatsapp_link' in st.session_state:
                    st.markdown(f"<a href='{st.session_state['whatsapp_link']}' target='_blank' style='background-color:#25D366; color:white; padding:8px 16px; border-radius:5px; text-decoration:none; font-weight:bold; display:inline-block; margin-bottom:10px;'>💬 Send OTP via WhatsApp</a>", unsafe_allow_html=True)
                if 'latest_otp' in st.session_state:
                    st.info(f"📲 Direct OTP: **{st.session_state['latest_otp']}**")
                
                in_otp = st.text_input("Enter OTP *", key="verify_otp_sch_inp")
                col_v1, col_v2 = st.columns(2)
                with col_v1:
                    if st.button("Verify OTP", type="primary", key="btn_verify_otp_sch"):
                        if in_otp == st.session_state['temp_sch_otp']:
                            st.session_state['sch_reg_step'] = 3
                            st.rerun()
                        else: 
                            st.error("Invalid OTP!")
                with col_v2:
                    if st.button("⬅️ Change Number/Email", key="btn_change_num_sch"):
                        st.session_state['sch_reg_step'] = 1
                        st.rerun()
                    
            elif st.session_state['sch_reg_step'] == 3:
                st.success("OTP Verified! Set your account password.")
                pwd1 = st.text_input("Set Password *", type="password", key="sch_pwd1")
                pwd2 = st.text_input("Confirm Password *", type="password", key="sch_pwd2")
                if st.button("Register & Create Profile", type="primary", key="sch_reg_done"):
                    if pwd1 and pwd1 == pwd2:
                        uid = st.session_state['temp_r_adh']
                        sch_users_db[uid] = {
                            "mobile": st.session_state['temp_r_mob'],
                            "password": pwd1,
                            "draft": {}
                        }
                        save_sch_users(sch_users_db)
                        st.success("Registration Successful! Please login with your ID.")
                        st.session_state['sch_reg_step'] = 1
                        st.rerun()
                    else: st.error("Passwords do not match!")

    else:
        cur_uid = st.session_state['sch_current_user']
        user_profile = sch_users_db[cur_uid]
        draft_data = user_profile.get("draft", {})
        
        c_dash1, c_dash2 = st.columns([8, 2])
        c_dash1.success(f"Welcome Student! User ID: {cur_uid}")
        if c_dash2.button("🔴 Logout"):
            st.session_state['sch_logged_in'] = False
            del st.session_state['sch_current_user']
            st.rerun()
            
        existing_app_id = None
        existing_app_data = None
        for a_id, a_data in scholarships_db.items():
            if a_data.get("user_id") == cur_uid:
                existing_app_id = a_id
                existing_app_data = a_data
                break
                
        if existing_app_id:
            st.warning("You have already submitted your scholarship application.")
            st.markdown(render_odisha_scholarship_html(existing_app_id, existing_app_data), unsafe_allow_html=True)
        else:
            st.info("Fill out your Scholarship Application details below.")
            with st.form("sch_main_form"):
                app_name = st.text_input("Applicant Name *", value=draft_data.get("app_name", ""))
                father_name = st.text_input("Father Name *", value=draft_data.get("father_name", ""))
                dob = st.text_input("Date of Birth (YYYY-MM-DD) *", value=draft_data.get("dob", ""))
                acc_no = st.text_input("Bank Account Number *", value=draft_data.get("acc_no", ""))
                ifsc = st.text_input("Bank IFSC Code *", value=draft_data.get("ifsc", ""))
                
                if st.form_submit_button("Submit Scholarship Application", type="primary"):
                    if not app_name or not acc_no:
                        st.error("Please fill mandatory fields.")
                    else:
                        app_id = "SCH" + str(random.randint(100000, 999999))
                        scholarships_db[app_id] = {
                            "user_id": cur_uid,
                            "app_name": sanitize(app_name),
                            "father_name": sanitize(father_name),
                            "dob": sanitize(dob),
                            "acc_no": sanitize(acc_no),
                            "ifsc": sanitize(ifsc),
                            "mobile": user_profile.get("mobile", ""),
                            "status": "Pending_Master",
                            "payment_mode": "Offline Verified"
                        }
                        save_scholarships(scholarships_db)
                        st.success("Scholarship submitted successfully!")
                        st.rerun()

# ----------------- NEW STUDENT REGISTRATION -----------------
elif menu == "New Student Registration":
    c_home, c_title = st.columns([1, 8])
    with c_home:
        if st.button("🏠 Home", key="reg_stu_home"): st.query_params["portal"] = "home"; st.rerun()
    with c_title: st.subheader("👨‍🎓 New Student Registration")

    with st.form("student_simple_reg"):
        stu_name = st.text_input("Student Name *")
        stu_phone = st.text_input("Mobile No *")
        stu_class = st.selectbox("Class", classes_list)
        if st.form_submit_button("Submit Registration", type="primary"):
            if not stu_name or not stu_phone:
                st.error("Please fill mandatory fields.")
            else:
                reg_id = "REG" + str(random.randint(100000, 999999))
                st.success(f"Registered successfully! Registration ID: **{reg_id}**")

# ----------------- NEW SCHOOL REGISTRATION -----------------
elif menu == "New School Registration":
    c_home, c_title = st.columns([1, 8])
    with c_home:
        if st.button("🏠 Home", key="reg_sch_home"): st.query_params["portal"] = "home"; st.rerun()
    with c_title: st.subheader("🏫 New School Registration")

    with st.form("sch_simple_reg"):
        s_id = st.text_input("School ID (Unique) *")
        s_name = st.text_input("School Name *")
        s_pass = st.text_input("Password *", type="password")
        if st.form_submit_button("Register School", type="primary"):
            if s_id and s_name and s_pass:
                schools_db[sanitize(s_id)] = {"name": sanitize(s_name), "pass": s_pass, "status": "Active"}
                save_data(schools_db, students_db)
                st.success("School registered successfully!")
            else:
                st.error("Please fill all fields.")

# ----------------- MASTER LOGIN -----------------
elif menu == "Master Login":
    c_home, c_title = st.columns([1, 8])
    with c_home:
        if st.button("🏠 Home", key="m_home_btn"): st.query_params["portal"] = "home"; st.rerun()
    with c_title: st.subheader("🔑 Master Administrator Portal")
    
    if not st.session_state.get('master_logged', False):
        m_user = st.text_input("Master Username")
        m_pass = st.text_input("Master Password", type="password")
        if st.button("Login", type="primary"):
            if sanitize(m_user) == master_db.get("username") and m_pass == master_db.get("password"):
                st.session_state['master_logged'] = True
                st.rerun()
            else: 
                st.error("Invalid Master ID or Password!")
    else:
        st.success("Welcome Master Admin!")
        if st.button("🔴 Logout"):
            st.session_state['master_logged'] = False
            st.rerun()

# ----------------- SCHOOL LOGIN -----------------
elif menu == "School Login":
    c_home, c_title = st.columns([1, 8])
    with c_home:
        if st.button("🏠 Home", key="s_home_btn"): st.query_params["portal"] = "home"; st.rerun()
    with c_title: st.subheader("🏫 School Portal")
    
    s_id = st.text_input("School ID")
    s_pass = st.text_input("School Password", type="password")
    if st.button("Login as School", type="primary"):
        clean_id = sanitize(s_id)
        if clean_id in schools_db and schools_db[clean_id].get("pass") == s_pass:
            st.success(f"Welcome {schools_db[clean_id].get('name')}!")
        else:
            st.error("Invalid School credentials.")

# ----------------- RESULTS PORTAL -----------------
elif menu == "Results":
    c_home, c_title = st.columns([1, 8])
    with c_home:
        if st.button("🏠 Home", key="st_home_btn"): st.query_params["portal"] = "home"; st.rerun()
    with c_title: st.subheader("🎓 Results Portal")
    
    st_roll = st.text_input("Roll Number")
    st_dob = st.text_input("Date of Birth (YYYY-MM-DD)")
    if st.button("View Result", type="primary"):
        st.info("No exam result record published for this roll number.")

st.markdown("---")
st.markdown("<div style='text-align: center; padding: 15px; background: linear-gradient(90deg, #1e3a8a, #9333ea); color: white; border-radius: 8px; font-weight: bold;'>👨‍💻 Software Developed by: KULU SUTAR | 📞 Mob: 8910223342 | ✉️ kulusutar123@gmail.com</div>", unsafe_allow_html=True)
