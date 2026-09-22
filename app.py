import streamlit as st
import streamlit.components.v1 as components
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.graphics.barcode import createBarcodeDrawing, qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
import json
import os
import io
import datetime
import random
import urllib.parse
import html
import threading
import base64

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
    
    if "@" in target:
        st.success(f"✅ OTP Generated for Email: **{target}**")
        st.info(f"📧 [EMAIL OTP NOTIFICATION] Hello {student_name}, your OTP is: **{otp_code}**")
    else:
        st.success(f"✅ OTP Generated for Mobile: **{target}**")
        st.info(f"📲 [SYSTEM OTP FALLBACK] Verification OTP: **{otp_code}**")
        
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
        except Exception:
            st.error("CRITICAL ERROR: schools.json is corrupted.")
            st.stop()
    if os.path.exists(STUDENTS_FILE):
        try:
            with open(STUDENTS_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if content.strip(): students = json.loads(content)
        except Exception:
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

def create_student_receipt_pdf(reg_id, s_data):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
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
    buf.seek(0)
    return buf.getvalue()

def render_odisha_scholarship_html(app_id, s_data):
    masked_id = "XXXXXXXX" + str(s_data.get('aadhaar', ''))[-4:]
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
<tr><td style="background-color: #f9f9f9;"><b>ID Status</b></td><td>{masked_id}</td><td style="background-color: #f9f9f9;"><b>Category</b></td><td>{s_data.get('category', '')}</td></tr>
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

def create_school_receipt_pdf(sch_id, sch_data):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
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
    buf.seek(0)
    return buf.getvalue()

# ==========================================
# 🌐 COMPLETE PREVIEW HTML WITH BARCODE, QR & SIGNATURES
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
    
    # Text encoded into QR code
    qr_text = (
        f"--- STUDENT RESULT CARD ---\n"
        f"School: {school_name_en}\n"
        f"Name: {s_name_en}\n"
        f"Roll No: {roll_no}\n"
        f"Class: {st_data.get('class', '')}\n"
        f"DOB: {disp_dob}\n"
        f"Marks: {tot_obt}/{tot_full}\n"
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
def create_pdf_bytes(school_name, st_data, roll_no):
    disp_dob = format_display_date(st_data.get('dob', ''))
    raw_pub = st_data.get('pub_date', '')
    disp_pub_date = format_display_date(raw_pub) if raw_pub else datetime.date.today().strftime('%d-%m-%Y')
    
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    
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
    
    # 7. Guaranteed Native Offline Barcode (Left)
    curr_y -= 65
    clean_roll = str(roll_no).strip()
    try:
        bc_drawing = createBarcodeDrawing('Code128', value=clean_roll, width=160, height=35, humanReadable=True)
        renderPDF.draw(bc_drawing, c, 45, curr_y + 10)
    except Exception:
        c.setFont("Helvetica-Bold", 10)
        c.drawString(45, curr_y + 15, f"ROLL: {clean_roll}")
        
    # 8. Guaranteed Native Offline QR Code with Full Details (Right)
    try:
        tot_m = f"{st_data.get('total_obt', 0)}/{st_data.get('total_full', 0)}"
        qr_content = (
            f"--- STUDENT RESULT CARD ---\n"
            f"School: {school_name}\n"
            f"Name: {st_data.get('name', '')}\n"
            f"Roll No: {roll_no}\n"
            f"Class: {st_data.get('class', '')}\n"
            f"DOB: {disp_dob}\n"
            f"Marks: {tot_m}\n"
            f"Percentage: {st_data.get('percentage', 0.0)}%\n"
            f"Result: {st_data.get('result', 'PASS')}\n"
            f"Grade: {st_data.get('grade', '')}"
        )
        qr_obj = qr.QrCodeWidget(qr_content)
        bounds = qr_obj.getBounds()
        qr_w = bounds[2] - bounds[0]
        qr_h = bounds[3] - bounds[1]
        
        d_qr = Drawing(58, 58, transform=[58.0/qr_w, 0, 0, 58.0/qr_h, 0, 0])
        d_qr.add(qr_obj)
        renderPDF.draw(d_qr, c, 460, curr_y)
    except Exception:
        pass

    # 9. Signatures & Date (Fixed Bottom Coordinate)
    c.setStrokeColorRGB(0.59, 0.25, 0.60)
    c.setLineWidth(1)
    
    # Date
    c.line(45, 75, 160, 75)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(45, 62, f"Date: {disp_pub_date}")
    
    # Class Teacher Signature
    c.line(230, 75, 360, 75)
    c.drawCentredString(295, 62, "Class Teacher Signature")
    
    # Headmaster Signature
    c.line(430, 75, 560, 75)
    c.drawCentredString(495, 62, "Headmaster Signature")
    
    c.setFont("Helvetica-Oblique", 7)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawCentredString(306, 40, "This is a computer-generated mark sheet verified by the institution.")
    
    c.showPage()
    c.save()
    buf.seek(0)
    return buf.getvalue()

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
    with c_t: st.subheader("💰 Scholarship Student Portal")
    
    sch_fee = float(master_db.get("scholarship_fee", 50.0))

    if not st.session_state.get('sch_logged_in', False):
        log_tab, reg_tab = st.tabs(["🔑 Student Login", "📝 New Registration"])
        with log_tab:
            stu_log_mode = st.radio("Choose Action", ["Login", "Forgot Password"], key="stu_log_mode")
            if stu_log_mode == "Login":
                check_brute_force()
                st.info("Enter your 12-digit User ID.")
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
                st.info("Recover your Student Account using User ID")
                f_uid = st.text_input("Enter your User ID", key="f_sch_uid")
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
                            send_real_sms(sanitize(r_mob), st.session_state['temp_sch_otp'], "Student")
                            st.session_state['sch_reg_step'] = 2
                            st.rerun()
                    else: st.error("Please enter valid Mobile/Email and 12-digit ID.")
            elif st.session_state['sch_reg_step'] == 2:
                in_otp = st.text_input("Enter OTP *")
                if 'temp_sch_otp' in st.session_state:
                    send_real_sms(st.session_state.get('temp_r_mob', ''), st.session_state['temp_sch_otp'], "Student")
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
                        st.success("Registration Successful! Please login.")
                        st.session_state['sch_reg_step'] = 1
                    else: st.error("Passwords do not match!")
    else:
        cur_uid = st.session_state['sch_current_user']
        user_profile = sch_users_db[cur_uid]
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
            st.error("⚠️ You have already submitted your application.")
            st.markdown(render_odisha_scholarship_html(existing_app_id, existing_app_data), unsafe_allow_html=True)
            pdf_path = f"Scholarship_Data/Student_Submissions/{existing_app_id}/Payment_Receipt_Application.pdf"
            if not os.path.exists(pdf_path):
                os.makedirs(f"Scholarship_Data/Student_Submissions/{existing_app_id}", exist_ok=True)
                create_odisha_scholarship_pdf(pdf_path, existing_app_id, existing_app_data)
            with open(pdf_path, "rb") as f:
                pdf_data_bytes = f.read()
            st.download_button("📥 Download PDF", data=pdf_data_bytes, file_name=f"Scholarship_{existing_app_id}.pdf", mime="application/pdf", key="stu_dash_dl")

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
        pdf_bytes = create_student_receipt_pdf(st.session_state['stu_reg_id'], st.session_state['stu_reg_data'])
        st.download_button("📥 Download PDF Receipt", data=pdf_bytes, file_name=f"Receipt_{st.session_state['stu_reg_id']}.pdf", mime="application/pdf", key="stu_dl_btn_unique")
        if st.button("⬅️ Done", key="stu_done_btn_unique"): st.session_state['stu_reg_success'] = False; st.rerun()
                
    elif not st.session_state['payment_step']:
        with st.form("student_reg_form"):
            c_sc1, c_sc2 = st.columns(2)
            active_schools = {k: v for k, v in schools_db.items() if v.get("status", "Active") == "Active"}
            school_options = [f"{k} - {v['name']}" for k, v in active_schools.items()] if active_schools else []
            school_sel_str = c_sc1.selectbox("Select School Code & Name *", ["--Select--"] + school_options) if school_options else "--Select--"
            school_sel = school_sel_str.split(" - ")[0] if school_sel_str != "--Select--" else None
            
            c_n1, c_n2 = st.columns(2)
            stu_name_en = c_n1.text_input("1. Student's Name (English) *")
            stu_phone = c_n2.text_input("8. Mobile No *", max_chars=10)
            
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
                            "name": sanitize(stu_name_en), "phone": sanitize(stu_phone),
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
        sch_pdf_bytes = create_school_receipt_pdf(st.session_state['sch_reg_id'], st.session_state['sch_reg_data'])
        st.download_button("📥 Download PDF Receipt", data=sch_pdf_bytes, file_name=f"School_Receipt_{st.session_state['sch_reg_id']}.pdf", mime="application/pdf", key="sch_dl_btn_unique")
        if st.button("⬅️ Done", key="sch_done_btn_unique"): st.session_state['sch_reg_success'] = False; st.rerun()

    elif not st.session_state['school_payment_step']:
        with st.form("school_reg_form"):
            r_id = st.text_input("School ID (Unique) *")
            c_n1, c_n2 = st.columns(2)
            r_name_en = c_n1.text_input("School Name (English) *")
            r_name_loc = c_n2.text_input("School Name (Local Language)")
            r_state = st.selectbox("State", list(STATE_LANG_MAP.keys()), index=18)
            r_pass = st.text_input("New Password *", type="password")
            if st.form_submit_button("Proceed to Payment & Submit"):
                s_id_clean = sanitize(r_id)
                if not s_id_clean or not sanitize(r_name_en) or not r_pass: st.error("Fill mandatory fields (*)")
                elif s_id_clean in schools_db: st.error("School ID already exists.")
                else:
                    st.session_state['temp_school_data'] = {
                        "school_id": s_id_clean,
                        "data": {
                            "name": sanitize(r_name_en), "name_local": sanitize(r_name_loc),
                            "pass": r_pass, "state": r_state, "lang": STATE_LANG_MAP[r_state],
                            "status": "Pending_Master_Approval", "payment_mode": "Pending"
                        }
                    }
                    st.session_state['school_payment_step'] = True; st.rerun()

    if st.session_state.get('school_payment_step', False):
        s_tmp = st.session_state.get('temp_school_data')
        st.info(f"Total Fee: **₹{s_total_fee:.2f}**")
        if st.button("Complete Payment & Submit", key="sch_pay_complete"):
            s_tmp['data']['payment_mode'] = f"Online (₹{s_total_fee:.2f})"
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
        st.info("Master Control Active.")

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

        t_list, t_add, t_rep = st.tabs(["📋 My Students", "➕ Add Student", "🖨️ Report Card"])
        cur_students = students_db.get(cur_school, {})
        
        with t_list:
            if cur_students:
                st.write(f"Total Students: **{len(cur_students)}**")
                for r_no, s_info in cur_students.items():
                    st.write(f"✅ **Roll:** {r_no} | **Name:** {s_info.get('name')} | **Class:** {s_info.get('class', 'N/A')}")
            else: st.warning("No students found.")
                
        with t_add:
            c_roll, c_gen = st.columns(2)
            add_roll = c_roll.text_input("Roll No *", key="s_add_roll_v2")
            add_name = c_gen.text_input("Student Name (English) *", key="s_add_name_v2")
            
            c_p1, c_p2 = st.columns(2)
            add_pen = c_p1.text_input("PEN NO", key="s_add_pen_v2")
            add_apaar = c_p2.text_input("APAAR NO", key="s_add_apaar_v2")
            
            c_d1, c_c1 = st.columns(2)
            add_dob = c_d1.date_input("DOB", min_value=datetime.date(2000, 1, 1), key="s_add_dob_v2")
            add_class = c_c1.selectbox("Class", classes_list, key="s_add_cls_v2")
            
            add_batch = st.selectbox("Batch", batches_list, index=5, key="s_add_bat_v2")
            
            st.markdown("#### 📚 Add Subjects & Marks")
            if 's_add_num_subs' not in st.session_state: st.session_state.s_add_num_subs = 5
            
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
                        "name": sanitize(add_name), "pen_no": sanitize(add_pen), "apaar_no": sanitize(add_apaar),
                        "dob": str(add_dob), "class": add_class, "batch": add_batch,
                        "subjects": subjects_data, "total_full": total_full, "total_obt": total_obt,
                        "percentage": round(per, 2), "result": res, "grade": grd, "status": "Approved"
                    }
                    if cur_school not in students_db: students_db[cur_school] = {}
                    students_db[cur_school][sanitize(add_roll)] = new_data
                    save_data(schools_db, students_db); st.success("Added!"); st.rerun()

        with t_rep:
            st.markdown("### 🖨️ Report Card")
            if cur_students:
                rep_roll = st.selectbox("Select Roll for Report", list(cur_students.keys()), key="s_rep_roll_v2")
                curr_st_obj = cur_students[rep_roll]
                
                # HTML Live Preview with Barcode and QR
                st.markdown(generate_result_card_html(sch_data['name'], sch_data.get('name_local', ''), curr_st_obj, rep_roll, s_lang), unsafe_allow_html=True)
                
                # Memory PDF generation (Zero blank page issue)
                pdf_data = create_pdf_bytes(sch_data['name'], curr_st_obj, rep_roll)
                
                st.markdown("<br>", unsafe_allow_html=True)
                c_d1, c_d2 = st.columns(2)
                with c_d1:
                    st.download_button("📥 Download PDF", data=pdf_data, file_name=f"Report_{rep_roll}.pdf", mime="application/pdf", key="s_dl_pdf_v2")
                with c_d2:
                    if st.button("🖨️ Print Result Card", key="s_print_v2"):
                        components.html("<script>window.parent.print();</script>", height=0)

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
            dob_mismatch = False
            
            for s_id, school_students in students_db.items():
                for r_no, s_info in school_students.items():
                    match_roll = (r_no.strip().lower() == sq_clean)
                    match_name = (s_info.get("name", "").strip().lower() == sq_clean)
                    
                    if match_roll or match_name:
                        st_dob_norm = normalize_dob(s_info.get("dob", ""))
                        if st_dob_norm == ndob:
                            found_student = s_info
                            found_roll = r_no
                            found_school_id = s_id
                            break
                        else: dob_mismatch = True
                if found_student: break
            
            if found_student:
                st.session_state['active_result'] = {
                    "student": found_student,
                    "roll": found_roll,
                    "school_id": found_school_id
                }
                st.rerun()
            elif dob_mismatch:
                st.warning("⚠️ Roll No/Name match zala pan Date of Birth (DOB) match hot nahiye.")
            else:
                st.error("❌ Konihi record sapadla nahi! Roll Number aani DOB check kara.")

    # Render Result if stored in session
    if 'active_result' in st.session_state:
        res_info = st.session_state['active_result']
        f_student = res_info['student']
        f_roll = res_info['roll']
        f_sch_id = res_info['school_id']
        
        sch = schools_db.get(f_sch_id, {})
        s_lang = sch.get("lang", "English")
        st.success(f"🎉 **Welcome {f_student.get('name', '').upper()}!**")
        
        # Display Card on screen
        st.markdown(generate_result_card_html(sch.get('name', 'Unknown School'), sch.get('name_local', ''), f_student, f_roll, s_lang), unsafe_allow_html=True)
        
        # Download PDF bytes directly from memory
        pdf_bytes = create_pdf_bytes(sch.get('name', 'Unknown School'), f_student, f_roll)
        
        st.markdown("<br>", unsafe_allow_html=True)
        c_res1, c_res2 = st.columns(2)
        with c_res1:
            st.download_button("📥 Download PDF", data=pdf_bytes, file_name=f"Result_{f_roll}.pdf", mime="application/pdf", key="res_dl_v2")
        with c_res2:
            if st.button("🖨️ Print Result Card", key="res_print_v2"):
                components.html("<script>window.parent.print();</script>", height=0)

st.markdown("---")
st.markdown("<div style='text-align: center; padding: 15px; background: linear-gradient(90deg, #1e3a8a, #9333ea); color: white; border-radius: 8px; font-weight: bold;'>👨‍💻 Software Developed by: KULU SUTAR | 📞 Mob: 8910223342 | ✉️ kulusutar123@gmail.com</div>", unsafe_allow_html=True)
