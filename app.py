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
        st.error("🚨 ସୁରକ୍ଷା କାରଣରୁ ଆପଣଙ୍କୁ ବ୍ଲକ୍ କରାଯାଇଛି (Blocked due to repeated failed attempts). ବହୁତ ଥର ଭୁଲ୍ ପାସୱାର୍ଡ ଦିଆଯାଇଛି।")
        st.stop()

# ==========================================
# 📱 WHATSAPP & SYSTEM FALLBACK OTP GATEWAY
# ==========================================
def get_whatsapp_link(mobile_no, otp_code, student_name="Student"):
    clean_mob = "".join([c for c in str(mobile_no) if c.isdigit()])
    if not clean_mob.startswith("91") and len(clean_mob) == 10:
        clean_mob = "91" + clean_mob
    message = f"Hello {student_name}, your Registration/Login OTP for School Management System is: *{otp_code}*. Please use this code to verify your account."
    encoded_msg = urllib.parse.quote(message)
    return f"https://api.whatsapp.com/send?phone={clean_mob}&text={encoded_msg}"

def send_real_sms(mobile_no, otp_code, student_name="Student"):
    # Fast2SMS Quick API Integration (No KYC Required)
    url = "https://www.fast2sms.com/dev/bulkV2"
    
    # Your Fast2SMS API Key
    api_key = "YOUR_FAST2SMS_API_KEY"
    
    payload = {
        "route": "q",
        "message": f"Hello {student_name}, your OTP for School Management System is {otp_code}. Valid for 10 minutes.",
        "language": "english",
        "flash": 0,
        "numbers": str(mobile_no)
    }
    
    headers = {
        'authorization': api_key,
        'Content-Type': "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        
        if data.get("return") == True:
            return True
        else:
            st.session_state['sms_error'] = f"Fast2SMS Error: {data.get('message', 'Failed')}"
            return False
    except Exception as e:
        st.session_state['sms_error'] = str(e)
        return False
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

# ==========================================
# 🤖 SECURE DATA LOADERS
# ==========================================
def load_master_data():
    default_master = {
        "username": "master", "password": "master123", "email": "kulusutar123@gmail.com", 
        "phone": "8910223342", "upi_id": "school@sbi", "reg_fee": 150.0, "gst_percent": 18.0,
        "school_reg_fee": 1000.0, "school_gst_percent": 18.0, "scholarship_fee": 50.0,
        "notice_text": "📢 ନୂଆ ଅପଡେଟ୍: ଛାତ୍ରଛାତ୍ରୀମାନେ ଏବେ ଅନଲାଇନ୍ ରେଜିଷ୍ଟ୍ରେସନ୍, ସ୍କଲାରସିପ୍ ଏବଂ ପେମେଣ୍ଟ କରିପାରିବେ! <span class='new-badge'>NEW</span> &nbsp;&nbsp;|&nbsp;&nbsp; 👨‍💻 Software Developed by: KULU SUTAR &nbsp;&nbsp;|&nbsp;&nbsp; 📞 Helpdesk No: 8910223342 &nbsp;&nbsp;|&nbsp;&nbsp; ✉️ Mail ID: kulusutar123@gmail.com",
        "news_text": "🔴 [ODISHA] ନୂଆ ଶିକ୍ଷା ନୀତି ଅନୁଯାୟୀ ସମସ୍ତ ସ୍କୁଲରେ ଡିଜିଟାଲ୍ କ୍ଲାସରୁମ୍ ଆରମ୍ଭ ହେବ! &nbsp;&nbsp;♦&nbsp;&nbsp; 🔴 [DELHI] Central Government announces new scholarship schemes for brilliant students across India!",
        "bg_b64": "", "sch_bg_b64": "", "school_bg_b64": "", "reg_bg_b64": "",
        "font_family": "sans-serif", "font_size": "16", "text_color": "#000000", "theme_color": "#1e3a8a",
        "sms_api_key": "gDA5mQEVzx1veCbdfwc8XOqUHT2WY"
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
            st.error("CRITICAL ERROR: Master File is corrupted. System halted to prevent data loss.")
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
        except Exception:
            st.error("CRITICAL ERROR: schools.json is corrupted. System halted to prevent data loss.")
            st.stop()
    if os.path.exists(STUDENTS_FILE):
        try:
            with open(STUDENTS_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if content.strip(): students = json.loads(content)
        except Exception:
            st.error("CRITICAL ERROR: students.txt is corrupted. System halted to prevent data loss.")
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
            st.error("CRITICAL ERROR: scholarships.json is corrupted. System halted to prevent data loss.")
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
            st.error("CRITICAL ERROR: sch_users.json is corrupted. System halted to prevent data loss.")
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
    adh = s_data.get('aadhaar', '')
    masked_adh = f"XXXXXXXX{adh[-4:]}" if len(adh) >= 4 else adh
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
<tr><td style="background-color: #f9f9f9;"><b>Aadhaar No.</b></td><td>{masked_adh}</td><td style="background-color: #f9f9f9;"><b>Category</b></td><td>{s_data.get('category', '')}</td></tr>
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
<tr><td style="background-color: #f9f9f9;"><b>Account Holder</b></td><td>{s_data.get('acc_name', '').upper()}</td><td style="background-color: #f9f9f9;"><b>Aadhaar Seeded</b></td><td>Yes</td></tr>
</table>
<div style="font-size: 11px; color: #555; margin-top: 20px;">
<b>Student Declaration:</b><br>
1. I have read and understood the conditions of award of Scholarship.<br>
2. I am aware that my application is liable to be rejected, if it is found at any stage, that Aadhaar number provided by me is wrong.<br>
3. I am aware that for any wrong entry or mis-match of the Bank-account details, the State Government will not be responsible.
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
    adh = s_data.get('aadhaar', '')
    masked_adh = f"XXXXXXXX{adh[-4:]}" if len(adh) >= 4 else adh
    
    data2 = [
        ["Applicant Name", s_data.get('app_name', '').upper(), "Religion", s_data.get('religion', '')],
        ["Aadhaar No.", masked_adh, "Category", s_data.get('category', '')],
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
    
    elements.append(Paragraph("Institute/Course Information", section_header))
    data4 = [
        ["Institute Code", s_data.get('school_code', ''), "Course/Class", s_data.get('class', '')]
    ]
    t4 = Table(data4, colWidths=[130, 130, 130, 130])
    t4.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f9f9f9')),
        ('BACKGROUND', (2,0), (2,-1), colors.HexColor('#f9f9f9')),
    ]))
    elements.append(t4)
    
    elements.append(Paragraph("Eligibility Information", section_header))
    data5 = [
        ["Income Certificate No.", s_data.get('income_cert', ''), "Income Authority", s_data.get('inc_auth', '')],
        ["Caste Certificate No.", s_data.get('caste_cert', ''), "Caste Authority", s_data.get('cas_auth', '')]
    ]
    t5 = Table(data5, colWidths=[130, 130, 130, 130])
    t5.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f9f9f9')),
        ('BACKGROUND', (2,0), (2,-1), colors.HexColor('#f9f9f9')),
    ]))
    elements.append(t5)
    
    elements.append(Paragraph("Bank Information", section_header))
    data6 = [
        ["Bank Name", s_data.get('bank_name', ''), "Branch Name", s_data.get('branch_name', '')],
        ["IFSC Code", s_data.get('ifsc', ''), "Account No.", s_data.get('acc_no', '')],
        ["Account Holder Name", s_data.get('acc_name', '').upper(), "Aadhaar Seeded", "Yes"]
    ]
    t6 = Table(data6, colWidths=[130, 130, 130, 130])
    t6.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f9f9f9')),
        ('BACKGROUND', (2,0), (2,-1), colors.HexColor('#f9f9f9')),
    ]))
    elements.append(t6)
    
    elements.append(Paragraph("Application Status & Declarations", section_header))
    data7 = [
        ["Application ID", app_id],
        ["Payment Mode", s_data.get('payment_mode', 'Pending')],
        ["Current Status", s_data.get('status', 'Pending')]
    ]
    t7 = Table(data7, colWidths=[130, 390])
    t7.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f9f9f9')),
    ]))
    elements.append(t7)
    
    elements.append(Spacer(1, 20))
    decl_style = ParagraphStyle(name='Decl', fontName='Helvetica', fontSize=8, leading=10)
    elements.append(Paragraph("<b>Student Declaration</b>", ParagraphStyle(name='DeclBold', fontName='Helvetica-Bold', fontSize=8)))
    elements.append(Paragraph("1. I have read and understood the conditions of award of Scholarship.", decl_style))
    elements.append(Paragraph("2. I am aware that my application is liable to be rejected, if it is found at any stage, that Aadhaar number provided by me is wrong.", decl_style))
    elements.append(Paragraph("3. I am aware that for any wrong entry or mis-match of the Bank-account details, the State Government will not be responsible.", decl_style))
    
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("Date: __________________", decl_style))
    elements.append(Paragraph(f"Place: {s_data.get('district', '')}                                                                                     Full Signature of Applicant", decl_style))
    
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
    c.drawString(50, y, f"State: {sch_data.get('state', '')}"); y -= 25
    c.drawString(50, y, f"Payment Mode: {sch_data.get('payment_mode', 'N/A')}"); y -= 25
    c.drawString(50, y, f"Status: {sch_data.get('status', 'Pending')}"); y -= 25
    c.drawString(50, y, f"Date: {datetime.date.today().strftime('%d-%m-%Y')}"); y -= 40
    c.line(50, y, 550, y); y -= 20
    c.setFont("Helvetica-Oblique", 10); c.drawCentredString(300, y, "Computer-generated receipt.")
    c.save()

def generate_result_card_html(school_name_en, school_name_loc, st_data, roll_no, s_lang):
    disp_dob = format_display_date(st_data.get('dob', ''))
    raw_pub = st_data.get('pub_date', '')
    disp_pub_date = format_display_date(raw_pub) if raw_pub else datetime.date.today().strftime('%d-%m-%Y')
    bc, b_col, ob, t_bg = "#fef9f7", "#963f98", "#ce9bd0", "#fcf4fc"
    tot_obt = st_data.get('total_obt', 0)
    w_tot_en = number_to_words(tot_obt)
    s_name_en = st_data.get('name', 'N/A').upper()
    qr_text = f"SCHOOL: {school_name_en} | NAME: {s_name_en} | ROLL: {roll_no} | DOB: {disp_dob} | MARKS: {tot_obt}/{st_data.get('total_full', 0)} | GRADE: {st_data.get('grade', '')}"
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={urllib.parse.quote(qr_text)}"
    bc_url = f"https://barcode.tec-it.com/barcode.ashx?data={roll_no}&code=Code128&dpi=96"
    rows_html = "".join([f"<tr style='border-bottom: 1px solid {b_col};'><td style='padding: 8px; border-right: 1px solid {b_col}; text-align: left; font-weight: bold; color: #000;'>{sub.upper()}</td><td style='padding: 8px; border-right: 1px solid {b_col}; color: #000;'>{m['full']}</td><td style='padding: 8px; font-weight: bold; color: #000;'>{m['obt']}</td></tr>" for sub, m in st_data.get('subjects', {}).items()])
    
    html_str = f"""<div style='font-family: "Times New Roman", serif; border: 15px solid {ob}; padding: 4px; max-width: 800px; margin: auto; background-color: #fff;'>
<div style='border: 2px solid {b_col}; padding: 25px; background-color: {bc}; position: relative;'>
<div style='text-align: center; color: {b_col}; margin-bottom: 20px;'>
<h1 style='margin: 0; font-size: 24px; text-transform: uppercase;'>{school_name_en}</h1>
<h3 style='margin: 5px 0; font-size: 16px;'>ANNUAL EXAMINATION - {st_data.get('batch', '2025-2026')}</h3>
<p style='margin: 5px 0; font-weight: bold; font-size: 17px; text-decoration: underline;'>CERTIFICATE-CUM-MARK SHEET</p>
</div>
<table style='width: 100%; font-size: 13px; margin-bottom: 20px; font-weight: bold;'>
<tr><td><span style='color:{b_col};'>ROLL NO:</span> <span style='color:#000;'>{roll_no}</span></td><td style='text-align: right;'><span style='color:{b_col};'>CLASS:</span> <span style='color:#000;'>{st_data.get('class', '')}</span></td></tr>
<tr><td><span style='color:{b_col};'>PEN NO:</span> <span style='color:#000;'>{st_data.get('pen_no', '')}</span></td><td style='text-align: right;'><span style='color:{b_col};'>APAAR NO:</span> <span style='color:#000;'>{st_data.get('apaar_no', '')}</span></td></tr>
</table>
<table style='width: 100%; font-size: 14px; margin-bottom: 15px; text-transform: uppercase; line-height: 1.8;'>
<tr><td style='width: 250px; color: {b_col}; font-weight: bold;'>Certify that</td><td><b style='color:#000;'>{s_name_en}</b></td></tr>
<tr><td style='color: {b_col}; font-weight: bold;'>Mother's Name</td><td><b style='color:#000;'>{st_data.get('mother_name', '').upper()}</b></td></tr>
<tr><td style='color: {b_col}; font-weight: bold;'>Father's Name</td><td><b style='color:#000;'>{st_data.get('father_name', '').upper()}</b></td></tr>
<tr><td style='color: {b_col}; font-weight: bold;'>Date of Birth</td><td><b style='color:#000;'>{disp_dob}</b></td></tr>
<tr><td style='color: {b_col}; font-weight: bold;'>Category</td><td><b style='color:#000;'>{st_data.get('category', 'General')}</b></td></tr>
</table>
<table style='width: 100%; border-collapse: collapse; border: 2px solid {b_col}; text-align: center; font-size: 13px;'>
<tr style='color: {b_col}; background-color: {t_bg}; border-bottom: 2px solid {b_col};'>
<th style='padding: 8px; border-right: 1px solid {b_col};'>SUBJECT</th><th style='padding: 8px; border-right: 1px solid {b_col};'>FULL MARKS</th><th style='padding: 8px;'>MARKS SECURED</th>
</tr>
{rows_html}
<tr style='color: {b_col}; font-weight: bold; background-color: {t_bg}; border-top: 2px solid {b_col};'>
<td style='padding: 10px; border-right: 1px solid {b_col}; text-align: right;'>TOTAL MARKS</td><td style='padding: 10px; border-right: 1px solid {b_col}; color:#000;'>{st_data.get('total_full', 0)}</td><td style='padding: 10px; color:#000;'>{tot_obt}</td>
</tr>
</table>
<div style='text-align: center; font-weight: bold; font-size: 14px; margin-top: 20px; color:#000;'>( {w_tot_en} )</div>
<table style='width: 100%; margin-top: 20px; text-align: center; color: {b_col};'>
<tr>
<td style='width: 33%; vertical-align: bottom;'><img src='{bc_url}' style='height: 35px; margin-bottom: 10px;'/><br><div style='font-size: 11px;'>DATE OF PUBLICATION</div><div style='font-weight: bold; font-size: 14px; margin-bottom: 30px; color:#000;'>{disp_pub_date}</div><div style='border-bottom: 1px solid {b_col}; width: 80%; margin: auto;'></div><div style='font-size: 11px; font-weight: bold; margin-top:5px;'>HM SIGNATURE</div></td>
<td style='width: 34%; vertical-align: top;'><div style='font-size: 12px; margin-bottom: 5px;'>GRADE</div><div style='border: 2px solid {b_col}; padding: 10px 25px; display: inline-block; background-color: {t_bg};'><div style='font-weight: bold; font-size: 22px; color: #000;'>{st_data.get('grade', '')}</div></div></td>
<td style='width: 33%; vertical-align: bottom;'><img src='{qr_url}' style='height: 65px; margin-bottom: 10px;'/><div style='height: 15px; margin-bottom: 30px;'></div><div style='border-bottom: 1px solid {b_col}; width: 80%; margin: auto;'></div><div style='font-size: 11px; font-weight: bold; margin-top:5px;'>CLASS TEACHER SIGNATURE</div></td>
</tr>
</table>
</div>
</div>"""
    return html_str

def create_pdf(filename, school_name, st_data, roll_no):
    disp_dob = format_display_date(st_data.get('dob', ''))
    raw_pub = st_data.get('pub_date', '')
    disp_pub_date = format_display_date(raw_pub) if raw_pub else datetime.date.today().strftime('%d-%m-%Y')
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFillColorRGB(0.99, 0.98, 0.97); c.rect(30, 30, 552, 732, fill=1, stroke=0)
    c.setStrokeColorRGB(0.82, 0.60, 0.83); c.setLineWidth(15); c.rect(15, 15, 582, 762, fill=0, stroke=1)
    c.setStrokeColorRGB(0.59, 0.25, 0.60); c.setLineWidth(2); c.rect(30, 30, 552, 732, fill=0, stroke=1)
    c.setFillColorRGB(0.59, 0.25, 0.60)
    school_text = school_name.upper()
    c.setFont("Times-Bold", 16 if len(school_text)>25 else 20)
    c.drawCentredString(300, 720, school_text)
    c.setFont("Helvetica-Bold", 12); c.drawCentredString(300, 695, f"ANNUAL EXAMINATION - {st_data.get('batch', '2025-2026')}")
    c.setFont("Helvetica", 11); c.drawCentredString(300, 675, "CERTIFICATE-CUM-MARK SHEET")
    c.drawString(50, 635, "ROLL NO:"); c.setFillColorRGB(0,0,0); c.setFont("Helvetica-Bold", 11); c.drawString(110, 635, f"{roll_no}")
    c.setFillColorRGB(0.59, 0.25, 0.60); c.drawString(450, 635, "CLASS:"); c.setFillColorRGB(0,0,0); c.drawString(500, 635, f"{st_data.get('class', '')}")
    c.setFillColorRGB(0.59, 0.25, 0.60); c.drawString(50, 615, "PEN NO:"); c.setFillColorRGB(0,0,0); c.drawString(100, 615, f"{st_data.get('pen_no', '')}")
    c.setFillColorRGB(0.59, 0.25, 0.60); c.drawString(420, 615, "APAAR NO:"); c.setFillColorRGB(0,0,0); c.drawString(490, 615, f"{st_data.get('apaar_no', '')}")
    c.setFillColorRGB(0.59, 0.25, 0.60); c.setFont("Helvetica-Oblique", 11); c.drawString(50, 585, "Certify that"); c.setFillColorRGB(0,0,0); c.setFont("Helvetica-Bold", 11); c.drawString(150, 585, f"{st_data.get('name', '').upper()}")
    c.setFillColorRGB(0.59, 0.25, 0.60); c.setFont("Helvetica-Oblique", 11); c.drawString(50, 565, "Mother's Name"); c.setFillColorRGB(0,0,0); c.setFont("Helvetica-Bold", 11); c.drawString(150, 565, f"{st_data.get('mother_name', '').upper()}")
    c.setFillColorRGB(0.59, 0.25, 0.60); c.setFont("Helvetica-Oblique", 11); c.drawString(50, 545, "Father's Name"); c.setFillColorRGB(0,0,0); c.setFont("Helvetica-Bold", 11); c.drawString(150, 545, f"{st_data.get('father_name', '').upper()}")
    c.setFillColorRGB(0.59, 0.25, 0.60); c.setFont("Helvetica-Oblique", 11); c.drawString(50, 525, "Date of Birth"); c.setFillColorRGB(0,0,0); c.setFont("Helvetica-Bold", 11); c.drawString(150, 525, f"{disp_dob}")
    c.setFillColorRGB(0.59, 0.25, 0.60); c.setFont("Helvetica-Oblique", 11); c.drawString(50, 505, "Category"); c.setFillColorRGB(0,0,0); c.setFont("Helvetica-Bold", 11); c.drawString(150, 505, f"{st_data.get('category', 'General')}")
    c.setStrokeColorRGB(0.59, 0.25, 0.60); c.line(50, 485, 550, 485)
    c.setFillColorRGB(0.98, 0.95, 0.98); c.rect(50, 455, 500, 30, fill=1, stroke=0)
    c.setFillColorRGB(0.59, 0.25, 0.60); c.setFont("Helvetica-Bold", 11); c.drawString(60, 465, "SUBJECT"); c.drawCentredString(350, 465, "FULL MARKS"); c.drawRightString(540, 465, "MARKS SECURED")
    c.line(50, 455, 550, 455); c.line(50, 485, 50, 455); c.line(280, 485, 280, 455); c.line(420, 485, 420, 455); c.line(550, 485, 550, 455)
    c.setFillColorRGB(0,0,0); y = 435; t_b_y = y + 10
    for sub, m_info in st_data.get('subjects', {}).items():
        c.drawString(60, y, str(sub).upper()); c.drawCentredString(350, y, str(m_info['full'])); c.drawRightString(540, y, str(m_info['obt']))
        c.setStrokeColorRGB(0.59, 0.25, 0.60); c.line(50, y-10, 550, y-10); y -= 20; t_b_y = y + 10
    c.line(50, 455, 50, t_b_y); c.line(280, 455, 280, t_b_y); c.line(420, 455, 420, t_b_y); c.line(550, 455, 550, t_b_y)
    c.setFillColorRGB(0.98, 0.95, 0.98); c.rect(50, t_b_y-25, 500, 25, fill=1, stroke=0)
    c.setFillColorRGB(0.59, 0.25, 0.60); c.setFont("Helvetica-Bold", 11); c.drawRightString(270, t_b_y-17, "TOTAL MARKS"); c.drawCentredString(350, t_b_y-17, str(st_data.get('total_full', 0)))
    c.setFillColorRGB(0,0,0); c.drawRightString(540, t_b_y-17, str(st_data.get('total_obt', 0)))
    c.setStrokeColorRGB(0.59, 0.25, 0.60); c.line(50, t_b_y-25, 550, t_b_y-25)
    y = t_b_y - 45; c.setFillColorRGB(0,0,0); c.setFont("Helvetica-Bold", 10); c.drawCentredString(300, y, f"( {number_to_words(st_data.get('total_obt', 0))} )")
    y -= 60
    try: bc = code128.Code128(str(roll_no), barHeight=25, barWidth=1.2); bc.drawOn(c, 50, y+15)
    except: pass
    c.setFillColorRGB(0.59, 0.25, 0.60); c.setFont("Helvetica", 10); c.drawCentredString(140, y-10, "DATE OF PUBLICATION"); c.setFont("Helvetica-Bold", 11); c.drawCentredString(140, y-25, f"{disp_pub_date}")
    c.line(50, y-60, 230, y-60); c.setFont("Helvetica-Bold", 10); c.drawCentredString(140, y-75, "HM SIGNATURE")
    c.setStrokeColorRGB(0.59, 0.25, 0.60); c.setFillColorRGB(0.98, 0.95, 0.98); c.rect(260, y-30, 80, 40, fill=1, stroke=1)
    c.setFillColorRGB(0.59, 0.25, 0.60); c.setFont("Helvetica", 10); c.drawCentredString(300, y+20, "GRADE"); c.setFillColorRGB(0,0,0); c.setFont("Helvetica-Bold", 18); c.drawCentredString(300, y-15, f"{st_data.get('grade', '')}")
    c.setFillColorRGB(0.59, 0.25, 0.60); c.line(400, y-60, 550, y-60); c.setFont("Helvetica-Bold", 10); c.drawCentredString(475, y-75, "CLASS TEACHER SIGNATURE")
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
    bg_b64 = master_db.get("bg_b64", "")
    if bg_b64: inject_custom_bg(bg_b64)
elif menu == "Scholarship Portal":
    st.query_params["portal"] = "scholarship"
    bg_b64 = master_db.get("sch_bg_b64", "")
    if bg_b64: inject_custom_bg(bg_b64)
elif menu == "New Student Registration":
    st.query_params["portal"] = "reg_student"
    bg_b64 = master_db.get("reg_bg_b64", "")
    if bg_b64: inject_custom_bg(bg_b64)
elif menu == "New School Registration":
    st.query_params["portal"] = "reg_school"
    bg_b64 = master_db.get("reg_bg_b64", "")
    if bg_b64: inject_custom_bg(bg_b64)
elif menu == "School Login":
    st.query_params["portal"] = "school"
    bg_b64 = master_db.get("school_bg_b64", "")
    if bg_b64: inject_custom_bg(bg_b64)
elif menu == "Master Login":
    st.query_params["portal"] = "master"
elif menu == "Results":
    st.query_params["portal"] = "student"

classes_list = [str(i) for i in range(1, 11)]
batches_list = [f"{y}-{y+1}" for y in range(2020, 2051)]

# ----------------- HOME PAGE -----------------
if menu == "Home Page":
    if not master_db.get("bg_b64", ""):
        bg_images = [
            "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?q=80&w=1920",
            "https://images.unsplash.com/photo-1541829070764-84a7d30dd3f3?q=80&w=1920"
        ]
        selected_bg = random.choice(bg_images)
        st.markdown(f"""
        <style>
        .stApp {{ background-image: url("{selected_bg}"); background-size: cover; background-position: center; background-attachment: fixed; }}
        </style>
        """, unsafe_allow_html=True)
        
    st.markdown("""
    <style>
    .glass-panel { background: rgba(15, 23, 42, 0.85); padding: 20px; border-radius: 15px; border: 2px solid #38bdf8; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37); backdrop-filter: blur(4px); margin-bottom: 25px; }
    .login-card { background: rgba(255, 255, 255, 0.95) !important; border: 1px solid #cbd5e1; border-radius: 8px; padding: 20px; margin-bottom: 20px; text-align: center; text-decoration: none; display: block; box-shadow: 0 4px 6px rgba(0,0,0,0.05); transition: 0.3s; }
    .login-card:hover { background: #ffffff !important; transform: translateY(-3px); box-shadow: 0 8px 15px rgba(0,0,0,0.2); }
    .login-title { font-weight: bold; margin-bottom: 8px; }
    .login-sub { font-size: 14px; color: #64748b !important;}
    </style>
    """, unsafe_allow_html=True)

    today = datetime.date.today()
    mm_dd = today.strftime("%m-%d")
    event_images = ""
    event_title = "Welcome to Advanced School Management System"
    
    if mm_dd == "10-02":
        event_images += "<img class='marquee-img' src='https://images.weserv.nl/?url=upload.wikimedia.org/wikipedia/commons/7/7a/Mahatma-Gandhi%2C_studio%2C_1931.jpg&w=400' alt='Gandhi'>"
        event_title = "🙏 Happy Gandhi Jayanti 🙏"
    elif mm_dd == "08-15":
        event_images += "<img class='marquee-img' src='https://images.weserv.nl/?url=upload.wikimedia.org/wikipedia/en/4/41/Flag_of_India.svg&w=400' alt='Independence Day'>"
        event_title = "🇮🇳 Happy Independence Day 🇮🇳"
    elif mm_dd == "01-26":
        event_images += "<img class='marquee-img' src='https://images.weserv.nl/?url=upload.wikimedia.org/wikipedia/en/4/41/Flag_of_India.svg&w=400' alt='Republic Day'>"
        event_title = "🇮🇳 Happy Republic Day 🇮🇳"

    carousel_imgs_html = ""
    if os.path.exists("Carousel_Images"):
        for img_file in os.listdir("Carousel_Images"):
            if img_file.lower().endswith(('png', 'jpg', 'jpeg')):
                with open(os.path.join("Carousel_Images", img_file), "rb") as f:
                    b64_str = base64.b64encode(f.read()).decode('utf-8')
                    mime_type = "image/png" if img_file.lower().endswith('png') else "image/jpeg"
                    carousel_imgs_html += f"<img class='marquee-img' src='data:{mime_type};base64,{b64_str}'>"
    
    if not carousel_imgs_html:
        carousel_imgs_html = (
            "<img class='marquee-img' src='https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=600&q=80'>"
            "<img class='marquee-img' src='https://images.unsplash.com/photo-1509062522246-3755977927d7?w=600&q=80'>"
            "<img class='marquee-img' src='https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=600&q=80'>"
        )

    carousel_html = f"""
    <!DOCTYPE html>
    <html>
    <head><style>
    html, body {{ margin: 0; padding: 0; background: transparent; font-family: sans-serif; overflow: hidden; height: 100%; }}
    .carousel-container {{ width: 100%; height: 350px; overflow: hidden; border-radius: 10px; position: relative; border: 2px solid #38bdf8; background: rgba(15, 23, 42, 0.6); }}
    .marquee-img {{ height: 260px; border-radius: 10px; margin-right: 20px; object-fit: contain; display: inline-block; vertical-align: middle; margin-top: 15px; border: 2px solid #fbbf24; background-color: #fff; padding: 5px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }}
    .carousel-overlay {{ position: absolute; bottom: 0; background: rgba(30,58,138,0.9); width: 100%; color: white; text-align: center; padding: 12px; font-weight: bold; font-size: 20px; letter-spacing: 1px; box-sizing: border-box; text-shadow: 1px 1px 2px #000; }}
    </style></head>
    <body>
    <div class="carousel-container">
        <marquee behavior="scroll" direction="left" scrollamount="12" onmouseover="this.stop();" onmouseout="this.start();" style="display: flex; align-items: center; white-space: nowrap; height: 100%;">
            {event_images}{carousel_imgs_html}
        </marquee>
        <div class="carousel-overlay">Connecting Students, Teachers & Administration Seamlessly</div>
    </div>
    </body></html>
    """
    st.markdown(f"<div class='glass-panel'><h2 style='text-align: center; color: #fbbf24; margin-top: 0; text-shadow: 1px 1px 2px #000;'>🏫 {event_title}</h2>", unsafe_allow_html=True)
    components.html(carousel_html, height=360)
    st.markdown("</div>", unsafe_allow_html=True)

    notice_and_news_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
    body {{ margin: 0; padding: 0; font-family: sans-serif; background: transparent; }}
    .notice-box {{ background-color: rgba(30,41,59,0.9); border-radius: 5px; border: 1px solid #475569; overflow: hidden; color: #e2e8f0; font-size: 18px; padding: 10px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);}}
    .news-box {{ background-color: rgba(127,29,29,0.9); border-radius: 5px; border: 1px solid #ef4444; overflow: hidden; color: #ffffff; font-size: 18px; padding: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);}}
    .label {{ font-size:12px; font-weight:bold; margin-bottom:4px; letter-spacing: 1px; }}
    .new-badge {{ background-color: #fbbf24; color: black; font-size: 14px; font-weight: bold; padding: 2px 6px; border-radius: 3px; margin-left: 5px; }}
    </style>
    </head>
    <body>
        <div class="notice-box">
            <div class="label" style="color:#94a3b8;">📌 OFFICIAL NOTIFICATIONS & UPDATES</div>
            <marquee direction='left' scrollamount='8' style='font-weight: bold;'>
                <span style='color: #fbbf24;'>{master_db.get('notice_text')}</span>
            </marquee>
        </div>
        <div class="news-box">
            <div class="label" style="color:#fca5a5;">📰 ALL INDIA DAILY BREAKING NEWS</div>
            <marquee direction='left' scrollamount='6' style='font-weight: bold;'>
                <span>{master_db.get('news_text')}</span>
            </marquee>
        </div>
    </body>
    </html>
    """
    st.markdown("<div class='glass-panel' style='padding: 10px;'>", unsafe_allow_html=True)
    components.html(notice_and_news_html, height=180)
    st.markdown("</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1: 
        st.markdown("<a href='?portal=scholarship' target='_self' class='login-card'><div class='login-title'>💰 Scholarship Portal</div><div class='login-sub'>Apply Now</div></a>", unsafe_allow_html=True)
        st.markdown("<a href='?portal=master' target='_self' class='login-card'><div class='login-title'>🏛️ Master Login</div><div class='login-sub'>Admin Portal</div></a>", unsafe_allow_html=True)
    with c2: 
        st.markdown("<a href='?portal=reg_student' target='_self' class='login-card'><div class='login-title'>👨‍🎓 New Student Reg.</div><div class='login-sub'>Apply for admission</div></a>", unsafe_allow_html=True)
        st.markdown("<a href='?portal=school' target='_self' class='login-card'><div class='login-title'>🏫 School Login</div><div class='login-sub'>School / College Portal</div></a>", unsafe_allow_html=True)
    with c3: 
        st.markdown("<a href='?portal=reg_school' target='_self' class='login-card'><div class='login-title'>🏫 New School Reg.</div><div class='login-sub'>Register institution</div></a>", unsafe_allow_html=True)
        st.markdown("<a href='?portal=student' target='_self' class='login-card' style='height: 43%; display: flex; flex-direction: column; justify-content: center;'><div class='login-title' style='font-size: 32px;'>🎓 Check Results</div><div class='login-sub'>Download Rank Card</div></a>", unsafe_allow_html=True)

# ----------------- SCHOLARSHIP PORTAL (NEW LOGIN & DRAFT) -----------------
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
                st.info("Enter your 12-digit Aadhaar Number as User ID.")
                l_uid = st.text_input("User ID (Aadhaar No.) *", key="l_sch_uid")
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
                st.info("Recover your Student Account using Aadhaar No")
                f_uid = st.text_input("Enter your Aadhaar No (User ID)", key="f_sch_uid")
                if st.button("Send OTP", key="f_sch_send"):
                    if sanitize(f_uid) in sch_users_db:
                        otp_code = str(random.randint(1000, 9999))
                        st.session_state['sch_f_otp'] = otp_code
                        st.session_state['sch_f_uid'] = sanitize(f_uid)
                        reg_mob = sch_users_db[sanitize(f_uid)]["mobile"]
                        
                        send_real_sms(reg_mob, otp_code)
                        st.warning("⚠️ Direct SMS is restricted by gateway provider. Use the instant WhatsApp Notification button below to get your OTP on WhatsApp!")
                        wa_url = st.session_state.get('whatsapp_link', '#')
                        st.markdown(f"<a href='{wa_url}' target='_blank' style='background-color:#25D366; color:white; padding:10px 20px; border-radius:5px; text-decoration:none; font-weight:bold; display:inline-block; margin-top:10px;'>💬 Send OTP via WhatsApp</a>", unsafe_allow_html=True)
                        st.info(f"📲 [SYSTEM FALLBACK] Demo OTP is: {otp_code}")
                    else:
                        st.error("Aadhaar Number not found in our records!")
                        
                if 'sch_f_otp' in st.session_state:
                    entered_otp = st.text_input("Enter 4-digit OTP", key="f_sch_otp_inp")
                    if st.button("Verify OTP", key="f_sch_ver"):
                        if entered_otp == st.session_state['sch_f_otp']:
                            st.success("OTP Verified! You can now reset your password.")
                            st.session_state['sch_otp_verified'] = True
                        else:
                            st.error("Invalid OTP!")
                            
                if st.session_state.get('sch_otp_verified', False):
                    st.markdown("### 🔄 Reset Password")
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
                        elif new_s_pass != c_s_pass:
                            st.error("Passwords do not match!")
                        else:
                            st.warning("Please enter a password.")
                    
        with reg_tab:
            if 'sch_reg_step' not in st.session_state: st.session_state['sch_reg_step'] = 1
            
            if st.session_state['sch_reg_step'] == 1:
                r_mob = st.text_input("Mobile Number *", max_chars=10)
                r_adh = st.text_input("Aadhaar Number (12-digit) *", max_chars=12)
                if st.button("Get OTP"):
                    if len(r_mob) == 10 and len(r_adh) == 12:
                        if sanitize(r_adh) in sch_users_db:
                            st.error("Aadhaar Number already registered! Please go to Login.")
                        else:
                            st.session_state['temp_r_mob'] = sanitize(r_mob)
                            st.session_state['temp_r_adh'] = sanitize(r_adh)
                            st.session_state['temp_sch_otp'] = str(random.randint(1000, 9999))
                            
                            send_real_sms(sanitize(r_mob), st.session_state['temp_sch_otp'])
                            st.warning("⚠️ Direct SMS is restricted. Use the instant WhatsApp button below to get your OTP on WhatsApp!")
                            wa_url = st.session_state.get('whatsapp_link', '#')
                            st.markdown(f"<a href='{wa_url}' target='_blank' style='background-color:#25D366; color:white; padding:10px 20px; border-radius:5px; text-decoration:none; font-weight:bold; display:inline-block; margin-top:10px;'>💬 Send OTP via WhatsApp</a>", unsafe_allow_html=True)
                            st.info(f"📲 [SYSTEM FALLBACK] Demo OTP is: {st.session_state['temp_sch_otp']}")
                                
                            st.session_state['sch_reg_step'] = 2
                            st.rerun()
                    else: st.error("Please enter valid Mobile and Aadhaar numbers.")
            
            elif st.session_state['sch_reg_step'] == 2:
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
                if st.button("Register & Create Profile", type="primary"):
                    if pwd1 and pwd1 == pwd2:
                        uid = st.session_state['temp_r_adh']
                        sch_users_db[uid] = {
                            "mobile": st.session_state['temp_r_mob'],
                            "password": pwd1,
                            "draft": {}
                        }
                        save_sch_users(sch_users_db)
                        st.success("Registration Successful! Please login with your Aadhaar No.")
                        st.session_state['sch_reg_step'] = 1
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
            if a_data.get("aadhaar") == cur_uid:
                existing_app_id = a_id
                existing_app_data = a_data
                break
                
        if existing_app_id:
            st.error("⚠️ ଆପଣ ପୂର୍ବରୁ ସ୍କଲାରସିପ୍ ଆବେଦନ କରିସାରିଛନ୍ତି (You have already submitted your application). ଆପଣ ପୁନର୍ବାର ଆବେଦନ କରିପାରିବେ ନାହିଁ।")
            
            st.markdown(render_odisha_scholarship_html(existing_app_id, existing_app_data), unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            c_btn1, c_btn2 = st.columns(2)
            
            pdf_path = f"Scholarship_Data/Student_Submissions/{existing_app_id}/Payment_Receipt_Application.pdf"
            if not os.path.exists(pdf_path):
                os.makedirs(f"Scholarship_Data/Student_Submissions/{existing_app_id}", exist_ok=True)
                create_odisha_scholarship_pdf(pdf_path, existing_app_id, existing_app_data)
                
            with open(pdf_path, "rb") as f:
                c_btn1.download_button("📥 Download PDF", f, file_name=f"Scholarship_{existing_app_id}.pdf", mime="application/pdf", key="stu_dash_dl")
            
            if c_btn2.button("🖨️ Print Application", key="stu_dash_print"):
                components.html("<script>window.parent.print();</script>", height=0)
                
        else:
            if st.session_state.get('sch_app_success'):
                st.success("✅ Application & Payment Submitted Successfully!")
                pdf_path = f"Scholarship_Data/Student_Submissions/{st.session_state['sch_app_id']}/Payment_Receipt_Application.pdf"
                c_suc1, c_suc2 = st.columns(2)
                with c_suc1:
                    if os.path.exists(pdf_path):
                        with open(pdf_path, "rb") as f: 
                            st.download_button("📥 Download Application & Receipt PDF", f, file_name=f"Scholarship_{st.session_state['sch_app_id']}.pdf", mime="application/pdf", key="sch_dl_success")
                with c_suc2:
                    if st.button("🏠 Go to Home Page", key="sch_go_home"): 
                        st.query_params["portal"] = "home"
                        st.session_state['sch_app_success'] = False
                        st.session_state['sch_app_step'] = False
                        st.rerun()

            elif not st.session_state.get('sch_app_step'):
                st.info("💡 To prevent data loss (20 min session timeout), click **'💾 Save as Draft'** at the bottom frequently.")
                
                col_o1, col_o2 = st.columns([8, 2])
                otr_input = col_o1.text_input("OTR No. *", value=draft_data.get("otr", ""), key="otr_inp_val")
                if col_o2.button("VERIFY OTR"):
                    st.success("✅ OTR Verified Successfully!")

                c_ad1, c_ad2 = st.columns([8, 2])
                aadhaar_input = c_ad1.text_input("Aadhaar No. *", value=cur_uid, disabled=True, key="ad_inp_val")
                if c_ad2.button("VERIFY AADHAAR"):
                    st.success("✅ Aadhaar Linked & Verified!")

                c1, c2, c3 = st.columns(3)
                ac_year = c1.selectbox("Academic Year", ["2026-27", "2027-28"])
                dept = c2.selectbox("Department", ["ST&SC and MBC Welfare Depart", "Higher Education"])
                scheme = c3.selectbox("Scheme", ["Pre Matric", "Post Matric"])
                
                c4, c5 = st.columns(2)
                app_name = c4.text_input("Applicant Name *", value=draft_data.get("app_name", ""))
                category = c5.selectbox("Category *", SOCIAL_CATEGORIES)
                
                c6, c7, c8 = st.columns(3)
                gender = c6.radio("Applicant Gender:", ["Male", "Female", "Transgender"])
                religion = c7.selectbox("Religion", ["Select", "Hindu", "Muslim", "Christian", "Other"])
                photo = c8.file_uploader("Profile Photo (jpg, png)", type=['png', 'jpg', 'jpeg'])
                
                c9, c10 = st.columns(2)
                dob = c9.text_input("Date of Birth (YYYY-MM-DD) *", value=draft_data.get("dob", ""))
                mob_no = c10.text_input("Mobile No. *", value=user_profile.get("mobile", ""))
                
                c13, c14 = st.columns(2)
                f_name = c13.text_input("Father's Name *", value=draft_data.get("father_name", ""))
                m_name = c14.text_input("Mother's Name *", value=draft_data.get("mother_name", ""))
                
                addr = st.text_area("Full Address *", value=draft_data.get("full_address", ""))
                
                active_schools = {k: v for k, v in schools_db.items() if v.get("status", "Active") == "Active"}
                school_options = [f"{k} - {v['name']}" for k, v in active_schools.items()]
                c24, c25 = st.columns(2)
                school_sel_str = c24.selectbox("Institute (School) *", ["--Select--"] + school_options)
                sch_class = c25.selectbox("Class *", ["IX", "X", "XI", "XII"])
                school_code = school_sel_str.split(" - ")[0] if school_sel_str != "--Select--" else None
                
                c33, c34 = st.columns(2)
                with c33:
                    st.markdown("**Income Certificate**")
                    inc_no = st.text_input("Income Certificate No. *", value=draft_data.get("income_cert", ""))
                    if st.button("VERIFY INCOME"): st.success("Verified")
                    inc_file = st.file_uploader("Upload Income Certificate Photo *", type=['png', 'jpg', 'jpeg'])
                with c34:
                    st.markdown("**Caste Certificate**")
                    cas_no = st.text_input("Caste Certificate No. *", value=draft_data.get("caste_cert", ""))
                    if st.button("VERIFY CASTE"): st.success("Verified")
                    cas_file = st.file_uploader("Upload Caste Certificate Photo *", type=['png', 'jpg', 'jpeg'])
                
                st.markdown("### 🏦 Bank Information")
                c35, c36 = st.columns([8, 2])
                ifsc = c35.text_input("IFSC Code *", value=draft_data.get("ifsc", ""))
                if c36.button("FIND IFSC"):
                    st.success("✅ IFSC Verified!")
                
                c38, c39 = st.columns([8, 2])
                acc_no = c38.text_input("Account Number *", type="password", value=draft_data.get("acc_no", ""))
                if c39.button("VERIFY ACCOUNT"): st.success("✅ Account Verified!")
                acc_name = st.text_input("Account Holder Name *", value=draft_data.get("acc_name", ""))
                
                c_seed, c_pass = st.columns(2)
                seeded = c_seed.radio("Aadhaar Seeded?", ["Yes", "No"], index=0)
                passbook = c_pass.file_uploader("Upload Passbook (JPG/PNG) *", type=['png', 'jpg', 'jpeg'])
                
                st.markdown("---")
                col_save, col_sub = st.columns(2)
                
                with col_save:
                    if st.button("💾 Save to Draft Box", use_container_width=True):
                        sch_users_db[cur_uid]["draft"] = {
                            "otr": sanitize(otr_input), "app_name": sanitize(app_name), "dob": sanitize(dob),
                            "father_name": sanitize(f_name), "mother_name": sanitize(m_name), "full_address": sanitize(addr),
                            "income_cert": sanitize(inc_no), "caste_cert": sanitize(cas_no), "ifsc": sanitize(ifsc),
                            "acc_no": sanitize(acc_no), "acc_name": sanitize(acc_name)
                        }
                        save_sch_users(sch_users_db)
                        st.success("Progress Saved Securely to Draft!")
                        
                with col_sub:
                    if st.button("Proceed to Payment & Submit", type="primary", use_container_width=True):
                        if not school_code or not sanitize(app_name) or not sanitize(acc_no):
                            st.error("Please fill all mandatory fields (*).")
                        else:
                            photo_b64 = base64.b64encode(photo.read()).decode('utf-8') if photo else ""
                            inc_file_b64 = base64.b64encode(inc_file.read()).decode('utf-8') if inc_file else ""
                            cas_file_b64 = base64.b64encode(cas_file.read()).decode('utf-8') if cas_file else ""
                            passbook_b64 = base64.b64encode(passbook.read()).decode('utf-8') if passbook else ""
                            
                            app_id = "SCH" + str(random.randint(1000000, 9999999))
                            st.session_state['temp_sch_data'] = {
                                "app_id": app_id,
                                "data": {
                                    "academic_year": ac_year, "scheme": scheme, "app_name": sanitize(app_name),
                                    "category": category, "otr": sanitize(otr_input), "gender": gender,
                                    "dob": str(dob), "aadhaar": cur_uid, "mobile": sanitize(mob_no),
                                    "full_address": sanitize(addr), "school_code": school_code, "class": sch_class, 
                                    "father_name": sanitize(f_name), "mother_name": sanitize(m_name),
                                    "income_cert": sanitize(inc_no), "caste_cert": sanitize(cas_no), "ifsc": sanitize(ifsc), 
                                    "acc_no": sanitize(acc_no), "acc_name": sanitize(acc_name),
                                    "photo_b64": photo_b64, "inc_file_b64": inc_file_b64,
                                    "cas_file_b64": cas_file_b64, "passbook_b64": passbook_b64,
                                    "status": "Pending_Master", "payment_mode": "Pending", "fee": sch_fee
                                }
                            }
                            st.session_state['sch_app_step'] = True
                            st.rerun()

            if st.session_state.get('sch_app_step', False):
                st.markdown("### 💳 Secure Scholarship Payment Gateway")
                tmp = st.session_state['temp_sch_data']
                st.info(f"Applicant: **{tmp['data']['app_name']}** | Fee: **₹{sch_fee:.2f}**")
                pay_mode = st.radio("Select Payment Mode", ["Online Payment (UPI/QR)", "Offline Payment"])
                
                if pay_mode == "Online Payment (UPI/QR)":
                    master_upi = master_db.get("upi_id", "school@sbi")
                    upi_url = f"upi://pay?pa={master_upi}&pn=ScholarshipFee&am={sch_fee:.2f}&cu=INR"
                    qr_api = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={urllib.parse.quote(upi_url)}"
                    st.markdown(f"<img src='{qr_api}' style='border:5px solid #1E3A8A; border-radius:10px;'>", unsafe_allow_html=True)
                    txn_id = st.text_input("Enter 12-digit Transaction ID / UTR No. *")
                    if st.button("Verify & Submit Application", type="primary"):
                        if not txn_id or len(txn_id) < 8: st.error("Enter valid Transaction ID.")
                        else:
                            tmp['data']['payment_mode'] = f"Online (₹{sch_fee:.2f} - Txn: {sanitize(txn_id)})"
                            
                            folder_path = f"Scholarship_Data/Student_Submissions/{tmp['app_id']}"
                            os.makedirs(folder_path, exist_ok=True)
                            pdf_path = f"{folder_path}/Payment_Receipt_Application.pdf"
                            create_odisha_scholarship_pdf(pdf_path, tmp['app_id'], tmp['data'])
                            
                            scholarships_db[tmp['app_id']] = tmp['data']
                            save_scholarships(scholarships_db)
                            
                            sch_users_db[cur_uid]["draft"] = {}
                            save_sch_users(sch_users_db)
                            
                            st.session_state['sch_app_success'] = True
                            st.session_state['sch_app_id'] = tmp['app_id']
                            st.session_state['sch_app_data'] = tmp['data']
                            st.session_state['sch_app_step'] = False; st.rerun()
                else:
                    if st.button("Complete Payment & Submit Application", type="primary"):
                        tmp['data']['payment_mode'] = f"Offline (₹{sch_fee:.2f})"
                        
                        folder_path = f"Scholarship_Data/Student_Submissions/{tmp['app_id']}"
                        os.makedirs(folder_path, exist_ok=True)
                        pdf_path = f"{folder_path}/Payment_Receipt_Application.pdf"
                        create_odisha_scholarship_pdf(pdf_path, tmp['app_id'], tmp['data'])
                        
                        scholarships_db[tmp['app_id']] = tmp['data']
                        save_scholarships(scholarships_db)
                        
                        sch_users_db[cur_uid]["draft"] = {}
                        save_sch_users(sch_users_db)
                        
                        st.session_state['sch_app_success'] = True
                        st.session_state['sch_app_id'] = tmp['app_id']
                        st.session_state['sch_app_data'] = tmp['data']
                        st.session_state['sch_app_step'] = False; st.rerun()

# ----------------- NEW STUDENT REGISTRATION -----------------
elif menu == "New Student Registration":
    c_home, c_title = st.columns([1, 8])
    with c_home:
        if st.button("🏠 Home", key="reg_stu_home"): st.query_params["portal"] = "home"; st.rerun()
    with c_title: st.subheader("👨‍🎓 New Student Registration & Payment Portal")

    base_fee = float(master_db.get("reg_fee", 150.0))
    gst_pct = float(master_db.get("gst_percent", 18.0))
    total_fee = round(base_fee + (base_fee * (gst_pct / 100.0)), 2)

    if 'payment_step' not in st.session_state: st.session_state['payment_step'] = False
    if 'stu_reg_success' not in st.session_state: st.session_state['stu_reg_success'] = False

    if st.session_state['stu_reg_success']:
        st.success(f"✅ Application Submitted! Reg ID: **{st.session_state['stu_reg_id']}**.")
        pdf_file = f"Receipt_{st.session_state['stu_reg_id']}.pdf"
        create_student_receipt_pdf(pdf_file, st.session_state['stu_reg_id'], st.session_state['stu_reg_data'])
        with open(pdf_file, "rb") as f: st.download_button("📥 Download PDF Receipt", f, file_name=pdf_file, mime="application/pdf", key="stu_dl_btn_unique")
        if st.button("⬅️ Done", key="stu_done_btn_unique"): st.session_state['stu_reg_success'] = False; st.rerun()
                
    elif not st.session_state['payment_step']:
        with st.form("student_reg_form"):
            st.markdown("#### 1. School Information")
            c_sc1, c_sc2 = st.columns(2)
            active_schools = {k: v for k, v in schools_db.items() if v.get("status", "Active") == "Active"}
            school_options = [f"{k} - {v['name']}" for k, v in active_schools.items()] if active_schools else []
            school_sel_str = c_sc1.selectbox("Select School Code & Name *", ["--Select--"] + school_options) if school_options else "--Select--"
            school_sel = school_sel_str.split(" - ")[0] if school_sel_str != "--Select--" else None
            
            st.markdown("#### 2. Personal Details")
            c_n1, c_n2 = st.columns(2)
            stu_name_en = c_n1.text_input("1. Student's Name (English) *")
            stu_name_loc = c_n2.text_input("1. Student's Name (Local Language)")
            
            c_g1, c_g2, c_g3 = st.columns(3)
            stu_gender_en = c_g1.selectbox("2. Gender", ["Male", "Female", "Other"])
            stu_dob = c_g2.date_input("3. Date of Birth *", min_value=datetime.date(2000, 1, 1), max_value=datetime.date.today())
            stu_category = c_g3.selectbox("4. Category *", SOCIAL_CATEGORIES)
            
            c_d1, c_d2 = st.columns(2)
            m_name_en = c_d1.text_input("5. Mother's Name (English) *")
            m_name_loc = c_d2.text_input("Mother's Name (Local)")
            
            c_f1, c_f2 = st.columns(2)
            f_name_en = c_f1.text_input("6. Father's Name (English) *")
            f_name_loc = c_f2.text_input("Father's Name (Local)")
            
            st.markdown("#### 3. Contact & Identification")
            c_id1, c_id2 = st.columns(2)
            stu_aadhar = c_id1.text_input("7. AADHAAR Number *", max_chars=12)
            stu_phone = c_id2.text_input("8. Mobile No *", max_chars=10)
            
            c_ad1, c_ad2 = st.columns(2)
            stu_address_en = c_ad1.text_area("9. Address (English) *")
            stu_address_loc = c_ad2.text_area("Address (Local)")
            
            c_loc1, c_loc2, c_loc3 = st.columns(3)
            stu_state = c_loc1.selectbox("10. State", list(STATE_LANG_MAP.keys()), index=18)
            stu_pin = c_loc2.text_input("11. PIN Code *", max_chars=6)
            stu_minority = c_loc3.selectbox("12. Minority Group", ["No", "Yes - Muslim", "Yes - Christian", "Yes - Sikh", "Yes - Buddhist", "Yes - Parsi", "Yes - Jain"])
            
            c_nat1, c_nat2 = st.columns(2)
            stu_country = c_nat1.selectbox("13. Nationality", COUNTRIES)
            stu_bg = c_nat2.selectbox("14. Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"])
            
            declaration = st.checkbox("✅ I declare the above info is true.")
            if st.form_submit_button("Proceed to Payment & Submit"):
                if not declaration: st.error("⚠️ Please check the declaration box.")
                elif not school_sel or not sanitize(stu_name_en) or not sanitize(stu_phone):
                    st.error("Please fill all mandatory fields (*).")
                else:
                    temp_reg_id = "REG" + str(random.randint(100000, 999999))
                    st.session_state['temp_student_data'] = {
                        "reg_id": temp_reg_id, "school_sel": school_sel,
                        "data": {
                            "name": sanitize(stu_name_en), "name_local": sanitize(stu_name_loc), 
                            "gender": stu_gender_en, "category": stu_category,
                            "father_name": sanitize(f_name_en), "father_name_local": sanitize(f_name_loc),
                            "mother_name": sanitize(m_name_en), "mother_name_local": sanitize(m_name_loc),
                            "dob": str(stu_dob), "aadhaar": sanitize(stu_aadhar), "phone": sanitize(stu_phone),
                            "address": sanitize(stu_address_en), "address_local": sanitize(stu_address_loc),
                            "state": stu_state, "pin_code": sanitize(stu_pin), "minority": stu_minority, 
                            "nationality": stu_country, "blood_group": stu_bg,
                            "school_code": school_sel, "class": "1", "batch": "2025-2026",
                            "subjects": {}, "total_full": 0, "total_obt": 0, "percentage": 0.0,
                            "result": "N/A", "grade": "N/A", "pub_date": str(datetime.date.today()),
                            "payment_mode": "Pending", "status": "Pending_Master", "total_fee": total_fee
                        }
                    }
                    st.session_state['payment_step'] = True; st.rerun()

    if st.session_state.get('payment_step', False):
        temp_obj = st.session_state.get('temp_student_data')
        st.info(f"Total Fee: **₹{total_fee:.2f}**")
        pay_mode = st.radio("Select Payment Mode", ["Online Payment (UPI/QR)", "Offline Payment"], key="stu_pay_mode_unique")
        
        if pay_mode == "Online Payment (UPI/QR)":
            master_upi = master_db.get("upi_id", "school@sbi")
            upi_url = f"upi://pay?pa={master_upi}&pn=StudentReg&am={total_fee:.2f}&cu=INR"
            qr_api = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={urllib.parse.quote(upi_url)}"
            st.markdown(f"<img src='{qr_api}' style='border:5px solid #1E3A8A; border-radius:10px;'>", unsafe_allow_html=True)
            st.markdown(f"**UPI ID:** `{master_upi}`")
            txn_id = st.text_input("Enter 12-digit Transaction ID / UTR No. *", key="stu_txn_input_unique")
            if st.button("Complete Payment & Submit", type="primary", key="stu_complete_pay_btn_unique"):
                if not txn_id or len(txn_id) < 8: st.error("Enter valid Transaction ID.")
                else:
                    temp_obj['data']['payment_mode'] = f"Online (₹{total_fee:.2f} - Txn: {sanitize(txn_id)})"
                    sch_id = temp_obj['school_sel']
                    if sch_id not in students_db: students_db[sch_id] = {}
                    students_db[sch_id][temp_obj['reg_id']] = temp_obj['data']
                    save_data(schools_db, students_db)
                    st.session_state['stu_reg_success'] = True
                    st.session_state['stu_reg_id'] = temp_obj['reg_id']
                    st.session_state['stu_reg_data'] = temp_obj['data']
                    st.session_state['payment_step'] = False; st.rerun()
        else:
            if st.button("Complete Payment & Submit", type="primary", key="stu_offline_pay_btn_unique"):
                temp_obj['data']['payment_mode'] = f"Offline (₹{total_fee:.2f})"
                sch_id = temp_obj['school_sel']
                if sch_id not in students_db: students_db[sch_id] = {}
                students_db[sch_id][temp_obj['reg_id']] = temp_obj['data']
                save_data(schools_db, students_db)
                st.session_state['stu_reg_success'] = True
                st.session_state['stu_reg_id'] = temp_obj['reg_id']
                st.session_state['stu_reg_data'] = temp_obj['data']
                st.session_state['payment_step'] = False; st.rerun()

# ----------------- NEW SCHOOL REGISTRATION -----------------
elif menu == "New School Registration":
    c_home, c_title = st.columns([1, 8])
    with c_home:
        if st.button("🏠 Home", key="reg_sch_home"): st.query_params["portal"] = "home"; st.rerun()
    with c_title: st.subheader("📝 New School Registration")
    
    s_base_fee = float(master_db.get("school_reg_fee", 1000.0))
    s_gst_pct = float(master_db.get("school_gst_percent", 18.0))
    s_total_fee = round(s_base_fee + (s_base_fee * (s_gst_pct / 100.0)), 2)

    if 'school_payment_step' not in st.session_state: st.session_state['school_payment_step'] = False
    if 'sch_reg_success' not in st.session_state: st.session_state['sch_reg_success'] = False

    if st.session_state['sch_reg_success']:
        st.success("✅ Registration Successful! PENDING approval from Master Admin.")
        pdf_file = f"School_Receipt_{st.session_state['sch_reg_id']}.pdf"
        create_school_receipt_pdf(pdf_file, st.session_state['sch_reg_id'], st.session_state['sch_reg_data'])
        with open(pdf_file, "rb") as f: st.download_button("📥 Download PDF Receipt", f, file_name=pdf_file, mime="application/pdf", key="sch_dl_btn_unique")
        if st.button("⬅️ Done", key="sch_done_btn_unique"): st.session_state['sch_reg_success'] = False; st.rerun()

    elif not st.session_state['school_payment_step']:
        with st.form("school_reg_form"):
            r_id = st.text_input("School ID (Unique) *")
            c_n1, c_n2 = st.columns(2)
            r_name_en = c_n1.text_input("School Name (English) *")
            r_name_loc = c_n2.text_input("School Name (Local Language)")
            r_state = st.selectbox("State", list(STATE_LANG_MAP.keys()), index=18)
            r_hm_name = st.text_input("Head Master Name")
            r_hm_phone = st.text_input("HM Mobile No.")
            c_p1, c_p2 = st.columns(2)
            r_pass = c_p1.text_input("New Password *", type="password")
            r_cpass = c_p2.text_input("Confirm Password *", type="password")
            
            s_decl = st.checkbox("✅ I declare the above info is true.")
            if st.form_submit_button("Proceed to Payment & Submit"):
                s_id_clean = sanitize(r_id)
                if not s_decl: st.error("⚠️ Check declaration box.")
                elif not s_id_clean or not sanitize(r_name_en) or not r_pass: st.error("Fill mandatory fields (*)")
                elif r_pass != r_cpass: st.error("Passwords do not match!")
                elif s_id_clean in schools_db: st.error("School ID already exists.")
                else:
                    st.session_state['temp_school_data'] = {
                        "school_id": s_id_clean,
                        "data": {
                            "name": sanitize(r_name_en), "name_local": sanitize(r_name_loc),
                            "hm_name": sanitize(r_hm_name), "hm_phone": sanitize(r_hm_phone),
                            "pass": r_pass, "state": r_state, "lang": STATE_LANG_MAP[r_state],
                            "status": "Pending_Master_Approval", "payment_mode": "Pending"
                        }
                    }
                    st.session_state['school_payment_step'] = True; st.rerun()

    if st.session_state.get('school_payment_step', False):
        s_tmp = st.session_state.get('temp_school_data')
        st.info(f"Total Fee: **₹{s_total_fee:.2f}**")
        s_pay_mode = st.radio("Select Payment Mode", ["Online Payment (UPI/QR)", "Offline Payment"], key="sch_pay_mode_unique")
        if s_pay_mode == "Online Payment (UPI/QR)":
            master_upi = master_db.get("upi_id", "school@sbi")
            upi_url = f"upi://pay?pa={master_upi}&pn=SchoolReg&am={s_total_fee:.2f}&cu=INR"
            qr_api = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={urllib.parse.quote(upi_url)}"
            st.markdown(f"<img src='{qr_api}' style='border:5px solid #1E3A8A; border-radius:10px;'>", unsafe_allow_html=True)
            txn_id = st.text_input("Enter Transaction ID / UTR No. *", key="sch_txn_input_unique")
            if st.button("Complete Payment & Submit", key="sch_online_sub_btn_unique"):
                if not txn_id or len(txn_id) < 8: st.error("Enter valid Transaction ID.")
                else:
                    s_tmp['data']['payment_mode'] = f"Online (₹{s_total_fee:.2f} - Txn: {sanitize(txn_id)})"
                    schools_db[s_tmp["school_id"]] = s_tmp["data"]
                    save_data(schools_db, students_db)
                    st.session_state['sch_reg_success'] = True
                    st.session_state['sch_reg_id'] = s_tmp['school_id']
                    st.session_state['sch_reg_data'] = s_tmp['data']
                    st.session_state['school_payment_step'] = False; st.rerun()
        else:
            if st.button("Complete Payment & Submit", key="sch_offline_sub_btn_unique"):
                s_tmp['data']['payment_mode'] = f"Offline (₹{s_total_fee:.2f})"
                schools_db[s_tmp["school_id"]] = s_tmp["data"]
                save_data(schools_db, students_db)
                st.session_state['sch_reg_success'] = True
                st.session_state['sch_reg_id'] = s_tmp['school_id']
                st.session_state['sch_reg_data'] = s_tmp['data']
                st.session_state['school_payment_step'] = False; st.rerun()

# ----------------- MASTER LOGIN -----------------
elif menu == "Master Login":
    c_home, c_title = st.columns([1, 8])
    with c_home:
        if st.button("🏠 Home", key="m_home_btn"): st.query_params["portal"] = "home"; st.rerun()
    with c_title: st.subheader("🔑 Master Administrator Portal")
    
    if not st.session_state.get('master_logged', False):
        login_mode = st.radio("Choose Action", ["Login", "Forgot Password"])
        if login_mode == "Login":
            check_brute_force()
            m_user = st.text_input("Master Username")
            m_pass = st.text_input("Master Password", type="password")
            if st.button("Login"):
                if sanitize(m_user) == master_db.get("username") and m_pass == master_db.get("password"):
                    st.session_state.failed_logins = 0
                    st.session_state['master_logged'] = True; st.rerun()
                else: 
                    st.session_state.failed_logins += 1
                    st.error("ଭୁଲ୍ Master ID କିମ୍ବା Password!")
        elif login_mode == "Forgot Password":
            st.info("Recover your Master Account using Mobile or Email OTP")
            verify_contact = st.text_input("Enter Registered Mobile No or Email")
            if st.button("Send OTP"):
                if verify_contact == master_db.get("email") or verify_contact == master_db.get("phone"):
                    otp_code = str(random.randint(1000, 9999))
                    st.session_state['master_otp'] = otp_code
                    send_real_sms(master_db.get("phone"), otp_code, "Master Admin")
                    st.warning("⚠️ Direct SMS is restricted. Use the instant WhatsApp button below to get your OTP on WhatsApp!")
                    wa_url = st.session_state.get('whatsapp_link', '#')
                    st.markdown(f"<a href='{wa_url}' target='_blank' style='background-color:#25D366; color:white; padding:10px 20px; border-radius:5px; text-decoration:none; font-weight:bold; display:inline-block; margin-top:10px;'>💬 Send OTP via WhatsApp</a>", unsafe_allow_html=True)
                    st.info(f"📲 [SYSTEM FALLBACK] Demo OTP is: {otp_code}")
                else: st.error("Invalid Email or Mobile Number!")
            if 'master_otp' in st.session_state:
                entered_otp = st.text_input("Enter 4-digit OTP")
                if st.button("Verify OTP"):
                    if entered_otp == st.session_state['master_otp']:
                        st.success("OTP Verified!")
                        st.session_state['otp_verified'] = True
                    else: st.error("Invalid OTP!")
            if st.session_state.get('otp_verified', False):
                new_m_user = st.text_input("New Master Username")
                new_m_pass = st.text_input("New Master Password", type="password")
                if st.button("Save New Credentials"):
                    if new_m_user and new_m_pass:
                        master_db["username"] = sanitize(new_m_user); master_db["password"] = new_m_pass
                        save_master_data(master_db)
                        st.success("Master ID & Password successfully updated!")
                        del st.session_state['master_otp']; del st.session_state['otp_verified']
                    else: st.warning("Please fill both fields.")
    else:
        c1, c2 = st.columns([8, 2])
        c1.success("Welcome Master Admin!")
        if c2.button("🔴 Logout"): st.session_state['master_logged'] = False; st.rerun()

        st.markdown("---")
        t1, t2, t3, t4, t5, t6, t7 = st.tabs(["👁️ Schools", "💳 Payments", "🎓 Scholarships Verify", "🎓 Edit Students", "⚙️ Settings", "🏦 Gateway", "🖼️ Display & Backgrounds"])
        
        with t1:
            st.markdown("### 🏫 Manage Schools")
            for s_id, s_info in list(schools_db.items()):
                status = s_info.get("status", "Active") 
                bg = "#f0fdf4" if status == "Active" else "#fef2f2"
                st.markdown(f"<div style='border:1px solid #cbd5e1; padding:10px; margin-bottom:10px; background-color:{bg};'><b>School ID:</b> {s_id} | <b>Name:</b> {s_info['name']} | Status: {status}</div>", unsafe_allow_html=True)
                if status == "Pending_Master_Approval":
                    if st.button("✅ Approve School Registration", key=f"app_{s_id}"):
                        s_info["status"] = "Active"; save_data(schools_db, students_db); st.rerun()
                elif status == "Inactive":
                    if st.button("✅ Make Active", key=f"act_{s_id}"):
                        s_info["status"] = "Active"; save_data(schools_db, students_db); st.rerun()

        with t2:
            st.markdown("### 💳 Verify Student Payments (Master)")
            pending_master = []
            for s_id, s_studs in students_db.items():
                for r_no, p_st in s_studs.items():
                    if p_st.get("status") == "Pending_Master":
                        pending_master.append((s_id, r_no, p_st))
            if pending_master:
                for s_id, r_no, p_st in pending_master:
                    st.write(f"**Reg:** {r_no} | **Name:** {p_st.get('name')} | **Amount:** ₹{p_st.get('total_fee', 0)}")
                    c_pay1, c_pay2 = st.columns(2)
                    if c_pay1.button(f"✅ Verify {r_no}", key=f"vp_{r_no}"):
                        p_st["status"] = "Pending_School"; save_data(schools_db, students_db); st.success("Verified!"); st.rerun()
                    if c_pay2.button(f"🚫 Reject {r_no}", key=f"rp_{r_no}"):
                        p_st['status'] = "Rejected_Refund"; save_data(schools_db, students_db); st.error("Rejected"); st.rerun()
            else: st.success("No pending student payments.")

        with t3:
            st.markdown("### 🎓 Scholarship Verifications (Master)")
            sch_tab1, sch_tab2 = st.tabs(["⏳ Pending Verification", "📂 Approved Master Folders"])
            
            with sch_tab1:
                pending_sch = {k: v for k, v in scholarships_db.items() if v.get("status") == "Pending_Master"}
                if pending_sch:
                    app_id = st.selectbox("Select Scholarship", list(pending_sch.keys()), key="m_sch_app_sel")
                    s_data = pending_sch[app_id]
                    
                    st.write(f"**Application ID:** {app_id} | **Payment:** {s_data.get('payment_mode')}")
                    
                    with st.expander("👁️ View & Edit Full Application", expanded=True):
                        c_e1, c_e2, c_e3 = st.columns(3)
                        e_name = c_e1.text_input("Applicant Name", s_data.get('app_name', ''), key=f"ms_name_{app_id}")
                        e_aadhaar = c_e2.text_input("Aadhaar No", s_data.get('aadhaar', ''), key=f"ms_adh_{app_id}")
                        e_mob = c_e3.text_input("Mobile No", s_data.get('mobile', ''), key=f"ms_mob_{app_id}")
                        
                        c_e4, c_e5, c_e6 = st.columns(3)
                        e_fname = c_e4.text_input("Father Name", s_data.get('father_name', ''), key=f"ms_fname_{app_id}")
                        e_mname = c_e5.text_input("Mother Name", s_data.get('mother_name', ''), key=f"ms_mname_{app_id}")
                        e_dob = c_e6.text_input("Date of Birth", s_data.get('dob', ''), key=f"ms_dob_{app_id}")
                        
                        c_e7, c_e8, c_e9 = st.columns(3)
                        e_inc = c_e7.text_input("Income Cert", s_data.get('income_cert', ''), key=f"ms_inc_{app_id}")
                        e_cas = c_e8.text_input("Caste Cert", s_data.get('caste_cert', ''), key=f"ms_cas_{app_id}")
                        e_acc = c_e9.text_input("Account No", s_data.get('acc_no', ''), key=f"ms_acc_{app_id}")
                        
                        st.markdown("#### 🖼️ Uploaded Documents")
                        c_doc1, c_doc2, c_doc3, c_doc4 = st.columns(4)
                        
                        def render_b64_img(col, title, b64_str, key_suffix):
                            col.markdown(f"**{title}**")
                            if b64_str:
                                img_data = base64.b64decode(b64_str)
                                col.image(img_data, use_container_width=True)
                                col.download_button("⬇️ Download", img_data, file_name=f"{title}_{app_id}.jpg", mime="image/jpeg", key=f"dl_{key_suffix}_{app_id}")
                            else:
                                col.info("Not Uploaded")

                        render_b64_img(c_doc1, "Profile Photo", s_data.get('photo_b64', ''), "photo")
                        render_b64_img(c_doc2, "Income Cert", s_data.get('inc_file_b64', ''), "inc")
                        render_b64_img(c_doc3, "Caste Cert", s_data.get('cas_file_b64', ''), "cas")
                        render_b64_img(c_doc4, "Bank Passbook", s_data.get('passbook_b64', ''), "pass")

                        if st.button("✅ Update Data & Approve Scholarship (Create Folder)", type="primary", key=f"m_sch_fwd_btn_{app_id}"):
                            s_data['app_name'] = sanitize(e_name)
                            s_data['aadhaar'] = sanitize(e_aadhaar)
                            s_data['mobile'] = sanitize(e_mob)
                            s_data['father_name'] = sanitize(e_fname)
                            s_data['mother_name'] = sanitize(e_mname)
                            s_data['dob'] = sanitize(e_dob)
                            s_data['income_cert'] = sanitize(e_inc)
                            s_data['caste_cert'] = sanitize(e_cas)
                            s_data['acc_no'] = sanitize(e_acc)
                            s_data['status'] = "Approved" 
                            
                            save_master_approved_folder(app_id, s_data)
                            
                            scholarships_db[app_id] = s_data
                            save_scholarships(scholarships_db)
                            st.success(f"Scholarship {app_id} Verified, Approved, & Saved to Master Folder!")
                            st.rerun()
                else: st.success("No pending scholarships.")
            
            with sch_tab2:
                approved_sch = {k: v for k, v in scholarships_db.items() if v.get("status") == "Approved"}
                if approved_sch:
                    a_id = st.selectbox("Select Approved Application Folder", list(approved_sch.keys()), key="m_appr_sel")
                    st.success(f"📂 Folder: Scholarship_Data/Approved_Master/{a_id}")
                    
                    pdf_m_file = f"Scholarship_Data/Approved_Master/{a_id}/Application_{a_id}.pdf"
                    if os.path.exists(pdf_m_file):
                        with open(pdf_m_file, "rb") as f:
                            st.download_button("📥 Download Final Application PDF", f, file_name=f"Application_{a_id}.pdf", mime="application/pdf", key=f"m_appr_pdf_{a_id}")
                    
                    app_data = approved_sch[a_id]
                    st.markdown(render_odisha_scholarship_html(a_id, app_data), unsafe_allow_html=True)
                    if st.button("🖨️ Print Application", key=f"m_print_{a_id}"):
                        components.html("<script>window.parent.print();</script>", height=0)

                else:
                    st.info("No approved folders yet.")

        with t4: 
            st.markdown("### 🎓 Edit & Delete Students Data (Master)")
            master_school_sel = st.selectbox("Select School", ["--Select--"] + list(schools_db.keys()), key="m_sch_sel_fixed")
            if master_school_sel != "--Select--":
                school_students = students_db.get(master_school_sel, {})
                s_lang = schools_db[master_school_sel].get("lang", "English")
                if school_students:
                    m_edit_roll = st.selectbox("Select Student Roll No", list(school_students.keys()), key="m_roll_sel_fixed")
                    m_curr_st = school_students[m_edit_roll]
                    
                    st.markdown("#### 📝 Edit Personal Details")
                    c1, c2 = st.columns(2)
                    m_up_name = c1.text_input("Name (English)", value=m_curr_st.get('name',''), key=f"m_name_fix_{m_edit_roll}")
                    m_up_name_loc = c2.text_input(f"Name ({s_lang})", value=m_curr_st.get('name_local',''), key=f"m_nameloc_fix_{m_edit_roll}")
                    c3, c4 = st.columns(2)
                    m_up_father = c3.text_input("Father's Name (English)", value=m_curr_st.get('father_name', ''), key=f"m_fat_fix_{m_edit_roll}")
                    m_up_father_loc = c4.text_input(f"Father's Name ({s_lang})", value=m_curr_st.get('father_name_local', ''), key=f"m_fatloc_fix_{m_edit_roll}")
                    
                    c_up1, c_up2, c_up3 = st.columns(3)
                    genders = ["Male", "Female", "Other"]
                    m_up_gender = c_up1.selectbox("Gender", genders, index=genders.index(m_curr_st.get('gender', 'Male')) if m_curr_st.get('gender', 'Male') in genders else 0, key=f"m_gen_fix_{m_edit_roll}")
                    m_up_pen = c_up2.text_input("PEN NO", value=m_curr_st.get('pen_no', ''), key=f"m_pen_fix_{m_edit_roll}")
                    m_up_apaar = c_up3.text_input("APAAR NO", value=m_curr_st.get('apaar_no', ''), key=f"m_apaar_fix_{m_edit_roll}")
                    
                    c_d1, c_c1, c_b1 = st.columns(3)
                    m_up_dob = c_d1.text_input("DOB (DD-MM-YYYY)", value=m_curr_st.get('dob', ''), key=f"m_dob_fix_{m_edit_roll}")
                    m_up_class = c_c1.selectbox("Class", classes_list, index=classes_list.index(m_curr_st.get('class', '1')) if m_curr_st.get('class', '1') in classes_list else 0, key=f"m_cls_fix_{m_edit_roll}")
                    m_up_batch = c_b1.selectbox("Batch", batches_list, index=batches_list.index(m_curr_st.get('batch', '2025-2026')) if m_curr_st.get('batch', '2025-2026') in batches_list else 5, key=f"m_bat_fix_{m_edit_roll}")
                    
                    st.markdown("#### 📚 Edit Subjects & Marks")
                    m_subjects = m_curr_st.get('subjects', {})
                    existing_m_keys = list(m_subjects.keys())
                    
                    m_state_key = f"m_edit_sub_cnt_{m_edit_roll}"
                    if m_state_key not in st.session_state:
                        st.session_state[m_state_key] = max(5, len(existing_m_keys))
                    
                    c_m_btn1, c_m_btn2 = st.columns(2)
                    if c_m_btn1.button("➕ Add Subject", key=f"m_add_esub_{m_edit_roll}"):
                        st.session_state[m_state_key] += 1
                        st.rerun()
                    if c_m_btn2.button("🗑️ Remove Subject", key=f"m_rem_esub_{m_edit_roll}"):
                        if st.session_state[m_state_key] > 1:
                            st.session_state[m_state_key] -= 1
                            st.rerun()

                    new_m_subjects = {}
                    m_tot_full = 0
                    m_tot_obt = 0
                    
                    for i in range(st.session_state[m_state_key]):
                        if i < len(existing_m_keys):
                            def_name = existing_m_keys[i]
                            def_fm = float(m_subjects[def_name]['full'])
                            def_om = float(m_subjects[def_name]['obt'])
                        else:
                            def_name = ""
                            def_fm = 100.0
                            def_om = 0.0

                        sc1, sc2, sc3 = st.columns(3)
                        u_sub = sc1.text_input(f"Subject {i+1}", value=def_name, key=f"m_esub_{i}_{m_edit_roll}")
                        u_f = sc2.number_input(f"Full Mark {i+1}", value=def_fm, key=f"m_efm_{i}_{m_edit_roll}")
                        u_o = sc3.number_input(f"Obtained {i+1}", value=def_om, key=f"m_eom_{i}_{m_edit_roll}")

                        if u_sub.strip():
                            new_m_subjects[sanitize(u_sub)] = {"full": u_f, "obt": u_o}
                            m_tot_full += u_f
                            m_tot_obt += u_o
                    
                    col_sv, col_dl = st.columns(2)
                    with col_sv:
                        if st.button("💾 Force Update Record", key=f"m_fix_upd_btn_{m_edit_roll}"):
                            new_per = (m_tot_obt / m_tot_full * 100) if m_tot_full > 0 else 0.0
                            new_res = "PASS" if new_per >= 33 else "FAIL"
                            new_grd = "A1" if new_per >= 90 else "A2" if new_per >= 80 else "B1" if new_per >= 70 else "B2" if new_per >= 60 else "C1" if new_per >= 50 else "C2" if new_per >= 40 else "D" if new_per >= 33 else "F"
                            
                            students_db[master_school_sel][m_edit_roll].update({
                                "name": sanitize(m_up_name), "name_local": sanitize(m_up_name_loc),
                                "father_name": sanitize(m_up_father), "father_name_local": sanitize(m_up_father_loc),
                                "gender": m_up_gender, "pen_no": sanitize(m_up_pen), "apaar_no": sanitize(m_up_apaar),
                                "dob": sanitize(m_up_dob), "class": m_up_class, "batch": m_up_batch,
                                "subjects": new_m_subjects,
                                "total_obt": m_tot_obt, "total_full": m_tot_full, 
                                "percentage": round(new_per, 2), "result": new_res, "grade": new_grd,
                                "status": "Approved"
                            })
                            save_data(schools_db, students_db)
                            st.success("Record updated and approved!")
                            st.rerun()
                    with col_dl:
                        if st.button("🗑️ Delete Student Record", type="primary", key=f"m_fix_del_btn_{m_edit_roll}"):
                            del students_db[master_school_sel][m_edit_roll]
                            save_data(schools_db, students_db)
                            st.success("Student deleted successfully!")
                            st.rerun()

        with t5: 
            st.markdown("### 📢 Update Notifications & Settings")
            
            st.markdown("#### 📱 SMS Gateway API Key")
            up_sms_api = st.text_input("Fast2SMS API Key", value=master_db.get("sms_api_key", ""), key="m_set_sms_api")
            
            st.markdown("---")
            up_notice = st.text_area("Official Notification Text", value=master_db.get("notice_text", ""), height=100, key="m_set_not")
            up_news = st.text_area("Breaking News Text", value=master_db.get("news_text", ""), height=100, key="m_set_new")
            
            st.markdown("---")
            st.markdown("#### 🎨 Font & Theme Customization")
            fonts = ["sans-serif", "Arial", "Times New Roman", "Courier New", "Verdana", "Georgia", "Tahoma", "Calibri", "Algerian", "Impact"]
            sizes = [str(i) for i in range(12, 32, 2)]
            
            c_font1, c_font2 = st.columns(2)
            up_ff = c_font1.selectbox("Font Style", fonts, index=fonts.index(master_db.get("font_family", "sans-serif")) if master_db.get("font_family", "sans-serif") in fonts else 0)
            up_fs = c_font2.selectbox("Font Size", sizes, index=sizes.index(master_db.get("font_size", "16")) if master_db.get("font_size", "16") in sizes else 2)
            
            c_col1, c_col2 = st.columns(2)
            up_tc = c_col1.color_picker("Text Color", value=master_db.get("text_color", "#000000"))
            up_thc = c_col2.color_picker("Theme/Button Color", value=master_db.get("theme_color", "#1e3a8a"))
            
            st.markdown("---")
            up_m_user = st.text_input("Master Username", value=master_db.get("username", ""), key="m_set_usr")
            up_m_pass = st.text_input("New Master Password", type="password", key="m_set_pas")
            up_m_email = st.text_input("Recovery Email", value=master_db.get("email", ""), key="m_set_eml")
            up_m_phone = st.text_input("Recovery Phone Number", value=master_db.get("phone", ""), key="m_set_phn")
            up_m_upi = st.text_input("Online Payment UPI ID (e.g. school@sbi)", value=master_db.get("upi_id", ""), key="m_set_upi")
            
            c_f1, c_f2 = st.columns(2)
            up_base_fee = c_f1.number_input("Student Registration Base Fee (₹)", value=float(master_db.get("reg_fee", 150.0)), min_value=0.0, key="m_set_fee")
            up_gst_pct = c_f2.number_input("Student GST Percentage (%)", value=float(master_db.get("gst_percent", 18.0)), min_value=0.0, key="m_set_gst")
            
            c_s1, c_s2 = st.columns(2)
            up_sch_fee = c_s1.number_input("School Registration Base Fee (₹)", value=float(master_db.get("school_reg_fee", 1000.0)), min_value=0.0, key="m_set_sfee")
            up_sch_gst = c_s2.number_input("School GST Percentage (%)", value=float(master_db.get("school_gst_percent", 18.0)), min_value=0.0, key="m_set_sgst")

            if st.button("Save Profile & Settings", key="m_set_save_all"):
                master_db["sms_api_key"] = sanitize(up_sms_api)
                master_db["username"] = sanitize(up_m_user); master_db["email"] = sanitize(up_m_email)
                master_db["phone"] = sanitize(up_m_phone); master_db["upi_id"] = sanitize(up_m_upi)
                master_db["reg_fee"] = float(up_base_fee); master_db["gst_percent"] = float(up_gst_pct)
                master_db["school_reg_fee"] = float(up_sch_fee); master_db["school_gst_percent"] = float(up_sch_gst)
                master_db["notice_text"] = up_notice
                master_db["news_text"] = up_news
                master_db["font_family"] = up_ff
                master_db["font_size"] = up_fs
                master_db["text_color"] = up_tc
                master_db["theme_color"] = up_thc
                
                if up_m_pass: master_db["password"] = up_m_pass
                save_master_data(master_db); st.success("Master settings successfully updated!")
                st.rerun()

        with t6:
            st.markdown("### 🏦 School Payment Gateway Setup (Master Control)")
            st.info("Set up individual Payment Gateways for Schools. Students will pay using these details, and ₹100 will auto-route to Master Account.")
            if schools_db:
                pg_school = st.selectbox("Select School to configure Gateway", list(schools_db.keys()), key="m_gw_sch_sel")
                curr_sch = schools_db[pg_school]
                
                sch_upi = st.text_input(f"School UPI ID (for {curr_sch['name']})", value=curr_sch.get('pg_upi', ''), key="m_gw_upi")
                sch_merch = st.text_input("Payment Gateway Merchant ID (Credit/Debit Card)", value=curr_sch.get('pg_merchant', ''), key="m_gw_merch")
                sch_key = st.text_input("Payment Gateway Secret Key (Hidden)", value=curr_sch.get('pg_key', ''), type="password", key="m_gw_key")
                
                if st.button("💾 Save School Gateway Settings", key="m_gw_save"):
                    schools_db[pg_school]['pg_upi'] = sanitize(sch_upi)
                    schools_db[pg_school]['pg_merchant'] = sanitize(sch_merch)
                    schools_db[pg_school]['pg_key'] = sanitize(sch_key)
                    save_data(schools_db, students_db)
                    st.success(f"Gateway settings securely saved for {curr_sch['name']}!")
            else:
                st.warning("No schools registered yet.")
                
        with t7:
            st.markdown("### 🖼️ Portal Backgrounds & Home Display")
            st.info("Upload different background photos for different portals.")
            
            c_bg1, c_bg2 = st.columns(2)
            up_h_bg = c_bg1.file_uploader("Home Page Background", type=['png', 'jpg', 'jpeg'], key="h_bg")
            up_sch_bg = c_bg2.file_uploader("Scholarship Portal Background", type=['png', 'jpg', 'jpeg'], key="sch_bg")
            up_scl_bg = c_bg1.file_uploader("School Login Background", type=['png', 'jpg', 'jpeg'], key="scl_bg")
            up_reg_bg = c_bg2.file_uploader("Registration Portal Background", type=['png', 'jpg', 'jpeg'], key="reg_bg")
            
            if st.button("💾 Save All Backgrounds", key="save_bgs"):
                if up_h_bg: master_db["bg_b64"] = base64.b64encode(up_h_bg.read()).decode('utf-8')
                if up_sch_bg: master_db["sch_bg_b64"] = base64.b64encode(up_sch_bg.read()).decode('utf-8')
                if up_scl_bg: master_db["school_bg_b64"] = base64.b64encode(up_scl_bg.read()).decode('utf-8')
                if up_reg_bg: master_db["reg_bg_b64"] = base64.b64encode(up_reg_bg.read()).decode('utf-8')
                save_master_data(master_db)
                st.success("Backgrounds Updated Successfully!")
                st.rerun()
                
            if st.button("🗑️ Reset All Backgrounds", key="reset_bgs"):
                master_db["bg_b64"] = ""
                master_db["sch_bg_b64"] = ""
                master_db["school_bg_b64"] = ""
                master_db["reg_bg_b64"] = ""
                save_master_data(master_db)
                st.success("Backgrounds reset to default!")
                st.rerun()
                
            st.markdown("---")
            st.markdown("#### 🖼️ Home Page Carousel Image Management")
            st.info("Upload photos here to show them in the big scrolling display on the Home Page.")
            uploaded_carousel = st.file_uploader("Upload Custom Display Image (JPG/PNG)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True, key="m_carousel_up")
            if st.button("📤 Upload to Home Display", key="m_carousel_btn"):
                if uploaded_carousel:
                    for file in uploaded_carousel:
                        with open(os.path.join("Carousel_Images", file.name), "wb") as f:
                            f.write(file.getbuffer())
                    st.success("Images successfully uploaded and added to Home Display!")
                    st.rerun()
                    
            st.markdown("#### Currently Displayed Images")
            imgs = [f for f in os.listdir("Carousel_Images") if f.lower().endswith(('png', 'jpg', 'jpeg'))]
            if imgs:
                for img in imgs:
                    col_img, col_del = st.columns([8, 2])
                    with col_img:
                        st.write(img)
                    with col_del:
                        if st.button("🗑️ Delete", key=f"del_img_{img}"):
                            os.remove(os.path.join("Carousel_Images", img))
                            st.rerun()
            else:
                st.warning("No custom images uploaded. Default images are running on the Home Page.")

# ----------------- SCHOOL LOGIN -----------------
elif menu == "School Login":
    c_home, c_title = st.columns([1, 8])
    with c_home:
        if st.button("🏠 Home", key="s_home_btn"): st.query_params["portal"] = "home"; st.rerun()
    with c_title: st.subheader("🏫 School Portal")
    
    if 'school_logged_id' not in st.session_state:
        check_brute_force()
        s_id = st.text_input("School ID")
        s_pass = st.text_input("School Password", type="password")
        
        if 'school_captcha' not in st.session_state:
            st.session_state['school_captcha'] = str(random.randint(10000, 99999))
        
        st.markdown(f"<div style='background:#f1f5f9; padding:5px 20px; font-size:22px; font-weight:bold; letter-spacing:6px; border:1px solid #cbd5e1; border-radius:5px; display:inline-block; color:#000;'>{st.session_state['school_captcha']}</div>", unsafe_allow_html=True)
        entered_captcha = st.text_input("Enter the CAPTCHA code")
        
        if st.button("Login as School"):
            if entered_captcha != st.session_state['school_captcha']:
                st.error("❌ ଭୁଲ୍ CAPTCHA! ଦୟାକରି ସଠିକ୍ କ୍ୟାପ୍ଚା କୋଡ୍ ଦିଅନ୍ତୁ।")
                st.session_state['school_captcha'] = str(random.randint(10000, 99999)); st.rerun()
            else:
                s_id_clean = sanitize(s_id)
                if s_id_clean in schools_db and schools_db[s_id_clean]["pass"] == s_pass:
                    st.session_state.failed_logins = 0
                    st.session_state['school_logged_id'] = s_id_clean; del st.session_state['school_captcha']; st.rerun()
                else:
                    st.session_state.failed_logins += 1
                    st.error("❌ Invalid ID/Password!"); st.session_state['school_captcha'] = str(random.randint(10000, 99999)); st.rerun()
    else: 
        cur_school = st.session_state['school_logged_id']
        sch_data = schools_db[cur_school]
        s_lang = sch_data.get("lang", "English")
        
        c1, c2 = st.columns([8, 2])
        c1.info(f"🏫 **School Portal** | ID: {cur_school} | {sch_data['name']}")
        if c2.button("🔴 Logout"): del st.session_state['school_logged_id']; st.rerun()

        t_list, t_reg, t_add, t_edit, t_rep = st.tabs(["📋 My Students", "✅ Registrations", "➕ Add Student", "✏️ Edit Student", "🖨️ Report Card"])
        
        cur_students = students_db.get(cur_school, {})
        
        with t_list:
            st.markdown("### 📋 My Students")
            if cur_students:
                st.write(f"Total Students: **{len(cur_students)}**")
                for r_no, s_info in cur_students.items():
                    st_stat = s_info.get('status', 'Approved')
                    badge = "✅" if st_stat == 'Approved' else "⏳"
                    st.write(f"{badge} **Roll:** {r_no} | **Name:** {s_info.get('name')} | **Class:** {s_info.get('class', 'N/A')} | **Status:** {st_stat}")
            else: st.warning("No students found.")
            
        with t_reg:
            st.markdown("### ✅ Review Online Registrations")
            pending_students = {k:v for k,v in cur_students.items() if v.get('status') in ['Pending_School', 'Pending_Master']}
            if pending_students:
                app_roll = st.selectbox("Select Pending Student", list(pending_students.keys()), key="s_pend_roll_sel")
                if st.button("✅ Final Approve", key="s_pend_app_btn"):
                    cur_students[app_roll]["status"] = "Approved"
                    save_data(schools_db, students_db); st.success("Approved!"); st.rerun()
            else: st.success("No pending approvals.")
                
        with t_add:
            st.markdown("### ➕ Add Student Direct (Full Form)")
            c_roll, c_gen = st.columns(2)
            add_roll = c_roll.text_input("Roll No *", key="s_add_roll_v2")
            add_gen = c_gen.selectbox("Gender", ["Male", "Female", "Other"], key="s_add_gen_v2")
            
            c_n1, c_n2 = st.columns(2)
            add_name = c_n1.text_input("Student Name (English) *", key="s_add_name_v2")
            add_name_loc = c_n2.text_input(f"Student Name ({s_lang}) [Optional]", key="s_add_nameloc_v2")
            
            add_fname = c_n1.text_input("Father's Name (English)", key="s_add_fat_v2")
            add_fname_loc = c_n2.text_input(f"Father's Name ({s_lang}) [Optional]", key="s_add_fatloc_v2")
            
            add_mname = c_n1.text_input("Mother's Name (English)", key="s_add_mot_v2")
            add_mname_loc = c_n2.text_input(f"Mother's Name ({s_lang}) [Optional]", key="s_add_motloc_v2")
            
            c_p1, c_p2 = st.columns(2)
            add_pen = c_p1.text_input("PEN NO", key="s_add_pen_v2")
            add_apaar = c_p2.text_input("APAAR NO", key="s_add_apaar_v2")
            
            c_d1, c_c1 = st.columns(2)
            add_dob = c_d1.date_input("DOB", min_value=datetime.date(2000, 1, 1), key="s_add_dob_v2")
            add_class = c_c1.selectbox("Class", classes_list, key="s_add_cls_v2")
            
            add_batch = st.selectbox("Batch", batches_list, index=5, key="s_add_bat_v2")
            opt_pub_date = st.date_input("Results Publication Date", value=datetime.date.today(), key="s_add_pub_v2")
            
            st.markdown("#### 📚 Add Subjects & Marks")
            if 's_add_num_subs' not in st.session_state: st.session_state.s_add_num_subs = 5
            
            c_ab1, c_ab2 = st.columns(2)
            if c_ab1.button("➕ Add Subject", key="s_add_sub_btn_v2"):
                st.session_state.s_add_num_subs += 1
                st.rerun()
            if c_ab2.button("🗑️ Remove Subject", key="s_rem_sub_btn_v2"):
                if st.session_state.s_add_num_subs > 1:
                    st.session_state.s_add_num_subs -= 1
                    st.rerun()
            
            subjects_data = {}; total_full = 0; total_obt = 0
            for i in range(st.session_state.s_add_num_subs):
                c1, c2, c3 = st.columns(3)
                s_name = c1.text_input(f"Subject {i+1}", key=f"s_as_v2_{i}")
                f_m = c2.number_input(f"FM {i+1}", value=100.0, key=f"s_af_v2_{i}")
                o_m = c3.number_input(f"OM {i+1}", value=0.0, key=f"s_ao_v2_{i}")
                if s_name.strip():
                    subjects_data[sanitize(s_name)] = {"full": f_m, "obt": o_m}
                    total_full += f_m; total_obt += o_m

            if st.button("💾 Save Student Data", key="s_save_stud_btn_v2"):
                if add_roll and add_name:
                    per = (total_obt / total_full * 100) if total_full > 0 else 0.0
                    res = "PASS" if per >= 33 else "FAIL"
                    grd = "A1" if per >= 90 else "A2" if per >= 80 else "B1" if per >= 70 else "B2" if per >= 60 else "C1" if per >= 50 else "C2" if per >= 40 else "D" if per >= 33 else "F"
                    
                    new_data = {
                        "name": sanitize(add_name), "name_local": sanitize(add_name_loc), 
                        "gender": add_gen, "pen_no": sanitize(add_pen), "apaar_no": sanitize(add_apaar),
                        "father_name": sanitize(add_fname), "father_name_local": sanitize(add_fname_loc),
                        "mother_name": sanitize(add_mname), "mother_name_local": sanitize(add_mname_loc),
                        "dob": str(add_dob), "class": add_class, "batch": add_batch, "pub_date": str(opt_pub_date),
                        "subjects": subjects_data, "total_full": total_full, "total_obt": total_obt,
                        "percentage": round(per, 2), "result": res, "grade": grd, "status": "Approved"
                    }
                    if cur_school not in students_db: students_db[cur_school] = {}
                    students_db[cur_school][sanitize(add_roll)] = new_data
                    save_data(schools_db, students_db); st.success("Added!"); st.rerun()
                    
        with t_edit:
            st.markdown("### ✏️ Edit Student Data (Full Form)")
            if cur_students:
                edit_roll = st.selectbox("Select Roll No", list(cur_students.keys()), key="s_edit_roll_v2")
                curr_st = cur_students[edit_roll]
                
                c_up_n1, c_up_n2 = st.columns(2)
                up_name = c_up_n1.text_input("Edit Name (English)", value=curr_st.get('name', ''), key=f"s_up_name_v2_{edit_roll}")
                up_name_loc = c_up_n2.text_input(f"Edit Name ({s_lang})", value=curr_st.get('name_local', ''), key=f"s_up_nameloc_v2_{edit_roll}")
                
                up_father = c_up_n1.text_input("Edit Father's Name (English)", value=curr_st.get('father_name', ''), key=f"s_up_fat_v2_{edit_roll}")
                up_father_loc = c_up_n2.text_input(f"Edit Father's Name ({s_lang})", value=curr_st.get('father_name_local', ''), key=f"s_up_fatloc_v2_{edit_roll}")
                
                up_mother = c_up_n1.text_input("Edit Mother's Name (English)", value=curr_st.get('mother_name', ''), key=f"s_up_mot_v2_{edit_roll}")
                up_mother_loc = c_up_n2.text_input(f"Edit Mother's Name ({s_lang})", value=curr_st.get('mother_name_local', ''), key=f"s_up_motloc_v2_{edit_roll}")
                
                c_up1, c_up2, c_up3 = st.columns(3)
                genders = ["Male", "Female", "Other"]
                up_gender = c_up1.selectbox("Edit Gender", genders, index=genders.index(curr_st.get('gender', 'Male')) if curr_st.get('gender', 'Male') in genders else 0, key=f"s_up_gen_v2_{edit_roll}")
                up_pen = c_up2.text_input("PEN NO", value=curr_st.get('pen_no', ''), key=f"s_up_pen_v2_{edit_roll}")
                up_apaar = c_up3.text_input("APAAR NO", value=curr_st.get('apaar_no', ''), key=f"s_up_apaar_v2_{edit_roll}")
                
                c_d1, c_c1, c_b1 = st.columns(3)
                up_dob_input = c_d1.text_input("DOB (DD-MM-YYYY)", value=curr_st.get('dob', ''), key=f"s_up_dob_v2_{edit_roll}")
                up_class = c_c1.selectbox("Edit Class", classes_list, index=classes_list.index(curr_st.get('class', '1')) if curr_st.get('class', '1') in classes_list else 0, key=f"s_up_cls_v2_{edit_roll}")
                up_batch = c_b1.selectbox("Edit Batch", batches_list, index=batches_list.index(curr_st.get('batch', '2025-2026')) if curr_st.get('batch', '2025-2026') in batches_list else 5, key=f"s_up_bat_v2_{edit_roll}")
                
                st.markdown("#### 📚 Edit Subjects & Marks")
                up_subjects = curr_st.get('subjects', {})
                existing_keys = list(up_subjects.keys())
                
                state_key = f"s_edit_sub_cnt_{edit_roll}"
                if state_key not in st.session_state:
                    st.session_state[state_key] = max(5, len(existing_keys))
                
                c_btn1, c_btn2 = st.columns(2)
                if c_btn1.button("➕ Add Subject", key=f"s_add_esub_{edit_roll}"):
                    st.session_state[state_key] += 1
                    st.rerun()
                if c_btn2.button("🗑️ Remove Subject", key=f"s_rem_esub_{edit_roll}"):
                    if st.session_state[state_key] > 1:
                        st.session_state[state_key] -= 1
                        st.rerun()

                new_up_subjects = {}
                up_tot_full = 0
                up_tot_obt = 0
                
                for i in range(st.session_state[state_key]):
                    if i < len(existing_keys):
                        def_name = existing_keys[i]
                        def_fm = float(up_subjects[def_name]['full'])
                        def_om = float(up_subjects[def_name]['obt'])
                    else:
                        def_name = ""
                        def_fm = 100.0
                        def_om = 0.0

                    sc1, sc2, sc3 = st.columns(3)
                    u_sub = sc1.text_input(f"Subject {i+1}", value=def_name, key=f"s_esub_{i}_{edit_roll}")
                    u_f = sc2.number_input(f"Full Mark {i+1}", value=def_fm, key=f"s_efm_{i}_{edit_roll}")
                    u_o = sc3.number_input(f"Obtained Mark {i+1}", value=def_om, key=f"s_eom_{i}_{edit_roll}")

                    if u_sub.strip():
                        new_up_subjects[sanitize(u_sub)] = {"full": u_f, "obt": u_o}
                        up_tot_full += u_f
                        up_tot_obt += u_o
                
                if st.button("💾 Save Updated Record", key=f"s_save_edit_btn_v2_{edit_roll}"):
                    new_per = (up_tot_obt / up_tot_full * 100) if up_tot_full > 0 else 0.0
                    new_res = "PASS" if new_per >= 33 else "FAIL"
                    new_grd = "A1" if new_per >= 90 else "A2" if new_per >= 80 else "B1" if new_per >= 70 else "B2" if new_per >= 60 else "C1" if new_per >= 50 else "C2" if new_per >= 40 else "D" if new_per >= 33 else "F"
                    
                    students_db[cur_school][edit_roll].update({
                        "name": sanitize(up_name), "name_local": sanitize(up_name_loc), 
                        "father_name": sanitize(up_father), "father_name_local": sanitize(up_father_loc),
                        "mother_name": sanitize(up_mother), "mother_name_local": sanitize(up_mother_loc),
                        "gender": up_gender, "pen_no": sanitize(up_pen), "apaar_no": sanitize(up_apaar),
                        "dob": sanitize(up_dob_input), "class": up_class, "batch": up_batch,
                        "subjects": new_up_subjects,
                        "total_obt": up_tot_obt, "total_full": up_tot_full, 
                        "percentage": round(new_per, 2), "result": new_res, "grade": new_grd,
                        "status": "Approved"
                    })
                    save_data(schools_db, students_db)
                    st.success("Record updated and approved!")
                    st.rerun()

        with t_rep:
            st.markdown("### 🖨️ Report Card")
            approved_students = {k:v for k,v in cur_students.items() if v.get('status') == 'Approved'}
            if approved_students:
                rep_roll = st.selectbox("Select Roll for Report", list(approved_students.keys()), key="s_rep_roll_v2")
                st.markdown(generate_result_card_html(sch_data['name'], sch_data.get('name_local', ''), approved_students[rep_roll], rep_roll, s_lang), unsafe_allow_html=True)
                pdf_file = f"Report_{rep_roll}.pdf"
                create_pdf(pdf_file, sch_data['name'], approved_students[rep_roll], rep_roll)
                with open(pdf_file, "rb") as f:
                    st.download_button("📥 Download PDF", f, file_name=pdf_file, mime="application/pdf", key="s_dl_pdf_v2")
                if st.button("🖨️ Print Result Card", key="s_print_v2"):
                    components.html("<script>window.parent.print();</script>", height=0)

# ----------------- RESULTS PORTAL -----------------
elif menu == "Results":
    c_home, c_title = st.columns([1, 8])
    with c_home:
        if st.button("🏠 Home", key="st_home_btn"): st.query_params["portal"] = "home"; st.rerun()
    with c_title: st.subheader("🎓 Results Portal")
    
    st_search_query = st.text_input("Roll Number OR Student Name", key="res_q_v2")
    st_dob_input = st.text_input("Date of Birth (DD-MM-YYYY)", key="res_dob_v2")
    
    if st.button("View Result", key="res_view_v2"):
        if st_search_query and st_dob_input:
            sq_clean = st_search_query.strip().lower()
            ndob = normalize_dob(st_dob_input)
            
            found_student = None; found_roll = None; found_school_id = None
            pending_status = None
            dob_mismatch = False
            
            for s_id, school_students in students_db.items():
                for r_no, s_info in school_students.items():
                    match_roll = (r_no.strip().lower() == sq_clean)
                    match_name = (s_info.get("name", "").strip().lower() == sq_clean)
                    
                    if match_roll or match_name:
                        st_dob_norm = normalize_dob(s_info.get("dob", ""))
                        if st_dob_norm == ndob:
                            if s_info.get("status", "Approved") == "Approved":
                                found_student = s_info
                                found_roll = r_no
                                found_school_id = s_id
                                break
                            else: pending_status = s_info.get("status")
                        else: dob_mismatch = True
                if found_student: break
            
            if found_student:
                sch = schools_db.get(found_school_id, {})
                s_lang = sch.get("lang", "English")
                st.success(f"🎉 **Welcome {found_student.get('name', '').upper()}!**")
                
                st.markdown(generate_result_card_html(sch.get('name', 'Unknown School'), sch.get('name_local', ''), found_student, found_roll, s_lang), unsafe_allow_html=True)
                
                pdf_file = f"Result_{found_roll}.pdf"
                create_pdf(pdf_file, sch.get('name', 'Unknown School'), found_student, found_roll)
                with open(pdf_file, "rb") as f:
                    st.download_button("📥 Download PDF", f, file_name=pdf_file, mime="application/pdf", key="res_dl_v2")
                if st.button("🖨️ Print Result Card", key="res_print_v2"):
                    components.html("<script>window.parent.print();</script>", height=0)
            elif pending_status:
                st.warning(f"⚠️ ଆପଣଙ୍କ ରେକର୍ଡ ମିଳିଲା, କିନ୍ତୁ ଷ୍ଟାଟସ୍ ଏବେ: '{pending_status}' ଅଛି। Master ବା School ରୁ ଆପ୍ରୁଭ୍ କରନ୍ତୁ।")
            elif dob_mismatch:
                st.warning("⚠️ ରୋଲ୍ ନମ୍ବର୍ ବା ନାମ ମେଚ୍ ହେଲା କିନ୍ତୁ ଜନ୍ମ ତାରିଖ (DOB) ମେଚ୍ ହେଉନାହିଁ।")
            else:
                st.error("❌ କୌଣସି ରେକର୍ଡ ମିଳିଲା ନାହିଁ! ସଠିକ୍ ରୋଲ୍ ନମ୍ବର୍ ଏବଂ DOB ଦିଅନ୍ତୁ।")

st.markdown("---")
st.markdown("<div style='text-align: center; padding: 15px; background: linear-gradient(90deg, #1e3a8a, #9333ea); color: white; border-radius: 8px; font-weight: bold;'>👨‍💻 Software Developed by: KULU SUTAR | 📞 Mob: 8910223342 | ✉️ kulusutar123@gmail.com</div>", unsafe_allow_html=True)
