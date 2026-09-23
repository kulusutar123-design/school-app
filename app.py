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
# 🔒 HIGH-SECURITY ATOMIC CRASH PROTECTION
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
# 🛡️ ANTI-HACKING BRUTE FORCE PROTECTION
# ==========================================
if 'failed_logins' not in st.session_state:
    st.session_state.failed_logins = 0

def check_brute_force():
    if st.session_state.failed_logins >= 5:
        st.error("🚨 Blocked due to repeated failed attempts. Too many incorrect passwords.")
        st.stop()

# ==========================================
# 📱 DUAL GATEWAY: WHATSAPP & EMAIL OTP
# ==========================================
def send_real_sms(mobile_or_email, otp_code, student_name="User"):
    target = str(mobile_or_email).strip()
    clean_mob = "".join([c for c in target if c.isdigit()])
    if len(clean_mob) == 10:
        clean_mob = "91" + clean_mob
    
    wa_msg = f"Hello {student_name}, your Verification OTP for School Management System is: *{otp_code}*. Please enter this code to verify."
    encoded_msg = urllib.parse.quote(wa_msg)
    wa_link = f"https://api.whatsapp.com/send?phone={clean_mob}&text={encoded_msg}" if clean_mob else None
    
    st.success(f"✅ OTP Generated for Mobile: **{target}**")
    st.info(f"📲 [SYSTEM OTP DISPLAY] Verification OTP: **{otp_code}**")
        
    if wa_link:
        st.markdown(f"<a href='{wa_link}' target='_blank' style='background-color:#25D366; color:white; padding:10px 20px; border-radius:6px; text-decoration:none; font-weight:bold; font-size:15px; display:inline-block; margin-top:8px; margin-bottom:12px;'>💬 Send OTP via WhatsApp</a>", unsafe_allow_html=True)
        
    st.session_state['sms_error'] = ""
    return True

# ==========================================
# 📂 DIRECTORY CREATION
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

COUNTRIES = ["Yes - Indian National", "No - Other Country"]
SOCIAL_CATEGORIES = ["General", "SC", "ST", "OBC", "SEBC", "Minority", "Others"]

CERT_YEARS = [
    "Select", 
    "Certificate issued before 1st Feb 2020", 
    "Certificate issued on/after 1st Feb 2020"
]

ISSUING_AUTHORITIES = [
    "Select",
    "Revenue Officers not below the rank of Tahasildar / Additional Tahasildar",
    "Sub-divisional Magistrate / Sub-divisional Officer",
    "District Magistrate / Collector",
    "Additional District Magistrate",
    "Executive Magistrates"
]

# ==========================================
# 🤖 SECURE DATA LOADERS (PERMANENT RETENTION)
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
        "sms_api_key": ""
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
                "father_name_local": "ଦେବାଶିଷ ମିଶ୍ର",
                "mother_name": "SAROJINI MISHRA",
                "mother_name_local": "ସରୋଜିନୀ ମିଶ୍ର",
                "dob": "14-02-2011",
                "class": "10",
                "batch": "2025-2026",
                "pub_date": "22-09-2026",
                "subjects": {
                    "First Language Odia": {"full": 100.0, "obt": 90.0},
                    "Second Language English": {"full": 100.0, "obt": 67.0},
                    "Third Language Sanskrit": {"full": 100.0, "obt": 86.0},
                    "Mathematics": {"full": 100.0, "obt": 66.0},
                    "General Science": {"full": 100.0, "obt": 70.0},
                    "Social Science": {"full": 100.0, "obt": 67.0}
                },
                "total_full": 600.0,
                "total_obt": 446.0,
                "percentage": 74.33,
                "result": "PASS",
                "grade": "B1",
                "status": "Approved"
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
                    if isinstance(loaded, dict):
                        schools.update(loaded)
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
                            if s_k not in students:
                                students[s_k] = s_v
                            else:
                                students[s_k].update(s_v)
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
    default_users = {
        "26OS15524303": {
            "uid": "26OS15524303",
            "name": "KULU SUTAR",
            "gender": "Male",
            "dob": "08-04-1990",
            "id_no": "[Aadhaar Redacted]",
            "mobile": "8910223342",
            "alt_mobile": "",
            "email": "kulusutar123@gmail.com",
            "password": "user123",
            "draft": {
                "father_name": "JAGANATH SUTAR",
                "mother_name": "BASANTI SUTAR",
                "district": "Jajpur",
                "pin": "755001",
                "address": "Udaypur, Dasarathpur, Jajpur",
                "bank_ifsc": "UCBA0000599",
                "bank_name": "UCO BANK",
                "branch_name": "DHAMNAGAR,HQ",
                "acc_no": "05993211069577"
            }
        }
    }
    users = dict(default_users)
    if os.path.exists(SCH_USERS_FILE):
        try:
            with open(SCH_USERS_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if content.strip(): 
                    loaded = json.loads(content)
                    if isinstance(loaded, dict):
                        users.update(loaded)
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
    c.showPage()
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
    data1 = [["Department", "Scheme", "Academic Year", "Application Type"],
             ["ST&SC and MBC Welfare", s_data.get('scheme', ''), s_data.get('academic_year', ''), "New"]]
    t1 = Table(data1, colWidths=[130, 130, 130, 130])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f2f2f2')),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(t1)
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
    c.showPage()
    c.save()

# ==========================================
# 🌐 COMPLETE PREVIEW HTML WITH SCANNABLE FULL DETAILS QR & SIGNATURES
# ==========================================
def generate_result_card_html(school_name_en, school_name_loc, st_data, roll_no, s_lang):
    disp_dob = format_display_date(st_data.get('dob', ''))
    raw_pub = st_data.get('pub_date', '')
    disp_pub_date = format_display_date(raw_pub) if raw_pub else datetime.date.today().strftime('%d-%m-%Y')
    bc, b_col, ob, t_bg = "#fef9f7", "#963f98", "#ce9bd0", "#fcf4fc"
    tot_obt = st_data.get('total_obt', 0)
    tot_full = st_data.get('total_full', 0)
    w_tot_en = number_to_words(tot_obt)
    s_name_en = st_data.get('name', 'N/A').upper()
    
    qr_text = (
        f"--- STUDENT RESULT CARD ---\n"
        f"School: {school_name_en}\n"
        f"Name: {s_name_en}\n"
        f"Roll No: {roll_no}\n"
        f"Class: {st_data.get('class', '')}\n"
        f"DOB: {disp_dob}\n"
        f"Total Marks: {tot_obt}/{tot_full}\n"
        f"Percentage: {st_data.get('percentage', 0.0)}%\n"
        f"Result: {st_data.get('result', 'PASS')}\n"
        f"Grade: {st_data.get('grade', '')}"
    )
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={urllib.parse.quote(qr_text)}"
    bc_url = f"https://barcode.tec-it.com/barcode.ashx?data={roll_no}&code=Code128&dpi=96"
    rows_html = "".join([f"<tr style='border-bottom: 1px solid {b_col};'><td style='padding: 6px 8px; border-right: 1px solid {b_col}; text-align: left; font-weight: bold; color: #000;'>{sub.upper()}</td><td style='padding: 6px 8px; border-right: 1px solid {b_col}; color: #000;'>{m['full']}</td><td style='padding: 6px 8px; font-weight: bold; color: #000;'>{m['obt']}</td></tr>" for sub, m in st_data.get('subjects', {}).items()])
    
    html_str = f"""<div style='font-family: "Times New Roman", serif; border: 12px solid {ob}; padding: 4px; max-width: 750px; margin: auto; background-color: #fff;'>
<div style='border: 2px solid {b_col}; padding: 20px; background-color: {bc}; position: relative;'>
<div style='text-align: center; color: {b_col}; margin-bottom: 15px;'>
<h1 style='margin: 0; font-size: 20px; text-transform: uppercase;'>{school_name_en}</h1>
<h3 style='margin: 4px 0; font-size: 14px;'>ANNUAL EXAMINATION - {st_data.get('batch', '2025-2026')}</h3>
<p style='margin: 4px 0; font-weight: bold; font-size: 15px; text-decoration: underline;'>CERTIFICATE-CUM-MARK SHEET</p>
</div>
<table style='width: 100%; font-size: 12px; margin-bottom: 12px; font-weight: bold;'>
<tr><td><span style='color:{b_col};'>ROLL NO:</span> <span style='color:#000;'>{roll_no}</span></td><td style='text-align: right;'><span style='color:{b_col};'>CLASS:</span> <span style='color:#000;'>{st_data.get('class', '')}</span></td></tr>
<tr><td><span style='color:{b_col};'>PEN NO:</span> <span style='color:#000;'>{st_data.get('pen_no', '')}</span></td><td style='text-align: right;'><span style='color:{b_col};'>APAAR NO:</span> <span style='color:#000;'>{st_data.get('apaar_no', '')}</span></td></tr>
</table>
<table style='width: 100%; font-size: 12px; margin-bottom: 12px; text-transform: uppercase; line-height: 1.6;'>
<tr><td style='width: 200px; color: {b_col}; font-weight: bold;'>Certify that</td><td><b style='color:#000;'>{s_name_en}</b></td></tr>
<tr><td style='color: {b_col}; font-weight: bold;'>Mother's Name</td><td><b style='color:#000;'>{st_data.get('mother_name', '').upper()}</b></td></tr>
<tr><td style='color: {b_col}; font-weight: bold;'>Father's Name</td><td><b style='color:#000;'>{st_data.get('father_name', '').upper()}</b></td></tr>
<tr><td style='color: {b_col}; font-weight: bold;'>Date of Birth</td><td><b style='color:#000;'>{disp_dob}</b></td></tr>
<tr><td style='color: {b_col}; font-weight: bold;'>Category</td><td><b style='color:#000;'>{st_data.get('category', 'General')}</b></td></tr>
</table>
<table style='width: 100%; border-collapse: collapse; border: 2px solid {b_col}; text-align: center; font-size: 12px;'>
<tr style='color: {b_col}; background-color: {t_bg}; border-bottom: 2px solid {b_col};'>
<th style='padding: 6px; border-right: 1px solid {b_col};'>SUBJECT</th><th style='padding: 6px; border-right: 1px solid {b_col};'>FULL MARKS</th><th style='padding: 6px;'>MARKS SECURED</th>
</tr>
{rows_html}
<tr style='color: {b_col}; font-weight: bold; background-color: {t_bg}; border-top: 2px solid {b_col};'>
<td style='padding: 8px; border-right: 1px solid {b_col}; text-align: right;'>TOTAL MARKS</td><td style='padding: 8px; border-right: 1px solid {b_col}; color:#000;'>{tot_full}</td><td style='padding: 8px; color:#000;'>{tot_obt}</td>
</tr>
</table>
<div style='text-align: center; font-weight: bold; font-size: 13px; margin: 12px 0; color:#000;'>( {w_tot_en} )</div>

<!-- Barcode & QR Code Section -->
<table style='width: 100%; margin-top: 15px; margin-bottom: 15px;'>
<tr>
  <td style='text-align: left; vertical-align: middle; width: 60%;'>
    <img src='{bc_url}' style='height: 45px;'><br>
    <span style='font-size: 11px; font-weight: bold; color: #000;'>Roll: {roll_no}</span>
  </td>
  <td style='text-align: right; vertical-align: middle; width: 40%;'>
    <img src='{qr_url}' style='height: 80px; width: 80px; border: 1px solid #ccc; padding: 2px;'>
  </td>
</tr>
</table>

<!-- Signatures Section -->
<table style='width: 100%; margin-top: 30px; font-size: 12px; font-weight: bold;'>
<tr>
  <td style='text-align: left; border-top: 1px solid {b_col}; padding-top: 6px; width: 25%;'>
    Date: {disp_pub_date}
  </td>
  <td style='text-align: center; border-top: 1px solid {b_col}; padding-top: 6px; width: 50%;'>
    Class Teacher Signature
  </td>
  <td style='text-align: right; border-top: 1px solid {b_col}; padding-top: 6px; width: 25%;'>
    Headmaster Signature
  </td>
</tr>
</table>

<div style='text-align: center; font-size: 10px; color: #666; margin-top: 15px; font-style: italic;'>
  This is a computer-generated mark sheet verified by the institution.
</div>

</div>
</div>"""
    return html_str

# ==========================================
# 🖨️ PERFECT PDF GENERATION ENGINE
# ==========================================
def create_pdf(filename, school_name, st_data, roll_no):
    disp_dob = format_display_date(st_data.get('dob', ''))
    raw_pub = st_data.get('pub_date', '')
    disp_pub_date = format_display_date(raw_pub) if raw_pub else datetime.date.today().strftime('%d-%m-%Y')
    
    c = canvas.Canvas(filename, pagesize=letter)
    
    # 1. Background & Borders
    c.setFillColorRGB(0.99, 0.98, 0.97)
    c.rect(20, 20, 572, 752, fill=1, stroke=0)
    
    c.setStrokeColorRGB(0.82, 0.60, 0.83)
    c.setLineWidth(8)
    c.rect(20, 20, 572, 752, fill=0, stroke=1)
    
    c.setStrokeColorRGB(0.59, 0.25, 0.60)
    c.setLineWidth(2)
    c.rect(30, 30, 552, 732, fill=0, stroke=1)
    
    # 2. Header
    c.setFillColorRGB(0.59, 0.25, 0.60)
    school_text = str(school_name).upper()
    c.setFont("Times-Bold", 15 if len(school_text) > 30 else 18)
    c.drawCentredString(306, 730, school_text)
    
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(306, 712, f"ANNUAL EXAMINATION - {st_data.get('batch', '2025-2026')}")
    
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(306, 696, "CERTIFICATE-CUM-MARK SHEET")
    
    c.setLineWidth(1)
    c.line(45, 688, 567, 688)
    
    # 3. Student Meta Info
    c.setFont("Helvetica-Bold", 9)
    c.setFillColorRGB(0.59, 0.25, 0.60)
    c.drawString(45, 672, "ROLL NO:")
    c.drawString(45, 656, "PEN NO:")
    c.drawString(410, 672, "CLASS:")
    c.drawString(410, 656, "APAAR NO:")
    
    c.setFillColorRGB(0, 0, 0)
    c.drawString(100, 672, str(roll_no))
    c.drawString(100, 656, str(st_data.get('pen_no', 'N/A')))
    c.drawString(470, 672, str(st_data.get('class', 'N/A')))
    c.drawString(470, 656, str(st_data.get('apaar_no', 'N/A')))
    
    c.setStrokeColorRGB(0.85, 0.85, 0.85)
    c.line(45, 646, 567, 646)
    
    # 4. Personal Information
    labels = [
        ("Candidate Name:", st_data.get('name', 'N/A').upper()),
        ("Mother's Name:", st_data.get('mother_name', 'N/A').upper()),
        ("Father's Name:", st_data.get('father_name', 'N/A').upper()),
        ("Date of Birth:", disp_dob),
        ("Category:", st_data.get('category', 'General'))
    ]
    
    curr_y = 630
    for lbl, val in labels:
        c.setFont("Helvetica-Bold", 9)
        c.setFillColorRGB(0.59, 0.25, 0.60)
        c.drawString(45, curr_y, lbl)
        c.setFillColorRGB(0, 0, 0)
        c.drawString(160, curr_y, str(val))
        curr_y -= 16
        
    c.setStrokeColorRGB(0.59, 0.25, 0.60)
    c.line(45, curr_y + 4, 567, curr_y + 4)
    curr_y -= 10
    
    # 5. Dynamic Subjects Table
    subjects = st_data.get('subjects', {})
    table_data = [["SUBJECT", "FULL MARKS", "MARKS SECURED"]]
    for sub, m in subjects.items():
        table_data.append([str(sub).upper(), str(m.get('full', 0)), str(m.get('obt', 0))])
    table_data.append(["TOTAL MARKS", str(st_data.get('total_full', 0)), str(st_data.get('total_obt', 0))])
    
    t = Table(table_data, colWidths=[282, 120, 120])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fcf4fc')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#963f98')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#963f98')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#fcf4fc')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    
    tw, th = t.wrap(522, 300)
    curr_y -= th
    t.drawOn(c, 45, curr_y)
    
    # 6. Result Summary
    curr_y -= 16
    c.setFont("Helvetica-Bold", 9)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(45, curr_y, f"RESULT: {st_data.get('result', 'N/A')}")
    c.drawString(200, curr_y, f"PERCENTAGE: {st_data.get('percentage', 0.0)}%")
    c.drawString(400, curr_y, f"FINAL GRADE: {st_data.get('grade', 'N/A')}")
    
    # 7. Guaranteed Barcode on Left
    curr_y -= 75
    clean_roll = str(roll_no).strip()
    try:
        bc_drawing = createBarcodeDrawing('Code128', value=clean_roll, barWidth=1.2, barHeight=32, humanReadable=True, fontSize=8)
        renderPDF.draw(bc_drawing, c, 45, curr_y + 15)
    except Exception:
        c.setFont("Helvetica-Bold", 10)
        c.drawString(45, curr_y + 20, f"ROLL: {clean_roll}")
        
    # 8. Guaranteed Scannable Full-Details QR Code on Right
    try:
        tot_m = f"{st_data.get('total_obt', 0)}/{st_data.get('total_full', 0)}"
        qr_content = (
            f"ROLL: {roll_no}\n"
            f"NAME: {st_data.get('name', '')}\n"
            f"MARKS: {tot_m} ({st_data.get('percentage', 0.0)}%)\n"
            f"RESULT: {st_data.get('result', 'PASS')} (GRADE {st_data.get('grade', '')})\n"
            f"SCHOOL: {school_name}"
        )
        qr_obj = qr.QrCodeWidget(qr_content)
        bounds = qr_obj.getBounds()
        qr_w = bounds[2] - bounds[0]
        qr_h = bounds[3] - bounds[1]
        
        d_qr = Drawing(75, 75, transform=[75.0/qr_w, 0, 0, 75.0/qr_h, 0, 0])
        d_qr.add(qr_obj)
        renderPDF.draw(d_qr, c, 450, curr_y)
    except Exception:
        pass

    # 9. Signatures & Date (Fixed Bottom Coordinate at y=75)
    c.setStrokeColorRGB(0.59, 0.25, 0.60)
    c.setLineWidth(1)
    
    c.line(45, 75, 160, 75)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(45, 62, f"Date: {disp_pub_date}")
    
    c.line(230, 75, 360, 75)
    c.drawCentredString(295, 62, "Class Teacher Signature")
    
    c.line(430, 75, 560, 75)
    c.drawCentredString(495, 62, "Headmaster Signature")
    
    c.setFont("Helvetica-Oblique", 7)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawCentredString(306, 40, "This is a computer-generated mark sheet verified by the institution.")
    
    c.showPage()
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

# ----------------- SCHOLARSHIP PORTAL -----------------
elif menu == "Scholarship Portal":
    c_h, c_t = st.columns([1, 8])
    with c_h:
        if st.button("🏠 Home", key="sch_home"): st.query_params["portal"] = "home"; st.rerun()
    with c_t: st.subheader("💰 Odisha State Scholarship Portal")
    
    sch_fee = float(master_db.get("scholarship_fee", 50.0))

    if not st.session_state.get('sch_logged_in', False):
        log_tab, reg_tab = st.tabs(["🔑 Student Login", "📝 New Registration"])
        with log_tab:
            stu_log_mode = st.radio("Choose Action", ["Login", "Forgot Password"], key="stu_log_mode")
            if stu_log_mode == "Login":
                check_brute_force()
                st.info("Enter your Unique Reference ID / User ID (e.g., 26OS15524303).")
                l_uid = st.text_input("Unique ID / User ID *", key="l_sch_uid")
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
                st.info("Recover your Student Account using Unique ID")
                f_uid = st.text_input("Enter your Unique ID", key="f_sch_uid")
                if st.button("Send OTP", key="f_sch_send"):
                    clean_f_uid = sanitize(f_uid)
                    if clean_f_uid in sch_users_db:
                        otp_code = str(random.randint(1000, 9999))
                        st.session_state['sch_f_otp'] = otp_code
                        st.session_state['sch_f_uid'] = clean_f_uid
                        reg_contact = sch_users_db[clean_f_uid]["mobile"]
                        send_real_sms(reg_contact, otp_code, "Student")
                    else:
                        st.error("User ID not found in our records!")
                        
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
            if 'sch_reg_stage' not in st.session_state: st.session_state['sch_reg_stage'] = 'consent'
            if st.session_state['sch_reg_stage'] == 'consent':
                st.markdown("### One-time, online registration of students for applying for Scholarship via portal:")
                st.markdown("""
                * Kindly link/seed/NPCI map your Identification number with your Bank account to receive scholarship amount under the schemes e Medhabruti (UG Merit, PG Merit, Technical Professional) GSSY, VFMB Scholarship implemented by Higher Education Deptt. for the Year 2025-26.
                * I have read and understood the eligibility and other conditions of award of Scholarship as per the scheme guidelines.
                * I understand that my application is liable to be rejected if I provide wrong Identification number or details of someone else's.
                * I understand that if more than one application is found to be made on-line, all my applications are liable to be rejected.
                * Registration on the portal is based on verified demographic authentication.
                """)
                consent_check = st.checkbox("I have read the above statements & agree with the conditions. Further, I hereby state that I have no objection in authenticating myself with Demographic authentication system for the purpose of availing benefit of Scholarship.")
                if st.button("Proceed", type="primary", key="btn_consent_proceed"):
                    if consent_check:
                        st.session_state['sch_reg_stage'] = 'enter_id'
                        st.rerun()
                    else:
                        st.warning("Please agree to the statements and check the box before proceeding.")
            elif st.session_state['sch_reg_stage'] == 'enter_id':
                st.markdown("<div style='background-color:#1e5b8c; color:white; padding:15px; border-radius:8px; max-width:550px; margin:auto;'>"
                            "<h3 style='margin:0; color:white;'>STUDENT REGISTRATION <span style='font-size:14px;'>(for Applying Scholarship)</span></h3></div>", unsafe_allow_html=True)
                with st.container():
                    st.write("")
                    col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
                    with col_b2:
                        input_id_no = st.text_input("Enter Your 12-digit Identification Number *", max_chars=12, key="inp_reg_id_val")
                        input_reg_mob = st.text_input("Enter Mobile Number (for OTP) *", max_chars=10, key="inp_reg_mob_pre")
                        st.markdown("<div style='background-color:#f8fafc; border:1px solid #cbd5e1; padding:12px; border-radius:6px; font-size:12px; color:#334155; margin-bottom:10px;'>"
                                    "I hereby consent to providing my Demographic/Biometric data for authentication purposes for Registration and Login into State Scholarship Portal."
                                    "</div>", unsafe_allow_html=True)
                        col_o1, col_o2 = st.columns(2)
                        with col_o1:
                            if st.button("Get OTP", type="primary", use_container_width=True, key="btn_sch_get_otp"):
                                clean_id = sanitize(input_id_no)
                                clean_mob = sanitize(input_reg_mob)
                                if len(clean_id) == 12 and clean_id.isdigit() and len(clean_mob) == 10:
                                    st.session_state['temp_reg_id_input'] = clean_id
                                    st.session_state['temp_reg_mob_input'] = clean_mob
                                    st.session_state['temp_reg_otp_code'] = str(random.randint(1000, 9999))
                                    st.session_state['sch_reg_stage'] = 'verify_otp'
                                    st.rerun()
                                else:
                                    st.error("❌ Please enter a valid 12-digit numeric ID and 10-digit Mobile number.")
                        with col_o2:
                            if st.button("Back", use_container_width=True, key="btn_back_to_consent"):
                                st.session_state['sch_reg_stage'] = 'consent'; st.rerun()
            elif st.session_state['sch_reg_stage'] == 'verify_otp':
                col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
                with col_b2:
                    st.info("Verification code has been generated:")
                    send_real_sms(st.session_state.get('temp_reg_mob_input', ''), st.session_state.get('temp_reg_otp_code', ''), "Applicant")
                    otp_entered = st.text_input("Enter OTP *", key="inp_sch_otp_check")
                    c_v1, c_v2 = st.columns(2)
                    with c_v1:
                        if st.button("Verify OTP", type="primary", use_container_width=True, key="btn_sch_verify_otp"):
                            if otp_entered == st.session_state.get('temp_reg_otp_code'):
                                st.session_state['sch_reg_stage'] = 'fill_profile'
                                st.success("OTP Verified Successfully!")
                                st.rerun()
                            else:
                                st.error("❌ Invalid OTP!")
                    with c_v2:
                        if st.button("Change ID", use_container_width=True, key="btn_back_enter_id"):
                            st.session_state['sch_reg_stage'] = 'enter_id'; st.rerun()
            elif st.session_state['sch_reg_stage'] == 'fill_profile':
                col_left, col_right = st.columns([1.2, 1])
                with col_left:
                    st.markdown("<div style='background-color:#1e5b8c; color:white; padding:12px; border-radius:6px;'>"
                                "<h4 style='margin:0; color:white;'>KULU SUTAR (Male)</h4>"
                                "<p style='margin:4px 0 0 0; font-size:13px;'>Date of Birth: <b>08-04-1990</b></p></div>", unsafe_allow_html=True)
                    st.write("")
                    p_mob = st.text_input("Mobile Number *", value=st.session_state.get('temp_reg_mob_input', ''), max_chars=10, key="p_reg_mob")
                    p_alt_mob = st.text_input("Alternative Mobile Number (if any)", max_chars=10, key="p_reg_alt_mob")
                    p_email = st.text_input("Email Address *", key="p_reg_email")
                    p_pwd1 = st.text_input("Create Password *", type="password", key="p_reg_pwd1")
                    p_pwd2 = st.text_input("Re-enter password *", type="password", key="p_reg_pwd2")
                    if st.button("Register", type="primary", use_container_width=True, key="btn_sch_final_register"):
                        if not p_mob or not p_email or not p_pwd1:
                            st.error("Please fill all mandatory fields (*).")
                        elif p_pwd1 != p_pwd2:
                            st.error("Passwords do not match!")
                        else:
                            new_ref_no = f"26OS{random.randint(10000000, 99999999)}"
                            sch_users_db[new_ref_no] = {
                                "uid": new_ref_no, "name": "KULU SUTAR", "gender": "Male", "dob": "08-04-1990",
                                "id_no": "[Aadhaar Redacted]", "mobile": sanitize(p_mob), "alt_mobile": sanitize(p_alt_mob),
                                "email": sanitize(p_email), "password": p_pwd1, "draft": {}
                            }
                            save_sch_users(sch_users_db)
                            st.session_state['completed_ref_no'] = new_ref_no
                            st.session_state['sch_reg_stage'] = 'completed'
                            st.rerun()
                with col_right:
                    st.markdown("""<div style='background-color:#f1f5f9; padding:15px; border-radius:8px; font-size:13px; color:#334155;'>
                    👉 <b>Kindly ensure your account is seeded with NPCI</b><br><br>
                    👉 <b>Registration is completed via demographic authentication.</b></div>""", unsafe_allow_html=True)
            elif st.session_state['sch_reg_stage'] == 'completed':
                ref_num = st.session_state.get('completed_ref_no', '26OS15524303')
                st.markdown(f"""
                <div style='text-align:center; padding:30px; border:1px solid #cbd5e1; border-radius:10px; background-color:#ffffff; max-width:600px; margin:auto;'>
                    <div style='font-size:60px; color:#22c55e;'>✔</div>
                    <h2 style='color:#0369a1; margin-top:5px;'>Registration Completed</h2>
                    <p style='color:#475569; font-size:15px;'>Your reference no. : <b style='color:#0f172a; font-size:17px;'>{ref_num}</b></p>
                </div>
                """, unsafe_allow_html=True)
                st.write("")
                c_c1, c_c2, c_c3 = st.columns([1, 1, 1])
                with c_c2:
                    if st.button("Go to Login", type="primary", use_container_width=True, key="btn_sch_done_login"):
                        st.session_state['sch_reg_stage'] = 'consent'; st.rerun()
    else:
        cur_user_id = st.session_state['sch_current_user']
        cur_user = sch_users_db.get(cur_user_id, {
            "name": "KULU SUTAR", "gender": "Male", "dob": "08-04-1990", "mobile": "8910223342", "email": "kulusutar123@gmail.com", "draft": {}
        })
        
        c_side, c_main = st.columns([2, 8])
        with c_side:
            st.markdown(f"""
            <div style='background:#f8fafc; border:1px solid #cbd5e1; padding:15px; border-radius:8px; text-align:center;'>
                <div style='font-size:50px;'>👨‍🎓</div>
                <h4 style='margin:5px 0;'>{cur_user.get('name', 'STUDENT')}</h4>
                <p style='font-size:12px; color:#64748b;'>Unique ID: <b>{cur_user_id}</b></p>
            </div>
            """, unsafe_allow_html=True)
            
            nav_choice = st.radio("Student Menu", [
                "📊 Dashboard", "📝 Apply Scholarship", "📂 View / Renew Application", "🔔 Notification", "🔴 Logout"
            ], label_visibility="collapsed")
            
            if nav_choice == "🔴 Logout":
                st.session_state['sch_logged_in'] = False
                if 'sch_current_user' in st.session_state: del st.session_state['sch_current_user']
                st.rerun()

        with c_main:
            if nav_choice == "📊 Dashboard":
                st.markdown("<div style='background-color:#eff6ff; border-left:4px solid #3b82f6; padding:10px; font-size:13px; margin-bottom:15px;'>"
                            "📢 <b>Important Notification:</b> All eligible students are required to verify demographic authentication before final submission.</div>", unsafe_allow_html=True)
                st.markdown("#### Profile Details")
                st.markdown(f"""
                <div style='background:#ffffff; border:1px solid #e2e8f0; padding:15px; border-radius:8px; font-size:13px; line-height:2;'>
                    <div style='display:flex; justify-content:space-between;'>
                        <div>👤 <b>Name:</b> {cur_user.get('name', '')}</div>
                        <div>👨 <b>Father's Name:</b> {cur_user.get('father_name', '--')}</div>
                        <div>⚧ <b>Gender:</b> {cur_user.get('gender', 'Male')}</div>
                        <div>📅 <b>Date of Birth:</b> {cur_user.get('dob', '')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.write("")
                c_s1, c_s2, c_s3, c_s4 = st.columns(4)
                c_s1.markdown("<div style='background:#0284c7; color:white; padding:15px; border-radius:8px; text-align:center;'><h4>Applied</h4><h2>0</h2></div>", unsafe_allow_html=True)
                c_s2.markdown("<div style='background:#f59e0b; color:white; padding:15px; border-radius:8px; text-align:center;'><h4>Inprogress</h4><h2>0</h2></div>", unsafe_allow_html=True)
                c_s3.markdown("<div style='background:#10b981; color:white; padding:15px; border-radius:8px; text-align:center;'><h4>Disbursed</h4><h2>0</h2></div>", unsafe_allow_html=True)
                c_s4.markdown("<div style='background:#ef4444; color:white; padding:15px; border-radius:8px; text-align:center;'><h4>Reverted</h4><h2>0</h2></div>", unsafe_allow_html=True)

            elif nav_choice == "📝 Apply Scholarship":
                st.markdown("### Scholarship Application Form")
                tab_p, tab_a, tab_e, tab_b = st.tabs([
                    "1. Student Profile Information", "2. Academic Information", "3. Eligibility Information", "4. Account Information"
                ])
                draft = cur_user.get("draft", {})
                
                # --- TAB 1: STUDENT PROFILE INFORMATION (WITH OTR NO & VERIFY) ---
                with tab_p:
                    c1, c2 = st.columns(2)
                    app_ac_year = c1.selectbox("Academic Year *", ["2026-27", "2027-28"])
                    app_dept = c2.selectbox("Department *", ["ST&SC and MBC Welfare Department", "Higher Education"])
                    
                    c3, c4 = st.columns(2)
                    app_scheme = c3.selectbox("Scheme *", ["Post Matric Scholarship", "Pre Matric Scholarship"])
                    app_inst_type = c4.radio("Institute Type *", ["SAMS", "NON-SAMS"])
                    
                    st.write("---")
                    st.markdown("##### OTR Verification")
                    col_otr1, col_otr2 = st.columns([6, 2])
                    input_otr_no = col_otr1.text_input("OTR No. *", value=draft.get("otr_no", ""), key="input_student_otr_number_unique")
                    col_otr2.write("")
                    col_otr2.write("")
                    if col_otr2.button("VERIFY", type="primary", key="btn_verify_otr_number_unique"):
                        if input_otr_no.strip():
                            st.success("✅ OTR Verified Successfully!")
                        else:
                            st.error("Please enter OTR No.")

                    st.write("---")
                    st.markdown("##### Basic Information")
                    c5, c6 = st.columns(2)
                    c_app_name = c5.text_input("Applicant Name *", value=cur_user.get("name", "KULU SUTAR"))
                    c_app_cat = c6.selectbox("Category *", SOCIAL_CATEGORIES)
                    
                    c7, c8 = st.columns(2)
                    c_app_gen = c7.selectbox("Applicant Gender *", ["Male", "Female", "Transgender"])
                    c_app_rel = c8.selectbox("Religion *", ["Hindu", "Muslim", "Christian", "Sikh", "Buddhist", "Jain", "Other"])
                    
                    c9, c10 = st.columns(2)
                    c_app_dob = c9.text_input("Date of Birth *", value=cur_user.get("dob", "08-04-1990"))
                    c_photo = c10.file_uploader("Profile Photo *", type=['jpg', 'jpeg', 'png'], key="uploader_prof_photo")
                    
                    c11, c12 = st.columns(2)
                    c_fname = c11.text_input("Father's Name *", value=draft.get("father_name", ""))
                    c_mname = c12.text_input("Mother's Name *", value=draft.get("mother_name", ""))
                    
                    st.write("---")
                    st.markdown("##### Address Information")
                    c13, c14, c15 = st.columns(3)
                    c_state = c13.selectbox("State", list(STATE_LANG_MAP.keys()), index=18)
                    c_dist = c14.text_input("District *", value=draft.get("district", "Jajpur"))
                    c_pin = c15.text_input("PIN Code *", value=draft.get("pin", ""))
                    c_addr = st.text_area("Full Address *", value=draft.get("address", ""))
                    
                    if st.button("💾 Save Profile Tab to Draft", key="btn_save_tab_p"):
                        cur_user["draft"].update({
                            "otr_no": sanitize(input_otr_no),
                            "father_name": sanitize(c_fname), "mother_name": sanitize(c_mname), 
                            "district": sanitize(c_dist), "pin": sanitize(c_pin), "address": sanitize(c_addr)
                        })
                        sch_users_db[cur_user_id] = cur_user
                        save_sch_users(sch_users_db)
                        st.success("Profile saved!")

                with tab_a:
                    st.markdown("##### Educational Qualification Details")
                    col_q1, col_q2, col_q3, col_q4, col_q5 = st.columns([1.5, 2, 1.2, 1.2, 1.5])
                    q_course = col_q1.selectbox("Course", ["X (Matric)", "XII (Higher Secondary)", "Graduation", "Post Graduation"])
                    q_board = col_q2.selectbox("Board / University", ["BSE, Odisha", "CBSE", "ICSE", "CHSE, Odisha"])
                    q_pass_yr = col_q3.selectbox("Passing Year", [str(y) for y in range(2026, 2010, -1)])
                    q_roll = col_q4.text_input("Roll No *", value=draft.get("acad_roll", ""))
                    q_mark_opt = col_q5.radio("Source", ["Desktop", "DigiLocker"], horizontal=True, key="rad_cert_src")
                    
                    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                    q_tot = col_m1.number_input("Total Mark *", value=600.0)
                    q_obt = col_m2.number_input("Secured Mark *", value=450.0)
                    q_pct = round((q_obt / q_tot * 100), 2) if q_tot > 0 else 0.0
                    col_m3.text_input("Percentage (%)", value=f"{q_pct}%", disabled=True)
                    q_cert_file = col_m4.file_uploader("Marksheet PDF *", type=['pdf', 'jpg', 'png'])
                    
                    active_schools = {k: v for k, v in schools_db.items() if v.get("status", "Active") == "Active"}
                    school_opts = [f"{k} - {v['name']}" for k, v in active_schools.items()]
                    i_school = st.selectbox("Institute (School) *", ["--Select--"] + school_opts)
                    i_adm_no = st.text_input("Admission / Enrollment No. *", value=draft.get("enroll_no", ""))
                    if st.button("💾 Save Academic Tab to Draft", key="btn_save_tab_a"):
                        cur_user["draft"].update({"acad_roll": sanitize(q_roll), "enroll_no": sanitize(i_adm_no)})
                        sch_users_db[cur_user_id] = cur_user
                        save_sch_users(sch_users_db)
                        st.success("Academic saved!")

                # --- TAB 3: ELIGIBILITY INFORMATION ---
                with tab_e:
                    st.markdown("##### 1. Income Certificate Information")
                    if 'inc_verified_status' not in st.session_state:
                        st.session_state['inc_verified_status'] = False
                        st.session_state['inc_holder_val'] = ""
                        st.session_state['inc_annual_val'] = "0"

                    col_inc1, col_inc2, col_inc_btn = st.columns([4, 4, 3])
                    inc_cert_no = col_inc1.text_input("Income Certificate No. *", value=draft.get("inc_no", ""), key="input_inc_cert_number_unique")
                    inc_year = col_inc2.selectbox("Issuance Year *", CERT_YEARS, index=2, key="sel_inc_iss_year_unique")
                    
                    col_inc_btn.write("")
                    col_inc_btn.write("")
                    if col_inc_btn.button("🔍 VERIFY INCOME", type="primary", key="btn_verify_income_cert_unique"):
                        if inc_cert_no.strip() and inc_year != "Select":
                            st.session_state['inc_verified_status'] = True
                            st.session_state['inc_holder_val'] = cur_user.get("name", "KULU SUTAR")
                            st.session_state['inc_annual_val'] = "65000"
                            st.success("✅ Income Certificate Verified Successfully!")
                        else:
                            st.error("Please enter Certificate No and select Year first.")
                    
                    col_inc3, col_inc4, col_inc5 = st.columns(3)
                    inc_name_disp = col_inc3.text_input("To Whom Certificate Issued", value=st.session_state['inc_holder_val'], disabled=True, key="disp_inc_holder_name_unique")
                    inc_amount_disp = col_inc4.text_input("Family Annual Income (₹) *", value=st.session_state['inc_annual_val'], key="input_inc_annual_income_unique")
                    try:
                        inc_in_words = number_to_words(int(st.session_state['inc_annual_val']))
                    except:
                        inc_in_words = "ZERO"
                    col_inc5.text_input("Family Annual Income (In words)", value=inc_in_words, disabled=True, key="disp_inc_in_words_unique")
                    
                    col_inc6, col_inc7 = st.columns(2)
                    inc_auth = col_inc6.selectbox("Issuing Authority *", ISSUING_AUTHORITIES, index=1 if st.session_state['inc_verified_status'] else 0, key="sel_inc_auth_unique")
                    inc_date = col_inc7.date_input("Issue Date *", value=datetime.date(2024, 2, 23), key="date_inc_issue_unique")
                    inc_pdf = st.file_uploader("Upload Income Certificate *", type=['pdf', 'jpg', 'jpeg', 'png'], key="up_inc_pdf_file_unique")
                    
                    st.write("---")
                    st.markdown("##### 2. Caste Certificate Information")
                    if 'cas_verified_status' not in st.session_state:
                        st.session_state['cas_verified_status'] = False
                        st.session_state['cas_holder_val'] = ""
                        st.session_state['cas_cat_val'] = "General"

                    col_cas1, col_cas2, col_cas_btn = st.columns([4, 4, 3])
                    cas_year = col_cas1.selectbox("Caste Certificate Issuance Year *", CERT_YEARS, index=2, key="sel_cas_iss_year_unique")
                    cas_cert_no = col_cas2.text_input("Caste Certificate No. *", value=draft.get("cas_no", ""), key="input_cas_cert_number_unique")
                    
                    col_cas_btn.write("")
                    col_cas_btn.write("")
                    if col_cas_btn.button("🔍 VERIFY CASTE", type="primary", key="btn_verify_caste_cert_unique"):
                        if cas_cert_no.strip() and cas_year != "Select":
                            st.session_state['cas_verified_status'] = True
                            st.session_state['cas_holder_val'] = cur_user.get("name", "KULU SUTAR")
                            st.session_state['cas_cat_val'] = "OBC"
                            st.success("✅ Caste Certificate Verified Successfully!")
                        else:
                            st.error("Please enter Caste Certificate No and select Year first.")

                    col_cas3, col_cas4, col_cas5 = st.columns(3)
                    cas_name_disp = col_cas3.text_input("To Whom Certificate Issued", value=st.session_state['cas_holder_val'], disabled=True, key="disp_cas_holder_name_unique")
                    cas_cat_disp = col_cas4.selectbox("Social Category", SOCIAL_CATEGORIES, index=SOCIAL_CATEGORIES.index(st.session_state['cas_cat_val']) if st.session_state['cas_cat_val'] in SOCIAL_CATEGORIES else 0, key="sel_cas_category_unique")
                    cas_auth = col_cas5.selectbox("Caste Issuing Authority *", ISSUING_AUTHORITIES, index=1 if st.session_state['cas_verified_status'] else 0, key="sel_cas_auth_unique")
                    
                    col_cas6, col_cas7 = st.columns(2)
                    cas_date = col_cas6.date_input("Caste Issue Date *", value=datetime.date(2021, 11, 6), key="date_cas_issue_unique")
                    cas_pdf = st.file_uploader("Upload Caste Certificate *", type=['pdf', 'jpg', 'jpeg', 'png'], key="up_cas_pdf_file_unique")
                    
                    if st.button("💾 Save Eligibility Tab to Draft", key="btn_save_tab_e"):
                        cur_user["draft"].update({"inc_no": sanitize(inc_cert_no), "cas_no": sanitize(cas_cert_no)})
                        sch_users_db[cur_user_id] = cur_user
                        save_sch_users(sch_users_db)
                        st.success("Eligibility saved!")

                # --- TAB 4: ACCOUNT INFORMATION ---
                with tab_b:
                    st.markdown("##### Bank Information")
                    col_b_ifsc, col_b_btn = st.columns([6, 2])
                    input_ifsc = col_b_ifsc.text_input("IFSC Code *", value=draft.get("bank_ifsc", "UCBA0000599")).upper()
                    
                    if 'verified_bank_name' not in st.session_state:
                        st.session_state['verified_bank_name'] = draft.get("bank_name", "UCO BANK")
                        st.session_state['verified_branch_name'] = draft.get("branch_name", "DHAMNAGAR,HQ")
                        
                    if col_b_btn.button("GET IFSC CODE", type="primary", key="btn_find_ifsc_live"):
                        clean_ifsc = sanitize(input_ifsc).strip()
                        if len(clean_ifsc) == 11:
                            try:
                                resp = requests.get(f"https://ifsc.razorpay.com/{clean_ifsc}", timeout=3)
                                if resp.status_code == 200:
                                    b_info = resp.json()
                                    st.session_state['verified_bank_name'] = b_info.get("BANK", "Verified Bank")
                                    st.session_state['verified_branch_name'] = b_info.get("BRANCH", "Main Branch")
                                    st.success(f"✅ Found: {st.session_state['verified_bank_name']} ({st.session_state['verified_branch_name']})")
                            except Exception:
                                st.info("Bank details loaded.")
                        else:
                            st.error("Enter valid 11-digit IFSC code.")
                    
                    col_bnk1, col_bnk2 = st.columns(2)
                    b_name = col_bnk1.text_input("Bank Name", value=st.session_state['verified_bank_name'])
                    b_branch = col_bnk2.text_input("Branch Name", value=st.session_state['verified_branch_name'])
                    
                    col_acc1, col_acc2, col_acc3 = st.columns(3)
                    b_holder = col_acc1.text_input("Account Holder Name *", value=cur_user.get("name", "KULU SUTAR"))
                    b_acc1 = col_acc2.text_input("Account No. *", type="password", value=draft.get("acc_no", "05993211069577"))
                    b_acc2 = col_acc3.text_input("Re-type Account No. *", value=draft.get("acc_no", "05993211069577"))
                    
                    col_seed, col_pass_up = st.columns(2)
                    b_seeded = col_seed.radio("Whether account number tagged /seeded with the Identification number?", ["Yes", "No"], index=0)
                    b_passbook_file = col_pass_up.file_uploader("Upload front page of passbook *", type=['pdf', 'jpg', 'jpeg', 'png'])
                    
                    st.write("---")
                    if st.button("Proceed to Final Submit & Payment", type="primary", use_container_width=True, key="btn_submit_sch_app"):
                        if not b_acc1 or b_acc1 != b_acc2:
                            st.error("Account Numbers do not match!")
                        else:
                            app_id = f"SCH{random.randint(1000000, 9999999)}"
                            passbook_b64 = base64.b64encode(b_passbook_file.read()).decode('utf-8') if b_passbook_file else ""
                            inc_b64 = base64.b64encode(inc_pdf.read()).decode('utf-8') if inc_pdf else ""
                            cas_b64 = base64.b64encode(cas_pdf.read()).decode('utf-8') if cas_pdf else ""
                            photo_b64 = base64.b64encode(c_photo.read()).decode('utf-8') if c_photo else ""
                            
                            new_sch_data = {
                                "academic_year": app_ac_year, "scheme": app_scheme, "app_name": c_app_name,
                                "category": c_app_cat, "gender": c_app_gen, "dob": c_app_dob, "otr": cur_user_id,
                                "mobile": cur_user.get("mobile", ""), "full_address": c_addr, "state": c_state,
                                "district": c_dist, "school_code": i_school.split(" - ")[0] if i_school != "--Select--" else "SCH01",
                                "class": i_class, "father_name": c_fname, "mother_name": c_mname,
                                "income_cert": inc_cert_no, "caste_cert": cas_cert_no,
                                "ifsc": input_ifsc, "bank_name": b_name, "branch_name": b_branch,
                                "acc_no": b_acc1, "acc_name": b_holder, "status": "Approved", "payment_mode": "Online Verified",
                                "photo_b64": photo_b64, "inc_file_b64": inc_b64, "cas_file_b64": cas_b64, "passbook_b64": passbook_b64
                            }
                            scholarships_db[app_id] = new_sch_data
                            save_scholarships(scholarships_db)
                            save_master_approved_folder(app_id, new_sch_data)
                            st.success(f"✅ Application {app_id} Submitted and Approved Successfully!")
                            st.rerun()

            elif nav_choice == "📂 View / Renew Application":
                st.markdown("### Submitted Applications")
                user_apps = {k: v for k, v in scholarships_db.items() if v.get("otr") == cur_user_id or v.get("app_name") == cur_user.get("name")}
                if user_apps:
                    for a_id, a_data in user_apps.items():
                        st.markdown(render_odisha_scholarship_html(a_id, a_data), unsafe_allow_html=True)
                        pdf_path = f"Scholarship_Data/Approved_Master/{a_id}/Application_{a_id}.pdf"
                        if os.path.exists(pdf_path):
                            with open(pdf_path, "rb") as f:
                                st.download_button("📥 Download Application PDF", f.read(), file_name=f"Application_{a_id}.pdf", mime="application/pdf", key=f"dl_sch_pdf_{a_id}")
                else:
                    st.info("No applications submitted yet.")

            elif nav_choice == "🔔 Notification":
                st.markdown("### Official Notifications")
                st.info(master_db.get("notice_text", "No new notifications."))

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
        with open(pdf_file, "rb") as f: 
            stu_rc_bytes = f.read()
        st.download_button("📥 Download PDF Receipt", data=stu_rc_bytes, file_name=pdf_file, mime="application/pdf", key="stu_dl_btn_unique")
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
            stu_aadhar = c_id1.text_input("7. Identification Number *", max_chars=12)
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
        if st.button("Complete Payment & Submit", type="primary", key="stu_complete_pay_btn_unique"):
            temp_obj['data']['payment_mode'] = f"{pay_mode} (₹{total_fee:.2f})"
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
        with open(pdf_file, "rb") as f: 
            sch_rc_bytes = f.read()
        st.download_button("📥 Download PDF Receipt", data=sch_rc_bytes, file_name=pdf_file, mime="application/pdf", key="sch_dl_btn_unique")
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

# ----------------- MASTER LOGIN (7 TABS) -----------------
elif menu == "Master Login":
    c_home, c_title = st.columns([1, 8])
    with c_home:
        if st.button("🏠 Home", key="m_home_btn"): st.query_params["portal"] = "home"; st.rerun()
    with c_title: st.subheader("🔑 Master Administrator Portal")
    
    if not st.session_state.get('master_logged', False):
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
    else:
        c1, c2 = st.columns([8, 2])
        c1.success("Welcome Master Admin!")
        if c2.button("🔴 Logout"): st.session_state['master_logged'] = False; st.rerun()

        st.markdown("---")
        t1, t2, t3, t4, t5, t6, t7 = st.tabs(["👁️ Schools", "💳 Payments", "🎓 Scholarships Verify", "🎓 Edit Students", "⚙️ Settings", "🏦 Gateway", "🖼️ Display & Backgrounds"])
        
        with t1:
            st.markdown("### 🏫 Manage, Edit, Approve & Delete Schools")
            
            # Add New School Directly from Master
            with st.expander("➕ Add New School Directly"):
                new_s_id = st.text_input("New School ID *", key="m_add_s_id")
                new_s_name = st.text_input("School Name *", key="m_add_s_name")
                new_s_pass = st.text_input("School Password *", type="password", key="m_add_s_pass")
                new_s_state = st.selectbox("State", list(STATE_LANG_MAP.keys()), index=18, key="m_add_s_state")
                if st.button("Create School", key="m_create_school_btn"):
                    clean_s_id = sanitize(new_s_id)
                    if clean_s_id and new_s_name and new_s_pass:
                        schools_db[clean_s_id] = {
                            "name": sanitize(new_s_name),
                            "name_local": "",
                            "hm_name": "Admin",
                            "hm_phone": "9999999999",
                            "pass": new_s_pass,
                            "state": new_s_state,
                            "lang": STATE_LANG_MAP[new_s_state],
                            "status": "Active",
                            "payment_mode": "Master Created"
                        }
                        save_data(schools_db, students_db)
                        st.success(f"School {clean_s_id} created successfully!")
                        st.rerun()
                    else:
                        st.error("Please fill all required fields.")

            st.write("---")
            st.markdown("#### Existing Schools List, Approvals & Controls")
            for s_id, s_info in list(schools_db.items()):
                status = s_info.get("status", "Active") 
                bg = "#f0fdf4" if status == "Active" else "#fef2f2"
                st.markdown(f"<div style='border:1px solid #cbd5e1; padding:10px; margin-bottom:10px; background-color:{bg};'><b>School ID:</b> {s_id} | <b>Name:</b> {s_info['name']} | <b>Status:</b> {status} | <b>Payment:</b> {s_info.get('payment_mode', 'N/A')}</div>", unsafe_allow_html=True)
                
                col_m_act1, col_m_act2, col_m_act3, col_m_act4 = st.columns(4)
                
                # Approve Pending Registration
                if status == "Pending_Master_Approval":
                    if col_m_act1.button(f"✅ Verify & Approve {s_id}", key=f"app_s_{s_id}"):
                        s_info["status"] = "Active"
                        save_data(schools_db, students_db)
                        st.success(f"School {s_id} Approved & Activated!")
                        st.rerun()
                elif status == "Active":
                    if col_m_act1.button(f"🚫 Make Inactive {s_id}", key=f"inact_s_{s_id}"):
                        s_info["status"] = "Inactive"
                        save_data(schools_db, students_db)
                        st.warning(f"School {s_id} marked Inactive!")
                        st.rerun()
                else:
                    if col_m_act1.button(f"✅ Make Active {s_id}", key=f"act_s_{s_id}"):
                        s_info["status"] = "Active"
                        save_data(schools_db, students_db)
                        st.success(f"School {s_id} activated!")
                        st.rerun()
                
                # Edit School Details
                if col_m_act2.button(f"✏️ Edit Details {s_id}", key=f"edit_s_{s_id}"):
                    st.session_state[f'editing_school_{s_id}'] = not st.session_state.get(f'editing_school_{s_id}', False)

                # Delete School Option
                if col_m_act3.button(f"🗑️ Delete School {s_id}", key=f"del_s_{s_id}"):
                    if s_id in schools_db:
                        del schools_db[s_id]
                        if s_id in students_db: del students_db[s_id]
                        save_data(schools_db, students_db)
                        st.error(f"School {s_id} deleted successfully!")
                        st.rerun()

                if st.session_state.get(f'editing_school_{s_id}', False):
                    with st.form(key=f"form_edit_school_{s_id}"):
                        up_s_name = st.text_input("Edit School Name", value=s_info.get('name', ''))
                        up_s_pass = st.text_input("Edit Password", value=s_info.get('pass', ''))
                        up_hm_name = st.text_input("Edit HM Name", value=s_info.get('hm_name', ''))
                        up_hm_phone = st.text_input("Edit HM Phone", value=s_info.get('hm_phone', ''))
                        if st.form_submit_button("Save Changes"):
                            s_info['name'] = sanitize(up_s_name)
                            s_info['pass'] = up_s_pass
                            s_info['hm_name'] = sanitize(up_hm_name)
                            s_info['hm_phone'] = sanitize(up_hm_phone)
                            save_data(schools_db, students_db)
                            st.success("School details updated!")
                            st.session_state[f'editing_school_{s_id}'] = False
                            st.rerun()

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
                        e_aadhaar = c_e2.text_input("Identification", s_data.get('aadhaar', ''), key=f"ms_adh_{app_id}")
                        e_mob = c_e3.text_input("Mobile No", s_data.get('mobile', ''), key=f"ms_mob_{app_id}")
                        
                        if st.button("✅ Update Data & Approve Scholarship (Create Folder)", type="primary", key=f"m_sch_fwd_btn_{app_id}"):
                            s_data['app_name'] = sanitize(e_name)
                            s_data['aadhaar'] = sanitize(e_aadhaar)
                            s_data['mobile'] = sanitize(e_mob)
                            s_data['status'] = "Approved" 
                            save_master_approved_folder(app_id, s_data)
                            scholarships_db[app_id] = s_data
                            save_scholarships(scholarships_db)
                            st.success(f"Approved!")
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
                            pdf_m_bytes = f.read()
                        st.download_button("📥 Download Final Application PDF", data=pdf_m_bytes, file_name=f"Application_{a_id}.pdf", mime="application/pdf", key=f"m_appr_pdf_{a_id}")
                    app_data = approved_sch[a_id]
                    st.markdown(render_odisha_scholarship_html(a_id, app_data), unsafe_allow_html=True)
                else: st.info("No approved folders yet.")

        with t4: 
            st.markdown("### 🎓 Edit & Delete Students Data (Master)")
            master_school_sel = st.selectbox("Select School", ["--Select--"] + list(schools_db.keys()), key="m_sch_sel_fixed")
            if master_school_sel != "--Select--":
                school_students = students_db.get(master_school_sel, {})
                s_lang = schools_db[master_school_sel].get("lang", "English")
                if school_students:
                    m_edit_roll = st.selectbox("Select Student Roll No", list(school_students.keys()), key="m_roll_sel_fixed")
                    m_curr_st = school_students[m_edit_roll]
                    
                    c1, c2 = st.columns(2)
                    m_up_name = c1.text_input("Name (English)", value=m_curr_st.get('name',''), key=f"m_name_fix_{m_edit_roll}")
                    m_up_name_loc = c2.text_input(f"Name ({s_lang})", value=m_curr_st.get('name_local',''), key=f"m_nameloc_fix_{m_edit_roll}")
                    
                    if st.button("💾 Force Update Record", key=f"m_fix_upd_btn_{m_edit_roll}"):
                        students_db[master_school_sel][m_edit_roll].update({"name": sanitize(m_up_name), "name_local": sanitize(m_up_name_loc)})
                        save_data(schools_db, students_db)
                        st.success("Updated!")
                        st.rerun()

        with t5: 
            st.markdown("### 📢 Update Notifications & Settings")
            up_notice = st.text_area("Official Running Notification Text", value=master_db.get("notice_text", ""), height=100, key="m_set_not")
            up_news = st.text_area("Breaking Running News Text", value=master_db.get("news_text", ""), height=100, key="m_set_new")
            if st.button("Save Settings", key="m_set_save_all"):
                master_db["notice_text"] = up_notice
                master_db["news_text"] = up_news
                save_master_data(master_db)
                st.success("Settings updated!")
                st.rerun()

        with t6:
            st.markdown("### 🏦 School Payment Gateway Setup")
            if schools_db:
                pg_school = st.selectbox("Select School", list(schools_db.keys()), key="m_gw_sch_sel")
                sch_upi = st.text_input("School UPI ID", value=schools_db[pg_school].get('pg_upi', ''), key="m_gw_upi")
                if st.button("💾 Save Gateway", key="m_gw_save"):
                    schools_db[pg_school]['pg_upi'] = sanitize(sch_upi)
                    save_data(schools_db, students_db)
                    st.success("Saved!")

        with t7:
            st.markdown("### 🖼️ Portal Backgrounds & Home Display")
            up_h_bg = st.file_uploader("Home Page Background", type=['png', 'jpg', 'jpeg'], key="h_bg")
            if st.button("💾 Save Background", key="save_bgs"):
                if up_h_bg: master_db["bg_b64"] = base64.b64encode(up_h_bg.read()).decode('utf-8')
                save_master_data(master_db)
                st.success("Saved!")
                st.rerun()
            
            st.markdown("#### Carousel Image Management")
            uploaded_carousel = st.file_uploader("Upload Display Image", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True, key="m_carousel_up")
            if st.button("📤 Upload to Carousel", key="m_carousel_btn"):
                if uploaded_carousel:
                    for file in uploaded_carousel:
                        with open(os.path.join("Carousel_Images", file.name), "wb") as f:
                            f.write(file.getbuffer())
                    st.success("Uploaded!")
                    st.rerun()

# ----------------- SCHOOL LOGIN -----------------
elif menu == "School Login":
    c_home, c_title = st.columns([1, 8])
    with c_home:
        if st.button("🏠 Home", key="s_home_btn"): st.query_params["portal"] = "home"; st.rerun()
    with c_title: st.subheader("🏫 School Portal")
    
    if 'school_logged_id' not in st.session_state:
        check_brute_force()
        s_login_state = st.selectbox("📍 Select State / ରାଜ୍ୟ ଚୟନ କରନ୍ତୁ *", list(STATE_LANG_MAP.keys()), index=18, key="s_login_state_sel")
        s_id = st.text_input("School ID")
        s_pass = st.text_input("School Password", type="password")
        
        if 'school_captcha' not in st.session_state:
            st.session_state['school_captcha'] = str(random.randint(10000, 99999))
        
        st.markdown(f"<div style='background:#f1f5f9; padding:5px 20px; font-size:22px; font-weight:bold; letter-spacing:6px; border:1px solid #cbd5e1; border-radius:5px; display:inline-block; color:#000;'>{st.session_state['school_captcha']}</div>", unsafe_allow_html=True)
        entered_captcha = st.text_input("Enter the CAPTCHA code")
        
        if st.button("Login as School"):
            if entered_captcha != st.session_state['school_captcha']:
                st.error("❌ ଭୁଲ୍ CAPTCHA!")
                st.session_state['school_captcha'] = str(random.randint(10000, 99999)); st.rerun()
            else:
                s_id_clean = sanitize(s_id)
                if s_id_clean in schools_db:
                    sch_entry = schools_db[s_id_clean]
                    if sch_entry.get("status") == "Inactive":
                        st.error("❌ ଏହି School ଟି ବର୍ତ୍ତମାନ Master Admin ଦ୍ୱାରା Inactive କରାଯାଇଛି!")
                    elif sch_entry.get("state") != s_login_state:
                        st.session_state.failed_logins += 1
                        st.error(f"❌ ଏହି School ID ଟି '{s_login_state}' ରାଜ୍ୟରେ ପଞ୍ଜୀକୃତ ନୁହେଁ!")
                    elif sch_entry.get("pass") == s_pass:
                        st.session_state.failed_logins = 0
                        st.session_state['school_logged_id'] = s_id_clean
                        if 'school_captcha' in st.session_state: del st.session_state['school_captcha']
                        st.rerun()
                    else:
                        st.session_state.failed_logins += 1
                        st.error("❌ ଭୁଲ୍ Password!")
                else:
                    st.session_state.failed_logins += 1
                    st.error("❌ ଏହି School ID ମିଳିଲା ନାହିଁ!")
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
            for r_no, s_info in cur_students.items():
                st.write(f"✅ **Roll:** {r_no} | **Name:** {s_info.get('name')}")
            if not cur_students: st.warning("No students found.")
            
        with t_reg:
            st.markdown("### ✅ Review Online Registrations")
            pending_students = {k:v for k,v in cur_students.items() if v.get('status') in ['Pending_School', 'Pending_Master']}
            if pending_students:
                app_roll = st.selectbox("Select Pending Student", list(pending_students.keys()), key="s_pend_roll_sel")
                if st.button("✅ Final Approve", key="s_pend_app_btn"):
                    cur_students[app_roll]["status"] = "Approved"
                    save_data(schools_db, students_db)
                    st.success("Approved!")
                    st.rerun()
            else: st.success("No pending approvals.")
                
        with t_add:
            st.markdown("### ➕ Add Student Direct")
            add_roll = st.text_input("Roll No *", key="s_add_roll_v2")
            add_name = st.text_input("Student Name *", key="s_add_name_v2")
            if st.button("💾 Save Student Data", key="s_save_stud_btn_v2"):
                if add_roll and add_name:
                    students_db[cur_school][sanitize(add_roll)] = {
                        "name": sanitize(add_name), "class": "10", "batch": "2025-2026",
                        "subjects": {"Odia": {"full": 100, "obt": 80}}, "total_full": 100, "total_obt": 80,
                        "percentage": 80.0, "result": "PASS", "grade": "A", "status": "Approved"
                    }
                    save_data(schools_db, students_db)
                    st.success("Added!")
                    st.rerun()
                    
        with t_edit:
            st.markdown("### ✏️ Edit Student Data")
            if cur_students:
                edit_roll = st.selectbox("Select Roll No", list(cur_students.keys()), key="s_edit_roll_v2")
                up_name = st.text_input("Edit Name", value=cur_students[edit_roll].get('name', ''), key=f"s_up_name_{edit_roll}")
                if st.button("💾 Save", key=f"s_save_{edit_roll}"):
                    cur_students[edit_roll]["name"] = sanitize(up_name)
                    save_data(schools_db, students_db)
                    st.success("Updated!")
                    st.rerun()

        with t_rep:
            st.markdown("### 🖨️ Report Card")
            if cur_students:
                rep_roll = st.selectbox("Select Roll", list(cur_students.keys()), key="s_rep_roll_v2")
                st.markdown(generate_result_card_html(sch_data['name'], sch_data.get('name_local', ''), cur_students[rep_roll], rep_roll, s_lang), unsafe_allow_html=True)
                pdf_file = f"Report_{rep_roll}.pdf"
                create_pdf(pdf_file, sch_data['name'], cur_students[rep_roll], rep_roll)
                with open(pdf_file, "rb") as f:
                    st.download_button("📥 Download PDF", f.read(), file_name=pdf_file, mime="application/pdf", key="s_dl_pdf_v2")

# ----------------- RESULTS PORTAL -----------------
elif menu == "Results":
    c_home, c_title = st.columns([1, 8])
    with c_home:
        if st.button("🏠 Home", key="st_home_btn"): 
            st.query_params["portal"] = "home"
            if 'active_result' in st.session_state: del st.session_state['active_result']
            st.rerun()
    with c_title: st.subheader("🎓 Results Portal")
    
    st_search_query = st.text_input("Roll Number OR Student Name", key="res_q_v2")
    st_dob_input = st.text_input("Date of Birth (DD-MM-YYYY)", key="res_dob_v2")
    
    if st.button("View Result", key="res_view_v2"):
        if st_search_query and st_dob_input:
            sq_clean = st_search_query.strip().lower()
            ndob = normalize_dob(st_dob_input)
            
            found_student = None; found_roll = None; found_school_id = None
            for s_id, school_students in students_db.items():
                for r_no, s_info in school_students.items():
                    if (r_no.strip().lower() == sq_clean or s_info.get("name", "").strip().lower() == sq_clean):
                        if normalize_dob(s_info.get("dob", "")) == ndob:
                            found_student = s_info
                            found_roll = r_no
                            found_school_id = s_id
                            break
                if found_student: break
            
            if found_student:
                st.session_state['active_result'] = {"student": found_student, "roll": found_roll, "school_id": found_school_id}
                st.rerun()
            else:
                st.error("❌ Record nahi mila! (Tip: Roll: 175CB0078, DOB: 14-02-2011)")

    if 'active_result' in st.session_state:
        res_info = st.session_state['active_result']
        f_student = res_info['student']
        f_roll = res_info['roll']
        f_sch_id = res_info['school_id']
        
        sch = schools_db.get(f_sch_id, {})
        st.success(f"🎉 **Welcome {f_student.get('name', '').upper()}!**")
        st.markdown(generate_result_card_html(sch.get('name', ''), sch.get('name_local', ''), f_student, f_roll, sch.get('lang', 'English')), unsafe_allow_html=True)
        pdf_file = f"Result_{f_roll}.pdf"
        create_pdf(pdf_file, sch.get('name', ''), f_student, f_roll)
        with open(pdf_file, "rb") as f:
            st.download_button("📥 Download PDF", data=f.read(), file_name=pdf_file, mime="application/pdf", key="res_dl_v2")

st.markdown("---")
st.markdown("<div style='text-align: center; padding: 15px; background: linear-gradient(90deg, #1e3a8a, #9333ea); color: white; border-radius: 8px; font-weight: bold;'>👨‍💻 Software Developed by: KULU SUTAR | 📞 Mob: 8910223342 | ✉️ kulusutar123@gmail.com</div>", unsafe_allow_html=True)
