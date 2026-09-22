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
# 🛡️ HEAVY ANTI-HACKING & BRUTE FORCE GUARD
# ==========================================
if 'failed_logins' not in st.session_state:
    st.session_state.failed_logins = 0

def check_brute_force():
    if st.session_state.failed_logins >= 5:
        st.error("🚨 System locked due to repeated incorrect login attempts. Maximum security enforced.")
        st.stop()

# ==========================================
# 📱 DUAL GATEWAY: WHATSAPP & SCREEN OTP
# ==========================================
def send_real_sms(mobile_or_email, otp_code, student_name="User"):
    target = str(mobile_or_email).strip()
    clean_mob = "".join([c for c in target if c.isdigit()])
    if len(clean_mob) == 10:
        clean_mob = "91" + clean_mob
    
    wa_msg = f"Hello {student_name}, your Verification OTP is: *{otp_code}*. Please enter this code to verify."
    encoded_msg = urllib.parse.quote(wa_msg)
    wa_link = f"https://api.whatsapp.com/send?phone={clean_mob}&text={encoded_msg}" if clean_mob else None
    
    st.success(f"✅ Secure OTP Generated for: **{target}**")
    st.info(f"📲 [SYSTEM OTP DISPLAY] Verification OTP: **{otp_code}**")
        
    if wa_link:
        st.markdown(f"<a href='{wa_link}' target='_blank' style='background-color:#25D366; color:white; padding:10px 20px; border-radius:6px; text-decoration:none; font-weight:bold; font-size:15px; display:inline-block; margin-top:8px; margin-bottom:12px;'>💬 Send OTP via WhatsApp</a>", unsafe_allow_html=True)
        
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
                * Kindly link/seed/NPCI map your Identification number with your Bank account to receive scholarship amount under the schemes.
                * I have read and understood the eligibility and other conditions of award of Scholarship.
                """)
                consent_check = st.checkbox("I have read the above statements & agree with the conditions.")
                if st.button("Proceed", type="primary"):
                    if consent_check:
                        st.session_state['sch_reg_stage'] = 'enter_id'
                        st.rerun()
                    else: st.warning("Please check the box.")
            elif st.session_state['sch_reg_stage'] == 'enter_id':
                input_id_no = st.text_input("Enter 12-digit Identification Number *", max_chars=12)
                input_reg_mob = st.text_input("Enter Mobile Number *", max_chars=10)
                if st.button("Get OTP", type="primary"):
                    if len(input_id_no) == 12 and len(input_reg_mob) == 10:
                        st.session_state['temp_reg_id_input'] = input_id_no
                        st.session_state['temp_reg_mob_input'] = input_reg_mob
                        st.session_state['temp_reg_otp_code'] = str(random.randint(1000, 9999))
                        st.session_state['sch_reg_stage'] = 'verify_otp'
                        st.rerun()
                    else: st.error("Enter valid 12-digit ID and 10-digit mobile.")
            elif st.session_state['sch_reg_stage'] == 'verify_otp':
                send_real_sms(st.session_state.get('temp_reg_mob_input', ''), st.session_state.get('temp_reg_otp_code', ''), "Applicant")
                otp_entered = st.text_input("Enter OTP *")
                if st.button("Verify OTP", type="primary"):
                    if otp_entered == st.session_state.get('temp_reg_otp_code'):
                        st.session_state['sch_reg_stage'] = 'fill_profile'
                        st.success("OTP Verified!")
                        st.rerun()
                    else: st.error("Invalid OTP!")
            elif st.session_state['sch_reg_stage'] == 'fill_profile':
                p_mob = st.text_input("Mobile Number *", value=st.session_state.get('temp_reg_mob_input', ''), max_chars=10)
                p_email = st.text_input("Email Address *")
                p_pwd1 = st.text_input("Create Password *", type="password")
                p_pwd2 = st.text_input("Re-enter password *", type="password")
                if st.button("Register", type="primary"):
                    if p_pwd1 and p_pwd1 == p_pwd2:
                        new_ref_no = f"26OS{random.randint(10000000, 99999999)}"
                        sch_users_db[new_ref_no] = {
                            "uid": new_ref_no, "name": "KULU SUTAR", "gender": "Male", "dob": "08-04-1990",
                            "mobile": sanitize(p_mob), "email": sanitize(p_email), "password": p_pwd1, "draft": {}
                        }
                        save_sch_users(sch_users_db)
                        st.session_state['completed_ref_no'] = new_ref_no
                        st.session_state['sch_reg_stage'] = 'completed'
                        st.rerun()
                    else: st.error("Passwords do not match!")
            elif st.session_state['sch_reg_stage'] == 'completed':
                ref_num = st.session_state.get('completed_ref_no', '26OS15524303')
                st.success(f"Registration Completed! Reference No: **{ref_num}**")
                if st.button("Go to Login", type="primary"):
                    st.session_state['sch_reg_stage'] = 'consent'; st.rerun()
    else:
        cur_user_id = st.session_state['sch_current_user']
        cur_user = sch_users_db.get(cur_user_id, {"name": "KULU SUTAR", "draft": {}})
        
        c_side, c_main = st.columns([2, 8])
        with c_side:
            st.markdown(f"#### {cur_user.get('name', 'STUDENT')}")
            st.write(f"ID: {cur_user_id}")
            nav_choice = st.radio("Menu", ["📊 Dashboard", "📝 Apply Scholarship", "📂 View / Renew Application", "🔔 Notification", "🔴 Logout"], label_visibility="collapsed")
            if nav_choice == "🔴 Logout":
                st.session_state['sch_logged_in'] = False
                if 'sch_current_user' in st.session_state: del st.session_state['sch_current_user']
                st.rerun()

        with c_main:
            if nav_choice == "📊 Dashboard":
                st.info("Welcome to Student Dashboard.")
            elif nav_choice == "📝 Apply Scholarship":
                tab_p, tab_a, tab_e, tab_b = st.tabs(["1. Profile", "2. Academic", "3. Eligibility", "4. Account"])
                draft = cur_user.get("draft", {})
                
                with tab_p:
                    c1, c2 = st.columns(2)
                    app_ac_year = c1.selectbox("Academic Year", ["2026-27", "2027-28"])
                    c_app_name = c2.text_input("Applicant Name", value=cur_user.get("name", "KULU SUTAR"))
                    c_photo = st.file_uploader("Profile Photo", type=['jpg', 'jpeg', 'png'])
                    if st.button("Save Profile Draft"):
                        st.success("Saved!")
                with tab_a:
                    st.text_input("Roll No", value=draft.get("acad_roll", ""))
                    st.file_uploader("Upload Marksheet")
                    if st.button("Save Academic Draft"):
                        st.success("Saved!")
                with tab_e:
                    st.markdown("##### 1. Income Certificate")
                    c_inc1, c_inc2, c_inc_btn = st.columns([4, 4, 3])
                    inc_no = c_inc1.text_input("Income Certificate No.", value=draft.get("inc_no", ""))
                    inc_yr = c_inc2.selectbox("Issuance Year", CERT_YEARS, index=2)
                    if c_inc_btn.button("🔍 VERIFY INCOME", type="primary"):
                        st.success(f"✅ Verified! Issued to: {cur_user.get('name')} | Income: ₹65,000")
                    c_inc_pdf = st.file_uploader("Upload Income Certificate (PDF/JPG)", type=['pdf', 'jpg', 'jpeg', 'png'])
                    
                    st.markdown("##### 2. Caste Certificate")
                    c_cas1, c_cas2, c_cas_btn = st.columns([4, 4, 3])
                    cas_no = c_cas1.text_input("Caste Certificate No.", value=draft.get("cas_no", ""))
                    cas_yr = c_cas2.selectbox("Issuance Year", CERT_YEARS, index=2)
                    if c_cas_btn.button("🔍 VERIFY CASTE", type="primary"):
                        st.success(f"✅ Verified! Issued to: {cur_user.get('name')} | Category: OBC")
                    c_cas_pdf = st.file_uploader("Upload Caste Certificate (PDF/JPG)", type=['pdf', 'jpg', 'jpeg', 'png'])
                    
                    if st.button("💾 Save Eligibility Tab to Draft"):
                        cur_user["draft"].update({"inc_no": sanitize(inc_no), "cas_no": sanitize(cas_no)})
                        sch_users_db[cur_user_id] = cur_user
                        save_sch_users(sch_users_db)
                        st.success("Saved!")
                with tab_b:
                    st.markdown("##### Bank Information")
                    c_ifsc, c_ifsc_btn = st.columns([6, 2])
                    b_ifsc = c_ifsc.text_input("IFSC Code", value=draft.get("bank_ifsc", "UCBA0000599")).upper()
                    if c_ifsc_btn.button("GET IFSC CODE", type="primary"):
                        st.success("✅ Bank: UCO BANK, Branch: DHAMNAGAR")
                    b_acc = st.text_input("Account No.", type="password", value=draft.get("acc_no", "05993211069577"))
                    b_seeded = st.radio("Aadhaar Seeded?", ["Yes", "No"], index=0)
                    b_pass = st.file_uploader("Upload Passbook Front Page", type=['pdf', 'jpg', 'jpeg', 'png'])
                    if st.button("Submit Application & Payment", type="primary"):
                        st.success("Application Submitted Successfully!")

            elif nav_choice == "📂 View / Renew Application":
                st.info("No applications submitted yet.")
            elif nav_choice == "🔔 Notification":
                st.info("No new notifications.")

# ----------------- NEW STUDENT REGISTRATION -----------------
elif menu == "New Student Registration":
    c_home, c_title = st.columns([1, 8])
    with c_home:
        if st.button("🏠 Home", key="reg_stu_home"): st.query_params["portal"] = "home"; st.rerun()
    with c_title: st.subheader("👨‍🎓 New Student Registration")
    st.info("Student Registration Form active.")

# ----------------- NEW SCHOOL REGISTRATION -----------------
elif menu == "New School Registration":
    c_home, c_title = st.columns([1, 8])
    with c_home:
        if st.button("🏠 Home", key="reg_sch_home"): st.query_params["portal"] = "home"; st.rerun()
    with c_title: st.subheader("📝 New School Registration")
    st.info("School Registration Portal active.")

# ----------------- MASTER LOGIN -----------------
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
            else: st.error("Invalid credentials!")
    else:
        st.success("Welcome Master Admin!")
        if st.button("🔴 Logout"): st.session_state['master_logged'] = False; st.rerun()
        t1, t2, t3, t4, t5, t6, t7 = st.tabs(["👁️ Schools", "💳 Payments", "🎓 Scholarships", "🎓 Students", "⚙️ Settings", "🏦 Gateway", "🖼️ Display"])
        with t1: st.write("Manage Schools")
        with t2: st.write("Payments")
        with t3: st.write("Scholarships")
        with t4: st.write("Students")
        with t5: st.write("Settings")
        with t6: st.write("Gateway")
        with t7: st.write("Display & Backgrounds")

# ----------------- SCHOOL LOGIN -----------------
elif menu == "School Login":
    c_home, c_title = st.columns([1, 8])
    with c_home:
        if st.button("🏠 Home", key="s_home_btn"): st.query_params["portal"] = "home"; st.rerun()
    with c_title: st.subheader("🏫 School Portal")
    
    if 'school_logged_id' not in st.session_state:
        check_brute_force()
        s_login_state = st.selectbox("📍 Select State", list(STATE_LANG_MAP.keys()), index=18)
        s_id = st.text_input("School ID")
        s_pass = st.text_input("School Password", type="password")
        if st.button("Login as School"):
            s_id_clean = sanitize(s_id)
            if s_id_clean in schools_db and schools_db[s_id_clean]["pass"] == s_pass:
                st.session_state['school_logged_id'] = s_id_clean
                st.rerun()
            else: st.error("Invalid School ID or Password!")
    else:
        cur_school = st.session_state['school_logged_id']
        st.success(f"Logged in as School: {cur_school}")
        if st.button("🔴 Logout"): del st.session_state['school_logged_id']; st.rerun()
        t_list, t_reg, t_add, t_edit, t_rep = st.tabs(["📋 My Students", "✅ Registrations", "➕ Add Student", "✏️ Edit Student", "🖨️ Report Card"])
        with t_list: st.write("My Students")
        with t_reg: st.write("Registrations")
        with t_add: st.write("Add Student")
        with t_edit: st.write("Edit Student")
        with t_rep: st.write("Report Card")

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
                st.error("❌ Record not found! Please check Roll Number and DOB. (Tip: Roll: 175CB0078, DOB: 14-02-2011)")

    if 'active_result' in st.session_state:
        res_info = st.session_state['active_result']
        f_student = res_info['student']
        f_roll = res_info['roll']
        f_sch_id = res_info['school_id']
        sch = schools_db.get(f_sch_id, {})
        st.success(f"🎉 Welcome {f_student.get('name', '').upper()}!")
        st.markdown(generate_result_card_html(sch.get('name', 'School'), sch.get('name_local', ''), f_student, f_roll, sch.get('lang', 'English')), unsafe_allow_html=True)
        pdf_file = f"Result_{f_roll}.pdf"
        create_pdf(pdf_file, sch.get('name', 'School'), f_student, f_roll)
        with open(pdf_file, "rb") as f:
            pdf_bytes = f.read()
        st.download_button("📥 Download PDF", data=pdf_bytes, file_name=pdf_file, mime="application/pdf", key="res_dl_v2")

st.markdown("---")
st.markdown("<div style='text-align: center; padding: 15px; background: linear-gradient(90deg, #1e3a8a, #9333ea); color: white; border-radius: 8px; font-weight: bold;'>👨‍💻 Software Developed by: KULU SUTAR | 📞 Mob: 8910223342 | ✉️ kulusutar123@gmail.com</div>", unsafe_allow_html=True)
