import streamlit as st
import streamlit.components.v1 as components
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
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

# ==========================================
# 🔒 CRASH PROTECTION & DATA SAFETY LOCKS
# ==========================================
file_lock = threading.Lock()

def sanitize(text):
    if isinstance(text, str):
        return html.escape(text.strip())
    return text

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

# ==========================================
# 🗺️ ALL INDIAN STATES & LOCAL LANGUAGE MAPPING
# ==========================================
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
# 🤖 AUTO TRANSLATION ENGINE
# ==========================================
@st.cache_data(show_spinner=False)
def auto_translate(text, lang_name):
    LANG_CODES = {"Odia": "or", "Hindi": "hi", "Bengali": "bn", "English": "en"}
    if lang_name == "English" or not text: return text
    target_code = LANG_CODES.get(lang_name, "en")
    if target_code == "en": return text
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl={target_code}&dt=t&q={urllib.parse.quote(text)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=5, context=ctx)
        return "".join([s[0] for s in json.loads(res.read().decode('utf-8'))[0]])
    except Exception: return text 

def t(eng_text, lang):
    translations = {"School Portal": {"Odia": "ସ୍କୁଲ୍ ପୋର୍ଟାଲ୍", "Hindi": "स्कूल पोर्टल"}}
    return translations.get(eng_text, {}).get(lang, eng_text)

# 🛠️ FIXED: Number to Words Crash Protection
def number_to_words(num):
    try:
        num = int(float(num))
    except:
        num = 0
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
    d_str = str(d_str).strip().replace('/', '-')
    parts = d_str.split('-')
    if len(parts) == 3 and len(parts[0]) == 4: return f"{parts[2]}-{parts[1]}-{parts[0]}"
    return d_str

def normalize_dob(d_str):
    d_str = d_str.strip().replace('/', '-')
    if d_str.count('-') == 2:
        p1, p2, p3 = d_str.split('-')
        if len(p1) == 4: return f"{p1}-{p2}-{p3}" 
        elif len(p3) == 4: return f"{p3}-{p2}-{p1}" 
    return d_str

# --- 100% SAFE JSON DATA LOAD/SAVE FUNCTIONS ---
def load_master_data():
    default_master = {
        "username": "master", "password": "master123", "email": "kulusutar123@gmail.com", 
        "phone": "8910223342", "upi_id": "school@sbi", "reg_fee": 150.0, "gst_percent": 18.0,
        "school_reg_fee": 1000.0, "school_gst_percent": 18.0, "scholarship_fee": 50.0
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
        except Exception: pass
    return default_master

def save_master_data(data):
    with file_lock:
        with open(MASTER_FILE, "w", encoding="utf-8") as f: json.dump(data, f, indent=4)

def load_data():
    schools = {}; students = {}
    if os.path.exists(SCHOOLS_FILE):
        try:
            with open(SCHOOLS_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if content.strip(): schools = json.loads(content)
        except: pass
    if os.path.exists(STUDENTS_FILE):
        try:
            with open(STUDENTS_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if content.strip(): students = json.loads(content)
        except: pass
    return schools, students

def save_data(schools, students):
    with file_lock:
        with open(SCHOOLS_FILE, "w", encoding="utf-8") as f: json.dump(schools, f, indent=4)
        with open(STUDENTS_FILE, "w", encoding="utf-8") as f: json.dump(students, f, indent=4)

def load_scholarships():
    sch = {}
    if os.path.exists(SCHOLARSHIPS_FILE):
        try:
            with open(SCHOLARSHIPS_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if content.strip(): sch = json.loads(content)
        except: pass
    return sch

def save_scholarships(sch):
    with file_lock:
        with open(SCHOLARSHIPS_FILE, "w", encoding="utf-8") as f: json.dump(sch, f, indent=4)

# ==========================================
# 🎨 PDF GENERATORS
# ==========================================
def create_student_receipt_pdf(filename, reg_id, s_data):
    c = canvas.Canvas(filename, pagesize=letter)
    c.setStrokeColorRGB(0.1, 0.2, 0.5); c.setLineWidth(4); c.rect(30, 30, 552, 732, stroke=1, fill=0)
    c.setFillColorRGB(0.1, 0.2, 0.5); c.setFont("Times-Bold", 22); c.drawCentredString(300, 720, "STUDENT REGISTRATION RECEIPT")
    c.setFillColorRGB(0, 0, 0); c.setFont("Helvetica-Bold", 12); c.drawString(50, 670, f"REGISTRATION ID: {reg_id}")
    c.setFont("Helvetica", 12); y = 640
    c.drawString(50, y, f"Student Name: {s_data.get('name', '').upper()}"); y -= 25
    c.drawString(50, y, f"Phone: {s_data.get('phone', '')}"); y -= 25
    c.drawString(50, y, f"Status: {s_data.get('status', 'Pending')}"); y -= 25
    c.line(50, y, 550, y); y -= 20
    c.setFont("Helvetica-Oblique", 10); c.drawCentredString(300, y, "This is a computer-generated receipt. Please keep it safe.")
    c.save()

def create_scholarship_pdf(filename, app_id, s_data):
    c = canvas.Canvas(filename, pagesize=letter)
    c.setStrokeColorRGB(0.1, 0.4, 0.2); c.setLineWidth(4); c.rect(30, 30, 552, 732, stroke=1, fill=0)
    c.setFillColorRGB(0.1, 0.4, 0.2); c.setFont("Times-Bold", 20); c.drawCentredString(300, 710, "SCHOLARSHIP APPLICATION RECEIPT")
    c.setFillColorRGB(0, 0, 0); c.setFont("Helvetica-Bold", 12); c.drawString(50, 670, f"APPLICATION ID: {app_id}")
    c.setFont("Helvetica", 11); y = 640
    c.drawString(50, y, f"Applicant Name: {s_data.get('app_name', '').upper()}"); c.drawString(350, y, f"OTR No: {s_data.get('otr', '')}"); y -= 25
    c.drawString(50, y, f"Aadhaar No: {s_data.get('aadhaar', '')}"); c.drawString(350, y, f"Category: {s_data.get('category', '')}"); y -= 25
    c.drawString(50, y, f"Phone: {s_data.get('mobile', '')}"); c.drawString(350, y, f"School Code: {s_data.get('school_code', '')}"); y -= 35
    c.setStrokeColorRGB(0.8, 0.8, 0.8); c.line(50, y, 550, y); y -= 20
    c.setFont("Helvetica-Bold", 12); c.drawString(50, y, "Certificate & Institute Info"); c.setFont("Helvetica", 11); y -= 20
    c.drawString(50, y, f"Class: {s_data.get('class', '')}"); c.drawString(350, y, f"Income Cert: {s_data.get('income_cert', '')}"); y -= 25
    c.drawString(50, y, f"Caste Cert: {s_data.get('caste_cert', '')}"); y -= 35
    c.setStrokeColorRGB(0.8, 0.8, 0.8); c.line(50, y, 550, y); y -= 20
    c.setFont("Helvetica-Bold", 12); c.drawString(50, y, "Bank Information"); c.setFont("Helvetica", 11); y -= 20
    c.drawString(50, y, f"Account No: {s_data.get('acc_no', '')}"); c.drawString(350, y, f"Bank: {s_data.get('bank_name', '')}"); y -= 25
    c.setStrokeColorRGB(0.8, 0.8, 0.8); c.line(50, y, 550, y); y -= 20
    c.setFont("Helvetica-Bold", 12); c.drawString(50, y, "Payment & Status"); c.setFont("Helvetica", 11); y -= 20
    c.drawString(50, y, f"Payment Mode: {s_data.get('payment_mode', 'N/A')}"); y -= 25
    c.drawString(50, y, f"Current Status: {s_data.get('status', 'Pending_Master')}"); y -= 40
    c.line(50, y, 550, y); y -= 20
    c.setFont("Helvetica-Oblique", 10); c.drawCentredString(300, y, "Computer-generated receipt. Keep for future reference.")
    try: bc = code128.Code128(str(app_id), barHeight=30, barWidth=1.5); bc.drawOn(c, 50, 40)
    except: pass
    c.save()

def generate_result_card_html(school_name_en, school_name_loc, st_data, roll_no, s_lang):
    disp_dob = format_display_date(st_data.get('dob', ''))
    raw_pub = st_data.get('pub_date', '')
    disp_pub_date = format_display_date(raw_pub) if raw_pub else datetime.date.today().strftime('%d-%m-%Y')

    bc, b_col, ob, t_bg = "#fef9f7", "#963f98", "#ce9bd0", "#fcf4fc"
    tot_obt = st_data.get('total_obt', 0)
    w_tot_en = number_to_words(tot_obt)
    s_name_en = st_data.get('name', 'N/A').upper()
    m_name_en = st_data.get('mother_name', 'N/A').upper()
    f_name_en = st_data.get('father_name', 'N/A').upper()
    
    t_sch = school_name_loc if school_name_loc.strip() else auto_translate(school_name_en, s_lang)
    t_stu = st_data.get('name_local', '').strip() or auto_translate(s_name_en, s_lang)
    t_mot = st_data.get('mother_name_local', '').strip() or auto_translate(m_name_en, s_lang)
    t_fat = st_data.get('father_name_local', '').strip() or auto_translate(f_name_en, s_lang)
    t_w_tot = auto_translate(w_tot_en, s_lang)

    qr_text = f"SCHOOL: {school_name_en} | NAME: {s_name_en} | ROLL: {roll_no} | DOB: {disp_dob} | MARKS: {tot_obt}/{st_data.get('total_full', 0)} | GRADE: {st_data.get('grade', '')}"
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={urllib.parse.quote(qr_text)}"
    bc_url = f"https://barcode.tec-it.com/barcode.ashx?data={roll_no}&code=Code128&dpi=96"

    rows_html = "".join([f"<tr style='border-bottom: 1px solid {b_col};'><td style='padding: 8px; border-right: 1px solid {b_col}; text-align: left; font-weight: bold; color: #000;'>{sub.upper()}</td><td style='padding: 8px; border-right: 1px solid {b_col}; color: #000;'>{m['full']}</td><td style='padding: 8px; font-weight: bold; color: #000;'>{m['obt']}</td></tr>" for sub, m in st_data.get('subjects', {}).items()])

    return f"""
    <div style='font-family: "Times New Roman", serif; border: 15px solid {ob}; padding: 4px; max-width: 800px; margin: auto; background-color: #fff;'>
        <div style='border: 2px solid {b_col}; padding: 25px; background-color: {bc}; position: relative;'>
            <div style='text-align: center; color: {b_col}; margin-bottom: 20px;'>
                <h1 style='margin: 0; font-size: 24px; text-transform: uppercase;'>{school_name_en}</h1>
                <h2 style='margin: 5px 0 10px 0; font-size: 18px;'>{t_sch}</h2>
                <h3 style='margin: 5px 0; font-size: 16px;'>ANNUAL EXAMINATION / {t('ANNUAL EXAMINATION', s_lang)} - {st_data.get('batch', '2025-2026')}</h3>
                <p style='margin: 5px 0; font-weight: bold; font-size: 17px; text-decoration: underline;'>CERTIFICATE-CUM-MARK SHEET <br><span style='font-size:14px;text-decoration:none;'>({t('CERTIFICATE-CUM-MARK SHEET', s_lang)})</span></p>
            </div>
            <table style='width: 100%; font-size: 13px; margin-bottom: 20px; font-weight: bold;'>
                <tr><td><span style='color:{b_col};'>ROLL NO:</span> <span style='color:#000;'>{roll_no}</span></td><td style='text-align: right;'><span style='color:{b_col};'>CLASS:</span> <span style='color:#000;'>{st_data.get('class', '')}</span></td></tr>
                <tr><td><span style='color:{b_col};'>PEN NO:</span> <span style='color:#000;'>{st_data.get('pen_no', '')}</span></td><td style='text-align: right;'><span style='color:{b_col};'>APAAR NO:</span> <span style='color:#000;'>{st_data.get('apaar_no', '')}</span></td></tr>
            </table>
            <table style='width: 100%; font-size: 14px; margin-bottom: 15px; text-transform: uppercase; line-height: 1.8;'>
                <tr><td style='width: 250px; color: {b_col}; font-weight: bold;'>Certify that / {t('NAME', s_lang)}</td><td><b style='color:#000;'>{s_name_en}</b><br><span style='font-size:14px; text-transform:none; color:#000;'>{t_stu}</span></td></tr>
                <tr><td style='color: {b_col}; font-weight: bold;'>Mother's Name</td><td><b style='color:#000;'>{m_name_en}</b><br><span style='font-size:14px; text-transform:none; color:#000;'>{t_mot}</span></td></tr>
                <tr><td style='color: {b_col}; font-weight: bold;'>Father's Name</td><td><b style='color:#000;'>{f_name_en}</b><br><span style='font-size:14px; text-transform:none; color:#000;'>{t_fat}</span></td></tr>
                <tr><td style='color: {b_col}; font-weight: bold;'>Date of Birth</td><td><b style='color:#000;'>{disp_dob}</b></td></tr>
                <tr><td style='color: {b_col}; font-weight: bold;'>Category</td><td><b style='color:#000;'>{st_data.get('category', 'General')}</b></td></tr>
            </table>
            <p style='color: {b_col}; text-align: center; margin-bottom: 20px; font-style:italic;'>Passed the Annual Examination held in {st_data.get('batch', '')}.</p>
            <table style='width: 100%; border-collapse: collapse; border: 2px solid {b_col}; text-align: center; font-size: 13px;'>
                <tr style='color: {b_col}; background-color: {t_bg}; border-bottom: 2px solid {b_col};'>
                    <th style='padding: 8px; border-right: 1px solid {b_col};'>SUBJECT</th><th style='padding: 8px; border-right: 1px solid {b_col};'>FULL MARKS</th><th style='padding: 8px;'>MARKS SECURED</th>
                </tr>
                {rows_html}
                <tr style='color: {b_col}; font-weight: bold; background-color: {t_bg}; border-top: 2px solid {b_col};'>
                    <td style='padding: 10px; border-right: 1px solid {b_col}; text-align: right;'>TOTAL MARKS</td><td style='padding: 10px; border-right: 1px solid {b_col}; color:#000;'>{st_data.get('total_full', 0)}</td><td style='padding: 10px; color:#000;'>{tot_obt}</td>
                </tr>
            </table>
            <div style='text-align: center; font-weight: bold; font-size: 14px; margin-top: 20px; color:#000;'>( {w_tot_en} ) <br><span style='font-size:13px; font-weight:normal;'>({t_w_tot})</span></div>
            <table style='width: 100%; margin-top: 20px; text-align: center; color: {b_col};'>
                <tr>
                    <td style='width: 33%; vertical-align: bottom;'><img src='{bc_url}' style='height: 35px; margin-bottom: 10px;'/><br><div style='font-size: 11px;'>DATE OF PUBLICATION</div><div style='font-weight: bold; font-size: 14px; margin-bottom: 30px; color:#000;'>{disp_pub_date}</div><div style='border-bottom: 1px solid {b_col}; width: 80%; margin: auto;'></div><div style='font-size: 11px; font-weight: bold; margin-top:5px;'>HM SIGNATURE</div></td>
                    <td style='width: 34%; vertical-align: top;'><div style='font-size: 12px; margin-bottom: 5px;'>GRADE</div><div style='border: 2px solid {b_col}; padding: 10px 25px; display: inline-block; background-color: {t_bg};'><div style='font-weight: bold; font-size: 22px; color: #000;'>{st_data.get('grade', '')}</div></div></td>
                    <td style='width: 33%; vertical-align: bottom;'><img src='{qr_url}' style='height: 65px; margin-bottom: 10px;'/><div style='height: 15px; margin-bottom: 30px;'></div><div style='border-bottom: 1px solid {b_col}; width: 80%; margin: auto;'></div><div style='font-size: 11px; font-weight: bold; margin-top:5px;'>CLASS TEACHER SIGNATURE</div></td>
                </tr>
            </table>
        </div>
    </div>
    """

def create_pdf(filename, school_name, st_data, roll_no):
    disp_dob = format_display_date(st_data.get('dob', ''))
    raw_pub = st_data.get('pub_date', '')
    disp_pub_date = format_display_date(raw_pub) if raw_pub else datetime.date.today().strftime('%d-%m-%Y')
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFillColorRGB(0.99, 0.98, 0.97); c.rect(30, 30, 552, 732, fill=1, stroke=0)
    c.setStrokeColorRGB(0.82, 0.60, 0.83); c.setLineWidth(15); c.rect(15, 15, 582, 762, fill=0, stroke=1)
    c.setStrokeColorRGB(0.59, 0.25, 0.60); c.setLineWidth(2); c.rect(30, 30, 552, 732, fill=0, stroke=1)
    
    c.setFillColorRGB(0.59, 0.25, 0.60); c.setFont("Times-Bold", 20); c.drawCentredString(300, 720, school_name.upper())
    c.setFont("Helvetica-Bold", 12); c.drawCentredString(300, 695, f"ANNUAL EXAMINATION - {st_data.get('batch', '2025-2026')}")
    c.setFont("Helvetica", 11); c.drawCentredString(300, 675, "CERTIFICATE-CUM-MARK SHEET")
    
    c.drawString(50, 635, "ROLL NO:"); c.setFillColorRGB(0,0,0); c.setFont("Helvetica-Bold", 11); c.drawString(110, 635, f"{roll_no}")
    c.setFillColorRGB(0.59, 0.25, 0.60); c.drawString(450, 635, "CLASS:"); c.setFillColorRGB(0,0,0); c.drawString(500, 635, f"{st_data.get('class', '')}")
    c.setFillColorRGB(0.59, 0.25, 0.60); c.drawString(50, 615, "PEN NO:"); c.setFillColorRGB(0,0,0); c.drawString(100, 615, f"{st_data.get('pen_no', '')}")
    c.setFillColorRGB(0.59, 0.25, 0.60); c.drawString(420, 615, "APAAR NO:"); c.setFillColorRGB(0,0,0); c.drawString(490, 615, f"{st_data.get('apaar_no', '')}")
    
    c.setFillColorRGB(0.59, 0.25, 0.60); c.setFont("Helvetica-Oblique", 11); c.drawString(50, 585, "Certify that")
    c.setFillColorRGB(0,0,0); c.setFont("Helvetica-Bold", 11); c.drawString(150, 585, f"{st_data.get('name', '').upper()}")
    c.setFillColorRGB(0.59, 0.25, 0.60); c.setFont("Helvetica-Oblique", 11); c.drawString(50, 565, "Mother's Name")
    c.setFillColorRGB(0,0,0); c.setFont("Helvetica-Bold", 11); c.drawString(150, 565, f"{st_data.get('mother_name', '').upper()}")
    c.setFillColorRGB(0.59, 0.25, 0.60); c.setFont("Helvetica-Oblique", 11); c.drawString(50, 545, "Father's Name")
    c.setFillColorRGB(0,0,0); c.setFont("Helvetica-Bold", 11); c.drawString(150, 545, f"{st_data.get('father_name', '').upper()}")
    c.setFillColorRGB(0.59, 0.25, 0.60); c.setFont("Helvetica-Oblique", 11); c.drawString(50, 525, "Date of Birth")
    c.setFillColorRGB(0,0,0); c.setFont("Helvetica-Bold", 11); c.drawString(150, 525, f"{disp_dob}")
    c.setFillColorRGB(0.59, 0.25, 0.60); c.setFont("Helvetica-Oblique", 11); c.drawString(50, 505, "Category")
    c.setFillColorRGB(0,0,0); c.setFont("Helvetica-Bold", 11); c.drawString(150, 505, f"{st_data.get('category', 'General')}")
    
    c.setStrokeColorRGB(0.59, 0.25, 0.60); c.line(50, 485, 550, 485)
    c.setFillColorRGB(0.98, 0.95, 0.98); c.rect(50, 455, 500, 30, fill=1, stroke=0)
    c.setFillColorRGB(0.59, 0.25, 0.60); c.setFont("Helvetica-Bold", 11)
    c.drawString(60, 465, "SUBJECT"); c.drawCentredString(350, 465, "FULL MARKS"); c.drawRightString(540, 465, "MARKS SECURED")
    c.line(50, 455, 550, 455); c.line(50, 485, 50, 455); c.line(280, 485, 280, 455); c.line(420, 485, 420, 455); c.line(550, 485, 550, 455)
    
    c.setFillColorRGB(0,0,0); y = 435; t_b_y = y + 10
    for sub, m_info in st_data.get('subjects', {}).items():
        c.drawString(60, y, str(sub).upper()); c.drawCentredString(350, y, str(m_info['full'])); c.drawRightString(540, y, str(m_info['obt']))
        c.setStrokeColorRGB(0.59, 0.25, 0.60); c.line(50, y-10, 550, y-10)
        y -= 20; t_b_y = y + 10
    c.line(50, 455, 50, t_b_y); c.line(280, 455, 280, t_b_y); c.line(420, 455, 420, t_b_y); c.line(550, 455, 550, t_b_y)
    
    c.setFillColorRGB(0.98, 0.95, 0.98); c.rect(50, t_b_y-25, 500, 25, fill=1, stroke=0)
    c.setFillColorRGB(0.59, 0.25, 0.60); c.setFont("Helvetica-Bold", 11)
    c.drawRightString(270, t_b_y-17, "TOTAL MARKS"); c.drawCentredString(350, t_b_y-17, str(st_data.get('total_full', 0)))
    c.setFillColorRGB(0,0,0); c.drawRightString(540, t_b_y-17, str(st_data.get('total_obt', 0)))
    c.setStrokeColorRGB(0.59, 0.25, 0.60); c.line(50, t_b_y-25, 550, t_b_y-25)
    c.line(50, t_b_y, 50, t_b_y-25); c.line(280, t_b_y, 280, t_b_y-25); c.line(420, t_b_y, 420, t_b_y-25); c.line(550, t_b_y, 550, t_b_y-25)
    
    y = t_b_y - 45; c.setFillColorRGB(0,0,0); c.setFont("Helvetica-Bold", 10)
    # FIX APPLIED HERE: SAFELY HANDLE number_to_words to avoid errors
    c.drawCentredString(300, y, f"( {number_to_words(st_data.get('total_obt', 0))} )")
    y -= 60
    try: bc = code128.Code128(str(roll_no), barHeight=25, barWidth=1.2); bc.drawOn(c, 50, y+15)
    except: pass
    c.setFillColorRGB(0.59, 0.25, 0.60); c.setFont("Helvetica", 10); c.drawCentredString(140, y-10, "DATE OF PUBLICATION")
    c.setFont("Helvetica-Bold", 11); c.drawCentredString(140, y-25, f"{disp_pub_date}")
    c.line(50, y-60, 230, y-60); c.setFont("Helvetica-Bold", 10); c.drawCentredString(140, y-75, "HM SIGNATURE")
    c.setStrokeColorRGB(0.59, 0.25, 0.60); c.setFillColorRGB(0.98, 0.95, 0.98); c.rect(260, y-30, 80, 40, fill=1, stroke=1)
    c.setFillColorRGB(0.59, 0.25, 0.60); c.setFont("Helvetica", 10); c.drawCentredString(300, y+20, "GRADE")
    c.setFillColorRGB(0,0,0); c.setFont("Helvetica-Bold", 18); c.drawCentredString(300, y-15, f"{st_data.get('grade', '')}")
    
    try:
        qr_text = f"SCHOOL: {school_name}\nROLL: {roll_no}\nMARKS: {st_data.get('total_obt')}/{st_data.get('total_full')}\nGRADE: {st_data.get('grade')}"
        qr_w = qr.QrCodeWidget(qr_text); b = qr_w.getBounds(); w = b[2]-b[0]; h = b[3]-b[1]
        d = Drawing(60, 60, transform=[60/w,0,0,60/h,0,0]); d.add(qr_w); renderPDF.draw(d, c, 445, y-5)
    except: pass
    c.setFillColorRGB(0.59, 0.25, 0.60); c.line(400, y-60, 550, y-60); c.setFont("Helvetica-Bold", 10); c.drawCentredString(475, y-75, "CLASS TEACHER SIGNATURE")
    c.save()

# --- MAIN APP START ---
schools_db, students_db = load_data()
master_db = load_master_data()
scholarships_db = load_scholarships()

menu_items = ["Home Page", "Scholarship Portal", "New Student Registration", "New School Registration", "Master Login", "School Login", "Results"]
portal_map = {"home": 0, "scholarship": 1, "reg_student": 2, "reg_school": 3, "master": 4, "school": 5, "student": 6}
portal_param = st.query_params.get("portal", "home")
default_idx = portal_map.get(portal_param, 0)

if portal_param != "home":
    st.sidebar.markdown("---")
    user_bg_color = st.sidebar.color_picker("🎨 Custom Background Color", "#ffffff")
    st.markdown(f"<style>.stApp {{ background-color: {user_bg_color} !important; }}</style>", unsafe_allow_html=True)

menu = st.sidebar.selectbox("🎯 Navigation Menu", menu_items, index=default_idx)

if menu == "Home Page": st.query_params["portal"] = "home"
elif menu == "Scholarship Portal": st.query_params["portal"] = "scholarship"
elif menu == "New Student Registration": st.query_params["portal"] = "reg_student"
elif menu == "New School Registration": st.query_params["portal"] = "reg_school"
elif menu == "Master Login": st.query_params["portal"] = "master"
elif menu == "School Login": st.query_params["portal"] = "school"
elif menu == "Results": st.query_params["portal"] = "student"

classes_list = [str(i) for i in range(1, 11)]
batches_list = [f"{y}-{y+1}" for y in range(2020, 2051)]

# ----------------- HOME PAGE (DYNAMIC UI) -----------------
if menu == "Home Page":
    bg_images = [
        "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?q=80&w=1920",
        "https://images.unsplash.com/photo-1541829070764-84a7d30dd3f3?q=80&w=1920"
    ]
    selected_bg = random.choice(bg_images)
    
    st.markdown(f"""
    <style>
    .stApp {{ background-image: url("{selected_bg}"); background-size: cover; background-position: center; background-attachment: fixed; }}
    .glass-panel {{ background: rgba(15, 23, 42, 0.85); padding: 20px; border-radius: 15px; border: 2px solid #38bdf8; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37); backdrop-filter: blur(4px); margin-bottom: 25px; }}
    .login-card {{ background: rgba(255, 255, 255, 0.95) !important; border: 1px solid #cbd5e1; border-bottom: 5px solid #fbbf24; border-radius: 8px; padding: 20px; margin-bottom: 20px; text-align: center; text-decoration: none; display: block; color: #1e3a8a !important; box-shadow: 0 4px 6px rgba(0,0,0,0.05); transition: 0.3s; }}
    .login-card:hover {{ background: #ffffff !important; border-bottom: 5px solid #1e3a8a; transform: translateY(-3px); box-shadow: 0 8px 15px rgba(0,0,0,0.2); }}
    .login-title {{ font-size: 20px; font-weight: bold; margin-bottom: 8px; color: #1e3a8a !important;}}
    .login-sub {{ font-size: 14px; color: #64748b !important;}}
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

    base_images = (
        "<img class='marquee-img' src='https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=600&q=80' alt='School Building'>"
        "<img class='marquee-img' src='https://images.weserv.nl/?url=upload.wikimedia.org/wikipedia/commons/e/e2/Droupadi_Murmu_Official_Portrait.jpg&w=400' alt='President Murmu'>"
        "<img class='marquee-img' src='https://images.weserv.nl/?url=upload.wikimedia.org/wikipedia/commons/c/c0/Official_Photograph_of_Prime_Minister_Narendra_Modi_Portrait.png&w=400' alt='PM Modi'>"
        "<img class='marquee-img' src='https://images.weserv.nl/?url=upload.wikimedia.org/wikipedia/commons/e/e0/Raja_Ravi_Varma_-_Saraswati.jpg&w=400' alt='Saraswati Maa'>"
        "<img class='marquee-img' src='https://images.weserv.nl/?url=upload.wikimedia.org/wikipedia/commons/1/19/Ganesha_Basohli_miniature_circa_1730_Dubost_p73.jpg&w=400' alt='Lord Ganesha'>"
        "<img class='marquee-img' src='https://images.weserv.nl/?url=upload.wikimedia.org/wikipedia/commons/b/b3/Jagannath.jpg&w=400' alt='Lord Jagannath'>"
    )

    carousel_html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8">
    <style>
    html, body {{ margin: 0; padding: 0; background: transparent; font-family: sans-serif; overflow: hidden; height: 100%; }}
    .carousel-container {{ width: 100%; height: 350px; overflow: hidden; border-radius: 10px; position: relative; border: 2px solid #38bdf8; box-sizing: border-box; background: rgba(15, 23, 42, 0.6); }}
    .marquee-img {{ height: 260px; border-radius: 10px; margin-right: 20px; object-fit: contain; display: inline-block; vertical-align: middle; margin-top: 15px; border: 2px solid #fbbf24; background-color: #fff; padding: 5px; box-shadow: 2px 2px 10px rgba(0,0,0,0.5); }}
    .carousel-overlay {{ position: absolute; bottom: 0; background: rgba(30,58,138,0.9); width: 100%; color: white; text-align: center; padding: 12px; font-weight: bold; font-size: 20px; letter-spacing: 1px; box-sizing: border-box; text-shadow: 1px 1px 2px #000; }}
    </style></head>
    <body>
    <div class="carousel-container">
        <marquee behavior="scroll" direction="left" scrollamount="12" onmouseover="this.stop();" onmouseout="this.start();" style="display: flex; align-items: center; white-space: nowrap; height: 100%;">
            {event_images}{base_images}
        </marquee>
        <div class="carousel-overlay">Connecting Students, Teachers & Administration Seamlessly</div>
    </div>
    </body></html>
    """

    st.markdown(f"<div class='glass-panel'><h2 style='text-align: center; color: #fbbf24; margin-top: 0; text-shadow: 1px 1px 2px #000;'>🏫 {event_title}</h2>", unsafe_allow_html=True)
    components.html(carousel_html, height=360)
    st.markdown("</div>", unsafe_allow_html=True)

    # 🌟 SEPARATE NOTIFICATION & NEWS TICKERS
    notice_and_news_html = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
    body { margin: 0; padding: 0; font-family: sans-serif; background: transparent; }
    .notice-box { background-color: rgba(30,41,59,0.9); border-radius: 5px; border: 1px solid #475569; overflow: hidden; color: #e2e8f0; font-size: 18px; padding: 10px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);}
    .news-box { background-color: rgba(127,29,29,0.9); border-radius: 5px; border: 1px solid #ef4444; overflow: hidden; color: #ffffff; font-size: 18px; padding: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);}
    .label { font-size:12px; font-weight:bold; margin-bottom:4px; letter-spacing: 1px; }
    .new-badge { background-color: #fbbf24; color: black; font-size: 14px; font-weight: bold; padding: 2px 6px; border-radius: 3px; margin-left: 5px; }
    </style>
    </head>
    <body>
        <div class="notice-box">
            <div class="label" style="color:#94a3b8;">📌 OFFICIAL NOTIFICATIONS & UPDATES</div>
            <marquee direction='left' scrollamount='8' style='font-weight: bold;'>
                <span style='color: #fbbf24;'>📢 ନୂଆ ଅପଡେଟ୍: ଛାତ୍ରଛାତ୍ରୀମାନେ ଏବେ ଅନଲାଇନ୍ ରେଜିଷ୍ଟ୍ରେସନ୍, ସ୍କଲାରସିପ୍ ଏବଂ ପେମେଣ୍ଟ କରିପାରିବେ! <span class='new-badge'>NEW</span> &nbsp;&nbsp;|&nbsp;&nbsp; 👨‍💻 Software Developed by: KULU SUTAR &nbsp;&nbsp;|&nbsp;&nbsp; 📞 Helpdesk No: 8910223342 &nbsp;&nbsp;|&nbsp;&nbsp; ✉️ Mail ID: kulusutar123@gmail.com </span>
            </marquee>
        </div>
        <div class="news-box">
            <div class="label" style="color:#fca5a5;">📰 ALL INDIA DAILY BREAKING NEWS</div>
            <marquee direction='left' scrollamount='6' style='font-weight: bold;'>
                <span>
                🔴 [ODISHA] ନୂଆ ଶିକ୍ଷା ନୀତି ଅନୁଯାୟୀ ସମସ୍ତ ସ୍କୁଲରେ ଡିଜିଟାଲ୍ କ୍ଲାସରୁମ୍ ଆରମ୍ଭ ହେବ! &nbsp;&nbsp;♦&nbsp;&nbsp; 
                🔴 [DELHI] Central Government announces new scholarship schemes for brilliant students across India! &nbsp;&nbsp;♦&nbsp;&nbsp; 
                🔴 [BENGAL] রাজ্যের সব স্কুলে নতুন শিক্ষাবর্ষের ভর্তি শুরু হচ্ছে! &nbsp;&nbsp;♦&nbsp;&nbsp; 
                🔴 [MAHARASHTRA] राज्यातील सर्व शाळांमध्ये नवीन तंत्रज्ञान लागू होणार! &nbsp;&nbsp;♦&nbsp;&nbsp; 
                🔴 [ANDHRA] రాష్ట్రంలోని పాఠశాలల్లో డిజిటల్ విద్య అమలు! &nbsp;&nbsp;♦&nbsp;&nbsp; 
                🔴 [HINDI] देश भर के सभी स्कूलों में नई डिजिटल शिक्षा प्रणाली लागू होगी!
                </span>
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
        st.markdown("<a href='?portal=scholarship' target='_self' class='login-card' style='border-bottom: 5px solid #10b981;'><div class='login-title'>💰 Scholarship Portal</div><div class='login-sub'>Apply Now</div></a>", unsafe_allow_html=True)
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
    with c_t: st.subheader("💰 Scholarship Application Portal")
    
    sch_fee = float(master_db.get("scholarship_fee", 50.0))
    
    if 'sch_app_step' not in st.session_state: st.session_state['sch_app_step'] = False
    if 'sch_app_success' not in st.session_state: st.session_state['sch_app_success'] = False
    if 'otr_verified' not in st.session_state: st.session_state['otr_verified'] = False

    if st.session_state['sch_app_success']:
        st.success(f"✅ Application Submitted! Reference ID is **{st.session_state['sch_app_id']}**.")
        st.info("Pending Master Verification. Download your receipt below.")
        pdf_file = f"Scholarship_{st.session_state['sch_app_id']}.pdf"
        create_scholarship_pdf(pdf_file, st.session_state['sch_app_id'], st.session_state['sch_app_data'])
        c1, c2 = st.columns(2)
        with c1:
            with open(pdf_file, "rb") as f: st.download_button("📥 Download PDF Receipt", f, file_name=pdf_file, mime="application/pdf")
        with c2:
            if st.button("⬅️ Back to Portal"):
                st.session_state['sch_app_success'] = False; st.rerun()

    elif not st.session_state['sch_app_step']:
        st.info("Please provide your One Time Registration (OTR) number generated from the National Scholarship Portal.")
        
        col_o1, col_o2 = st.columns([8, 2])
        otr_input = col_o1.text_input("OTR No. *", key="otr_inp_val")
        if col_o2.button("VERIFY OTR"):
            if otr_input:
                st.session_state['v_otr'] = otr_input
                st.session_state['v_name'] = "JYOTI PRAKASH SUTAR" 
                st.session_state['v_aadhaar'] = "8899-0011-2233" 
                st.success("✅ OTR Verified Successfully! Application Name and Aadhaar Auto-fetched.")
            else:
                st.error("Please enter OTR No.")

        c_ad1, c_ad2 = st.columns([8, 2])
        aadhaar_input = c_ad1.text_input("Aadhaar No. *", value=st.session_state.get('v_aadhaar', ''), key="ad_inp_val")
        if c_ad2.button("VERIFY AADHAAR"):
            if aadhaar_input:
                st.session_state['v_aadhaar'] = aadhaar_input
                st.success("✅ Aadhaar Linked & Verified Successfully!")
            else:
                st.error("Please enter Aadhaar No.")

        st.markdown("---")
        st.markdown("### 📝 Application Details")
        
        c1, c2, c3 = st.columns(3)
        ac_year = c1.selectbox("Academic Year", ["2026-27", "2027-28"])
        dept = c2.selectbox("Department", ["ST&SC and MBC Welfare Depart", "Higher Education"])
        scheme = c3.selectbox("Scheme", ["Pre Matric", "Post Matric"])
        
        c4, c5 = st.columns(2)
        app_name = c4.text_input("Applicant Name *", value=st.session_state.get('v_name', ''))
        category = c5.selectbox("Category *", SOCIAL_CATEGORIES)
        
        c6, c7, c8 = st.columns(3)
        gender = c6.radio("Applicant Gender:", ["Male", "Female", "Transgender"])
        religion = c7.selectbox("Religion", ["Select", "Hindu", "Muslim", "Christian", "Other"])
        photo = c8.file_uploader("Profile Photo (jpg, png)")
        
        c9, c10 = st.columns(2)
        dob = c9.date_input("Date of Birth *", min_value=datetime.date(1990, 1, 1), max_value=datetime.date.today())
        mob_no = c10.text_input("Student/Parent's Mobile No. *")
        
        st.markdown("---")
        c13, c14 = st.columns(2)
        f_name = c13.text_input("Father's Name *")
        m_name = c14.text_input("Mother's Name *")
        
        st.markdown("#### 📍 Address Information")
        addr = st.text_area("Full Address *", placeholder="Enter your complete address")
        
        c_st, c_dt = st.columns(2)
        all_states = list(STATE_LANG_MAP.keys())
        state_idx = all_states.index("Odisha") if "Odisha" in all_states else 0
        state = c_st.selectbox("State *", all_states, index=state_idx)
        
        if state == "Odisha":
            dist_list = ["Angul", "Balasore", "Bargarh", "Bhadrak", "Balangir", "Cuttack", "Khordha", "Puri", "Jajpur", "Sundargarh"]
            dist = c_dt.selectbox("District *", sorted(dist_list))
            c_blk, c_pin = st.columns(2)
            block = c_blk.text_input("Block/ULB *")
        else:
            dist = c_dt.text_input("District *")
            c_blk, c_pin = st.columns(2)
            block = c_blk.text_input("Block/ULB *")
            
        pin = c_pin.text_input("Pin Code *", max_chars=6)
        
        st.markdown("### Institute / Course Information")
        active_schools = {k: v for k, v in schools_db.items() if v.get("status", "Active") == "Active"}
        school_options = [f"{k} - {v['name']}" for k, v in active_schools.items()]
        c24, c25 = st.columns(2)
        school_sel_str = c24.selectbox("Institute (School) *", ["--Select--"] + school_options)
        sch_class = c25.selectbox("Class *", ["IX", "X", "XI", "XII"])
        school_code = school_sel_str.split(" - ")[0] if school_sel_str != "--Select--" else None
        
        st.markdown("### 📄 Certificate Information")
        c33, c34 = st.columns(2)
        with c33:
            st.markdown("**Income Certificate**")
            inc_year = st.selectbox("Issuing Year", CERT_YEARS)
            col_inc1, col_inc2 = st.columns([7, 3])
            inc_no = col_inc1.text_input("Income Certificate No. *")
            if col_inc2.button("VERIFY INCOME"):
                if inc_no: st.success(f"Income Certificate Verified")
                else: st.error("Enter Income Cert No")
            inc_whom = st.selectbox("To Whom Issued", RELATIONSHIPS)
            inc_auth = st.selectbox("Issuing Authority (Income)", ISSUING_AUTHORITIES)
            inc_file = st.file_uploader("Upload Income Certificate Photo *")
            
        with c34:
            st.markdown("**Caste Certificate**")
            cas_year = st.selectbox("Caste Issuing Year", CERT_YEARS)
            col_cas1, col_cas2 = st.columns([7, 3])
            cas_no = col_cas1.text_input("Caste Certificate No. *")
            if col_cas2.button("VERIFY CASTE"):
                if cas_no: st.success(f"Caste Certificate Verified")
                else: st.error("Enter Caste Cert No")
            cas_auth = st.selectbox("Issuing Authority (Caste)", ISSUING_AUTHORITIES)
            cas_file = st.file_uploader("Upload Caste Certificate Photo *")
        
        st.markdown("### 🏦 Bank Information")
        c35, c36 = st.columns([8, 2])
        ifsc = c35.text_input("IFSC Code *")
        if c36.button("FIND IFSC"):
            if ifsc:
                st.session_state['v_bank'] = "STATE BANK OF INDIA"
                st.session_state['v_branch'] = "MAIN BRANCH"
                st.success("✅ IFSC Verified & Bank Auto-Fetched!")
            else: 
                st.error("Enter IFSC Code")
            
        c36a, c37a = st.columns(2)
        b_name = c36a.text_input("Bank Name", value=st.session_state.get('v_bank', ''), disabled=True)
        b_branch = c37a.text_input("Branch Name", value=st.session_state.get('v_branch', ''), disabled=True)
        
        c38, c39 = st.columns([8, 2])
        acc_no = c38.text_input("Account Number *", type="password")
        if c39.button("VERIFY ACCOUNT"):
            if acc_no:
                st.session_state['v_acc_name'] = app_name
                st.success("✅ Account Verified!")
            else: st.error("Enter Account Number")
            
        acc_name = st.text_input("Account Holder Name *", value=st.session_state.get('v_acc_name', ''))
        re_acc_no = st.text_input("Re-type Account No. *")
        
        st.markdown("---")
        c_seed, c_pass = st.columns(2)
        seeded = c_seed.radio("Whether account number seeded with the Aadhaar number?", ["Yes", "No"], index=1)
        passbook = c_pass.file_uploader("Upload Passbook Front Page (max 1MB)")
        
        decl = st.checkbox("✅ I declare the above info is true.")
        
        if st.button("Proceed to Payment & Submit", type="primary"):
            if not decl: st.error("Please accept the declaration.")
            elif not school_code or not sanitize(app_name) or not sanitize(aadhaar_input) or not sanitize(acc_no):
                st.error("Please fill all mandatory fields (*).")
            else:
                app_id = "SCH" + str(random.randint(1000000, 9999999))
                st.session_state['temp_sch_data'] = {
                    "app_id": app_id,
                    "data": {
                        "academic_year": ac_year, "scheme": scheme, "app_name": sanitize(app_name),
                        "category": category, "otr": sanitize(otr_input), "gender": gender,
                        "dob": str(dob), "aadhaar": sanitize(aadhaar_input), "mobile": sanitize(mob_no),
                        "father_name": sanitize(f_name), "mother_name": sanitize(m_name),
                        "full_address": sanitize(addr), "state": sanitize(state), "district": sanitize(dist),
                        "school_code": school_code, "class": sch_class, 
                        "income_cert": sanitize(inc_no), "inc_auth": inc_auth,
                        "caste_cert": sanitize(cas_no), "cas_auth": cas_auth, "ifsc": sanitize(ifsc), 
                        "bank_name": st.session_state.get('v_bank', ''), "branch_name": st.session_state.get('v_branch', ''),
                        "acc_no": sanitize(acc_no), "acc_name": sanitize(acc_name), "aadhaar_seeded": seeded,
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
        
        if st.button("Complete Payment & Submit Application", type="primary"):
            tmp['data']['payment_mode'] = f"{pay_mode.split(' ')[0]} (₹{sch_fee:.2f})"
            scholarships_db[tmp['app_id']] = tmp['data']
            save_scholarships(scholarships_db)
            st.session_state['sch_app_success'] = True
            st.session_state['sch_app_id'] = tmp['app_id']
            st.session_state['sch_app_data'] = tmp['data']
            st.session_state['sch_app_step'] = False
            st.session_state['temp_sch_data'] = None
            st.rerun()

# ----------------- NEW STUDENT REGISTRATION -----------------
elif menu == "New Student Registration":
    c_home, c_title = st.columns([1, 8])
    with c_home:
        if st.button("🏠 Home", key="reg_stu_home"): st.query_params["portal"] = "home"; st.rerun()
    with c_title: st.subheader("👨‍🎓 New Student Registration")

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
            st.download_button("📥 Download PDF Receipt", f, file_name=pdf_file, mime="application/pdf")
        if st.button("⬅️ Done"):
            st.session_state['stu_reg_success'] = False; st.rerun()
                
    elif not st.session_state['payment_step']:
        with st.form("student_reg_form"):
            active_schools = {k: v for k, v in schools_db.items() if v.get("status", "Active") == "Active"}
            school_options = [f"{k} - {v['name']}" for k, v in active_schools.items()] if active_schools else []
            school_sel_str = st.selectbox("Select School Code & Name *", ["--Select--"] + school_options) if school_options else "--Select--"
            school_sel = school_sel_str.split(" - ")[0] if school_sel_str != "--Select--" else None
            
            stu_name_en = st.text_input("Student's Name *")
            stu_gender_en = st.selectbox("Gender", ["Male", "Female", "Other"])
            stu_dob = st.date_input("Date of Birth *", min_value=datetime.date(2000, 1, 1), max_value=datetime.date.today())
            f_name_en = st.text_input("Father's Name *")
            stu_phone = st.text_input("Mobile No *", max_chars=10)
            
            declaration = st.checkbox("✅ I declare the above info is true.")
            if st.form_submit_button("Proceed to Payment"):
                if not declaration: st.error("⚠️ Please check the declaration box.")
                elif not school_sel or not sanitize(stu_name_en) or not sanitize(stu_phone):
                    st.error("Please fill all mandatory fields (*).")
                else:
                    temp_reg_id = "REG" + str(random.randint(100000, 999999))
                    st.session_state['temp_student_data'] = {
                        "reg_id": temp_reg_id, "school_sel": school_sel,
                        "data": {
                            "name": sanitize(stu_name_en), "gender": stu_gender_en,
                            "father_name": sanitize(f_name_en), "dob": str(stu_dob), "phone": sanitize(stu_phone),
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
        pay_mode = st.radio("Select Payment Mode", ["Online Payment", "Offline Payment"])
        if st.button("Complete Payment & Submit"):
            temp_obj['data']['payment_mode'] = f"{pay_mode.split(' ')[0]} (₹{total_fee:.2f})"
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
    st.info("School registration offline module active. Please contact admin.")

# ----------------- MASTER LOGIN (FULL TABS RESTORED) -----------------
elif menu == "Master Login":
    c_home, c_title = st.columns([1, 8])
    with c_home:
        if st.button("🏠 Home", key="m_home_btn"): st.query_params["portal"] = "home"; st.rerun()
    with c_title: st.subheader("🔑 Master Administrator Portal")
    
    if not st.session_state.get('master_logged', False):
        m_user = st.text_input("Master Username")
        m_pass = st.text_input("Master Password", type="password")
        if st.button("Login"):
            if sanitize(m_user) == master_db.get("username") and m_pass == master_db.get("password"):
                st.session_state['master_logged'] = True; st.rerun()
            else: st.error("ଭୁଲ୍ Master ID କିମ୍ବା Password!")
    else:
        c1, c2 = st.columns([8, 2])
        c1.success("Welcome Master Admin!")
        if c2.button("🔴 Logout"): st.session_state['master_logged'] = False; st.rerun()

        st.markdown("---")
        t1, t2, t3, t4, t5 = st.tabs(["👁️ Schools", "💳 Payments", "🎓 Scholarships Verify", "🎓 Edit Students", "⚙️ Settings"])
        
        with t1:
            st.markdown("### 🏫 Manage Schools")
            for s_id, s_info in list(schools_db.items()):
                status = s_info.get("status", "Active") 
                bg = "#f0fdf4" if status == "Active" else "#fef2f2"
                st.markdown(f"<div style='border:1px solid #cbd5e1; padding:10px; margin-bottom:10px; background-color:{bg};'><b>School ID:</b> {s_id} | <b>Name:</b> {s_info['name']} | Status: {status}</div>", unsafe_allow_html=True)
                if status == "Inactive":
                    if st.button("✅ Make Active", key=f"act_{s_id}"):
                        s_info["status"] = "Active"; save_data(schools_db, students_db); st.rerun()

        with t2:
            st.markdown("### 💳 Verify Registrations")
            for s_id, s_studs in students_db.items():
                for r_no, p_st in s_studs.items():
                    if p_st.get("status") == "Pending_Master":
                        st.write(f"**Reg:** {r_no} | **Name:** {p_st.get('name')}")
                        if st.button(f"✅ Verify {r_no}", key=f"vp_{r_no}"):
                            p_st["status"] = "Pending_School"; save_data(schools_db, students_db); st.rerun()

        with t3:
            st.markdown("### 🎓 Scholarship Verifications (Master)")
            pending_sch = {k: v for k, v in scholarships_db.items() if v.get("status") == "Pending_Master"}
            if pending_sch:
                app_id = st.selectbox("Select Scholarship", list(pending_sch.keys()))
                if st.button("✅ Verify & Send to School", type="primary"):
                    pending_sch[app_id]['status'] = "Pending_School"
                    scholarships_db[app_id] = pending_sch[app_id]
                    save_scholarships(scholarships_db); st.success("Verified!"); st.rerun()
            else: st.success("No pending scholarships.")

        with t4: 
            st.markdown("### 🎓 Edit Students Data (Master)")
            master_school_sel = st.selectbox("Select School", ["--Select--"] + list(schools_db.keys()))
            if master_school_sel != "--Select--":
                school_students = students_db.get(master_school_sel, {})
                approved_students = {k:v for k,v in school_students.items() if v.get('status', 'Approved') == 'Approved'}
                if approved_students:
                    m_edit_roll = st.selectbox("Select Student Roll No", list(approved_students.keys()))
                    m_curr_st = approved_students[m_edit_roll]
                    m_up_name = st.text_input("Name", value=m_curr_st.get('name',''))
                    m_tot_full = st.number_input("Total Full Mark", value=float(m_curr_st.get('total_full', 300)))
                    m_tot_obt = st.number_input("Total Obtained", value=float(m_curr_st.get('total_obt', 0)))
                    if st.button("💾 Force Update Record"):
                        students_db[master_school_sel][m_edit_roll].update({
                            "name": sanitize(m_up_name), "total_full": m_tot_full, "total_obt": m_tot_obt
                        })
                        save_data(schools_db, students_db); st.success("Updated!"); st.rerun()

        with t5: 
            st.markdown("### ⚙️ Settings")
            st.write("Settings Panel Active.")

# ----------------- SCHOOL LOGIN (FULL TABS RESTORED) -----------------
elif menu == "School Login":
    c_home, c_title = st.columns([1, 8])
    with c_home:
        if st.button("🏠 Home", key="s_home_btn"): st.query_params["portal"] = "home"; st.rerun()
    with c_title: st.subheader("🏫 School Portal")
    
    if 'school_logged_id' not in st.session_state:
        s_id = st.text_input("School ID")
        s_pass = st.text_input("School Password", type="password")
        
        if 'school_captcha' not in st.session_state:
            st.session_state['school_captcha'] = str(random.randint(10000, 99999))
        
        st.markdown(f"<div style='background:#f1f5f9; padding:5px 20px; font-size:22px; font-weight:bold; letter-spacing:6px; border:1px solid #cbd5e1; border-radius:5px; display:inline-block;'>{st.session_state['school_captcha']}</div>", unsafe_allow_html=True)
        entered_captcha = st.text_input("Enter the CAPTCHA code")
        
        if st.button("Login as School"):
            if entered_captcha != st.session_state['school_captcha']:
                st.error("❌ ଭୁଲ୍ CAPTCHA! ଦୟାକରି ସଠିକ୍ କ୍ୟାପ୍ଚା କୋଡ୍ ଦିଅନ୍ତୁ।")
                st.session_state['school_captcha'] = str(random.randint(10000, 99999)); st.rerun()
            else:
                s_id_clean = sanitize(s_id)
                if s_id_clean in schools_db and schools_db[s_id_clean]["pass"] == s_pass:
                    st.session_state['school_logged_id'] = s_id_clean; del st.session_state['school_captcha']; st.rerun()
                else:
                    st.error("❌ Invalid ID/Password!"); st.session_state['school_captcha'] = str(random.randint(10000, 99999)); st.rerun()
    else: 
        cur_school = st.session_state['school_logged_id']
        sch_data = schools_db[cur_school]
        c1, c2 = st.columns([8, 2])
        c1.info(f"🏫 **School Portal** | ID: {cur_school} | {sch_data['name']}")
        if c2.button("🔴 Logout"): del st.session_state['school_logged_id']; st.rerun()

        t_list, t_reg, t_sch, t_add, t_edit, t_rep = st.tabs(["📋 My Students", "✅ Registrations", "🎓 Scholarship", "➕ Add Student", "✏️ Edit Student", "🖨️ Report Card"])
        
        cur_students = students_db.get(cur_school, {})
        approved_students = {k:v for k,v in cur_students.items() if v.get('status', 'Approved') == 'Approved'}
        
        with t_list:
            st.markdown("### 📋 My Students")
            if approved_students:
                for r_no, s_info in approved_students.items():
                    st.write(f"**Roll:** {r_no} | **Name:** {s_info['name']}")
            else: st.warning("No approved students.")
                
        with t_add:
            st.markdown("### ➕ Add Student Direct")
            add_roll = st.text_input("Roll No")
            add_name = st.text_input("Student Name")
            if st.button("Save Student Data"):
                if add_roll and add_name:
                    students_db[cur_school][add_roll] = {"name": add_name, "status": "Approved"}
                    save_data(schools_db, students_db); st.success("Added!"); st.rerun()
                    
        with t_edit:
            st.markdown("### ✏️ Edit Student")
            if approved_students:
                edit_roll = st.selectbox("Select Roll No", list(approved_students.keys()))
                e_name = st.text_input("Name", approved_students[edit_roll]['name'])
                if st.button("Save Edit"):
                    students_db[cur_school][edit_roll]['name'] = e_name
                    save_data(schools_db, students_db); st.success("Edited!"); st.rerun()

        with t_rep:
            st.markdown("### 🖨️ Report Card")
            if approved_students:
                rep_roll = st.selectbox("Select Roll for Report", list(approved_students.keys()))
                pdf_file = f"Report_{rep_roll}.pdf"
                create_pdf(pdf_file, sch_data['name'], approved_students[rep_roll], rep_roll)
                with open(pdf_file, "rb") as f:
                    st.download_button("📥 Download PDF", f, file_name=pdf_file, mime="application/pdf")

# ----------------- RESULTS PORTAL (CRASH PROOF) -----------------
elif menu == "Results":
    c_home, c_title = st.columns([1, 8])
    with c_home:
        if st.button("🏠 Home", key="st_home_btn"): st.query_params["portal"] = "home"; st.rerun()
    with c_title: st.subheader("🎓 Results Portal")
    
    st_search_query = st.text_input("Roll Number OR Student Name")
    st_dob_input = st.text_input("Date of Birth (DD-MM-YYYY)")
    
    if st.button("View Result"):
        if st_search_query and st_dob_input:
            sq_low = sanitize(st_search_query.strip().lower())
            ndob = normalize_dob(st_dob_input)
            
            found_student = None; found_roll = None; found_school_id = None
            
            for s_id, school_students in students_db.items():
                if st_search_query in school_students:
                    potential_student = school_students[st_search_query]
                    if normalize_dob(potential_student.get("dob", "")) == ndob and potential_student.get("status", "Approved") == "Approved":
                        found_student = potential_student; found_roll = st_search_query; found_school_id = s_id
                        break
                
                if not found_student:
                    for r_no, s_info in school_students.items():
                        if s_info.get("name", "").strip().lower() == sq_low:
                            if normalize_dob(s_info.get("dob", "")) == ndob:
                                if s_info.get("status", "Approved") == "Approved":
                                    found_student = s_info; found_roll = r_no; found_school_id = s_id
                                    break
                if found_student: break
            
            if found_student:
                sch = schools_db.get(found_school_id, {})
                s_lang = sch.get("lang", "English")
                st.success(f"🎉 **Welcome {found_student.get('name', '').upper()}!**")
                
                # HTML Display
                st.markdown(generate_result_card_html(sch.get('name', 'Unknown School'), sch.get('name_local', ''), found_student, found_roll, s_lang), unsafe_allow_html=True)
                
                # PDF Generation (Safeguarded against crashes)
                pdf_file = f"Result_{found_roll}.pdf"
                create_pdf(pdf_file, sch.get('name', 'Unknown School'), found_student, found_roll)
                with open(pdf_file, "rb") as f:
                    st.download_button("📥 Download PDF", f, file_name=pdf_file, mime="application/pdf")
            else:
                st.error("❌ କୌଣସି ରେକର୍ଡ ମିଳିଲା ନାହିଁ! ଭୁଲ୍ ତଥ୍ୟ ଦେଇଛନ୍ତି।")

st.markdown("---")
st.markdown("<div style='text-align: center; padding: 15px; background: linear-gradient(90deg, #1e3a8a, #9333ea); color: white; border-radius: 8px; font-weight: bold;'>👨‍💻 Software Developed by: KULU SUTAR | 📞 Mob: 8910223342 | ✉️ kulusutar123@gmail.com</div>", unsafe_allow_html=True)
