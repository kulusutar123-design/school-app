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
import sqlite3

# ==========================================
# 🔒 CRASH PROTECTION & ANTI-HACK LOCKS
# ==========================================
file_lock = threading.Lock()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def sanitize(text):
    if isinstance(text, str):
        return html.escape(text.strip())
    return text

@st.cache_resource
def get_db_connection():
    conn = sqlite3.connect('school_ultimate_secure.db', check_same_thread=False, timeout=60)
    conn.execute('PRAGMA journal_mode=WAL;') 
    conn.execute('PRAGMA synchronous=NORMAL;')
    conn.execute('PRAGMA cache_size=-64000;') 
    
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS master (id TEXT PRIMARY KEY, data TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS schools (id TEXT PRIMARY KEY, data TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS students 
                 (roll_no TEXT, dob TEXT, school_id TEXT, name TEXT, data TEXT, status TEXT, PRIMARY KEY (school_id, roll_no))''')
    c.execute('''CREATE INDEX IF NOT EXISTS idx_student_search ON students(roll_no, dob, name)''')
    
    c.execute("SELECT data FROM master WHERE id='master'")
    if not c.fetchone():
        def_m = {"username": "master", "password": hash_password("master123"), "email": "admin@school.com", "phone": "9999999999", "upi_id": "school@sbi", "reg_fee": 150.0, "gst_percent": 18.0, "school_reg_fee": 1000.0, "school_gst_percent": 18.0}
        c.execute("INSERT INTO master VALUES ('master', ?)", (json.dumps(def_m),))
    conn.commit()
    return conn

conn = get_db_connection()

def get_master():
    row = conn.cursor().execute("SELECT data FROM master WHERE id='master'").fetchone()
    return json.loads(row[0]) if row else {}

def save_master(data):
    with file_lock:
        conn.cursor().execute("UPDATE master SET data=? WHERE id='master'", (json.dumps(data),))
        conn.commit()

def get_school(s_id):
    row = conn.cursor().execute("SELECT data FROM schools WHERE id=?", (s_id,)).fetchone()
    return json.loads(row[0]) if row else None

def get_all_schools():
    return {row[0]: json.loads(row[1]) for row in conn.cursor().execute("SELECT id, data FROM schools").fetchall()}

def save_school(s_id, data):
    with file_lock:
        conn.cursor().execute("REPLACE INTO schools (id, data) VALUES (?, ?)", (sanitize(s_id), json.dumps(data)))
        conn.commit()

def delete_school(s_id):
    with file_lock:
        conn.cursor().execute("DELETE FROM schools WHERE id=?", (s_id,))
        conn.cursor().execute("DELETE FROM students WHERE school_id=?", (s_id,))
        conn.commit()

def get_students_by_school(s_id, status=None):
    if status:
        return {row[0]: json.loads(row[1]) for row in conn.cursor().execute("SELECT roll_no, data FROM students WHERE school_id=? AND status=?", (s_id, status)).fetchall()}
    return {row[0]: json.loads(row[1]) for row in conn.cursor().execute("SELECT roll_no, data FROM students WHERE school_id=?", (s_id,)).fetchall()}

def get_all_students_by_status(status):
    return [(row[0], row[1], json.loads(row[2])) for row in conn.cursor().execute("SELECT school_id, roll_no, data FROM students WHERE status=?", (status,)).fetchall()]

def save_student(s_id, roll_no, data, status="Approved"):
    n_dob = normalize_dob(data.get('dob',''))
    n_name = data.get('name','').lower()
    with file_lock:
        conn.cursor().execute("REPLACE INTO students (roll_no, dob, school_id, name, data, status) VALUES (?, ?, ?, ?, ?, ?)",
                              (sanitize(roll_no), n_dob, s_id, n_name, json.dumps(data), status))
        conn.commit()

def delete_student(s_id, roll_no):
    with file_lock:
        conn.cursor().execute("DELETE FROM students WHERE school_id=? AND roll_no=?", (s_id, roll_no))
        conn.commit()

# ==========================================
# 🌐 APP URL SETTING & CONFIG
# ==========================================
APP_URL = "http://localhost:8501"

st.set_page_config(page_title="Advanced School Management System", layout="wide")
st.markdown("<style>#MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)

STATE_LANG_MAP = {
    "Andhra Pradesh": "Telugu", "Arunachal Pradesh": "English", "Assam": "Assamese", "Bihar": "Hindi", "Chhattisgarh": "Hindi",
    "Goa": "Konkani", "Gujarat": "Gujarati", "Haryana": "Hindi", "Himachal Pradesh": "Hindi", "Jharkhand": "Hindi",
    "Karnataka": "Kannada", "Kerala": "Malayalam", "Madhya Pradesh": "Hindi", "Maharashtra": "Marathi", "Manipur": "English",
    "Meghalaya": "English", "Mizoram": "English", "Nagaland": "English", "Odisha": "Odia", "Punjab": "Punjabi",
    "Rajasthan": "Hindi", "Sikkim": "English", "Tamil Nadu": "Tamil", "Telangana": "Telugu", "Tripura": "Bengali",
    "Uttar Pradesh": "Hindi", "Uttarakhand": "Hindi", "West Bengal": "Bengali", "Delhi": "Hindi"
}

COUNTRIES = ["Yes - Indian National", "No - Other Country"]
SOCIAL_CATEGORIES = ["General", "SC (Scheduled Caste)", "ST (Scheduled Tribe)", "OBC (Other Backward Class)", "SEBC", "Minority", "Others"]

@st.cache_data(show_spinner=False)
def auto_translate(text, lang_name):
    if lang_name == "English" or not text: return text
    LC = {"Odia":"or", "Hindi":"hi", "Bengali":"bn", "Telugu":"te", "Tamil":"ta", "Marathi":"mr", "Gujarati":"gu", "Assamese":"as"}
    tc = LC.get(lang_name, "en")
    if tc == "en": return text
    try:
        ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl={tc}&dt=t&q={urllib.parse.quote(text)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=3, context=ctx)
        return "".join([s[0] for s in json.loads(res.read().decode('utf-8'))[0]])
    except: return text 

def t(eng_text, lang):
    tr = {
        "School Portal": {"Odia": "ସ୍କୁଲ୍ ପୋର୍ଟାଲ୍", "Hindi": "स्कूल पोर्टल"},
        "Logout": {"Odia": "ଲଗ୍ ଆଉଟ୍", "Hindi": "लॉग आउट"},
        "ANNUAL EXAMINATION": {"Odia": "ବାର୍ଷିକ ପରୀକ୍ଷା", "Hindi": "वार्षिक परीक्षा"},
        "CERTIFICATE-CUM-MARK SHEET": {"Odia": "ପ୍ରମାଣପତ୍ର ଏବଂ ମାର୍କସିଟ୍", "Hindi": "प्रमाणपत्र सह अंकतालिका"},
        "ROLL NO": {"Odia": "ରୋଲ୍ ନମ୍ବର", "Hindi": "रोल नंबर"},
        "CLASS": {"Odia": "ଶ୍ରେଣୀ", "Hindi": "कक्षा"},
        "NAME": {"Odia": "ନାମ", "Hindi": "नाम"},
        "DOB": {"Odia": "ଜନ୍ମ ତାରିଖ", "Hindi": "जन्म तिथि"},
        "SUBJECT": {"Odia": "ବିଷୟ", "Hindi": "विषय"},
        "TOTAL MARKS": {"Odia": "ସମୁଦାୟ ନମ୍ବର", "Hindi": "कुल प्राप्तांक"},
        "GRADE": {"Odia": "ଗ୍ରେଡ୍", "Hindi": "ग्रेड"},
    }
    return tr.get(eng_text, {}).get(lang, eng_text)

def number_to_words(num):
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

# --- OLD JSON DATA LOAD/SAVE FUNCTIONS (PRESERVES EXISTING DATA) ---
SCHOOLS_FILE = "schools.json"
STUDENTS_FILE = "students.txt"
MASTER_FILE = "master.json"

def load_master_data_json():
    default_master = {
        "username": "master", 
        "password": "master123", 
        "email": "admin@school.com", 
        "phone": "9999999999", 
        "upi_id": "school@sbi",
        "reg_fee": 150.0,
        "gst_percent": 18.0,
        "school_reg_fee": 1000.0,
        "school_gst_percent": 18.0
    }
    if os.path.exists(MASTER_FILE):
        try:
            with open(MASTER_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if content.strip():
                    m = json.loads(content)
                    if "upi_id" not in m: m["upi_id"] = "school@sbi"
                    if "reg_fee" not in m: m["reg_fee"] = 150.0
                    if "gst_percent" not in m: m["gst_percent"] = 18.0
                    if "school_reg_fee" not in m: m["school_reg_fee"] = 1000.0
                    if "school_gst_percent" not in m: m["school_gst_percent"] = 18.0
                    return m
        except Exception:
            pass
    return default_master

def save_master_data_json(data):
    with file_lock:
        with open(MASTER_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

def load_data_json():
    schools = {"S001": {"name": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "name_local": "", "address": "", "address_local": "", "hm_name": "", "hm_phone": "", "pass": "admin123", "state": "Odisha", "lang": "Odia", "status": "Active"}}
    students = {}
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

def save_data_json(schools, students):
    with file_lock:
        with open(SCHOOLS_FILE, "w", encoding="utf-8") as f:
            json.dump(schools, f, indent=4)
        with open(STUDENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(students, f, indent=4)

# ==========================================
# 🎨 RESULT CARD & RECEIPT PDF GENERATORS
# ==========================================
def create_student_receipt_pdf(filename, reg_id, s_data):
    c = canvas.Canvas(filename, pagesize=letter)
    c.setStrokeColorRGB(0.1, 0.2, 0.5); c.setLineWidth(4); c.rect(30, 30, 552, 732, stroke=1, fill=0)
    c.setFillColorRGB(0.1, 0.2, 0.5); c.setFont("Times-Bold", 22); c.drawCentredString(300, 720, "STUDENT REGISTRATION RECEIPT")
    c.setFillColorRGB(0, 0, 0); c.setFont("Helvetica-Bold", 12); c.drawString(50, 670, f"REGISTRATION ID: {reg_id}")
    c.setFont("Helvetica", 12); y = 640
    c.drawString(50, y, f"Student Name: {s_data.get('name', '').upper()}"); y -= 25
    c.drawString(50, y, f"Father's Name: {s_data.get('father_name', '').upper()}"); y -= 25
    c.drawString(50, y, f"Date of Birth: {s_data.get('dob', '')}"); y -= 25
    c.drawString(50, y, f"Gender: {s_data.get('gender', '')}"); y -= 25
    c.drawString(50, y, f"Category: {s_data.get('category', 'General')}"); y -= 25
    c.drawString(50, y, f"Contact No: {s_data.get('phone', '')}"); y -= 25
    c.drawString(50, y, f"Applied School Code: {s_data.get('school_code', 'N/A')}"); y -= 25
    c.drawString(50, y, f"Payment Details: {s_data.get('payment_mode', 'N/A')}"); y -= 25
    c.drawString(50, y, f"Status: {s_data.get('status', 'Pending')}"); y -= 25
    c.drawString(50, y, f"Application Date: {s_data.get('pub_date', datetime.date.today().strftime('%Y-%m-%d'))}"); y -= 40
    c.line(50, y, 550, y); y -= 20
    c.setFont("Helvetica-Oblique", 10); c.drawCentredString(300, y, "This is a computer-generated receipt. Please keep it safe.")
    try: bc = code128.Code128(str(reg_id), barHeight=30, barWidth=1.5); bc.drawOn(c, 50, 70)
    except: pass
    c.save()

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
    c.setFont("Helvetica-Oblique", 10); c.drawCentredString(300, y, "This is a computer-generated receipt. Please keep it safe.")
    try: bc = code128.Code128(str(sch_id), barHeight=30, barWidth=1.5); bc.drawOn(c, 50, 70)
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

    rows_html = "".join([f"<tr style='border-bottom: 1px solid {b_col};'><td style='padding: 8px; border-right: 1px solid {b_col}; text-align: left; font-weight: bold;'>{sub.upper()}</td><td style='padding: 8px; border-right: 1px solid {b_col};'>{m['full']}</td><td style='padding: 8px; font-weight: bold;'>{m['obt']}</td></tr>" for sub, m in st_data.get('subjects', {}).items()])

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
                <tr><td><span style='color:{b_col};'>ROLL NO:</span> {roll_no}</td><td style='text-align: right;'><span style='color:{b_col};'>CLASS:</span> {st_data.get('class', '')}</td></tr>
                <tr><td><span style='color:{b_col};'>PEN NO:</span> {st_data.get('pen_no', '')}</td><td style='text-align: right;'><span style='color:{b_col};'>APAAR NO:</span> {st_data.get('apaar_no', '')}</td></tr>
            </table>
            <table style='width: 100%; font-size: 14px; margin-bottom: 15px; text-transform: uppercase; line-height: 1.8;'>
                <tr><td style='width: 250px; color: {b_col}; font-weight: bold;'>Certify that / {t('NAME', s_lang)}</td><td><b>{s_name_en}</b><br><span style='font-size:14px; text-transform:none;'>{t_stu}</span></td></tr>
                <tr><td style='color: {b_col}; font-weight: bold;'>Mother's Name</td><td><b>{m_name_en}</b><br><span style='font-size:14px; text-transform:none;'>{t_mot}</span></td></tr>
                <tr><td style='color: {b_col}; font-weight: bold;'>Father's Name</td><td><b>{f_name_en}</b><br><span style='font-size:14px; text-transform:none;'>{t_fat}</span></td></tr>
                <tr><td style='color: {b_col}; font-weight: bold;'>Date of Birth</td><td><b>{disp_dob}</b></td></tr>
                <tr><td style='color: {b_col}; font-weight: bold;'>Category</td><td><b>{st_data.get('category', 'General')}</b></td></tr>
            </table>
            <p style='color: {b_col}; text-align: center; margin-bottom: 20px; font-style:italic;'>Passed the Annual Examination held in {st_data.get('batch', '')}.</p>
            <table style='width: 100%; border-collapse: collapse; border: 2px solid {b_col}; text-align: center; font-size: 13px;'>
                <tr style='color: {b_col}; background-color: {t_bg}; border-bottom: 2px solid {b_col};'>
                    <th style='padding: 8px; border-right: 1px solid {b_col};'>SUBJECT</th><th style='padding: 8px; border-right: 1px solid {b_col};'>FULL MARKS</th><th style='padding: 8px;'>MARKS SECURED</th>
                </tr>
                {rows_html}
                <tr style='color: {b_col}; font-weight: bold; background-color: {t_bg}; border-top: 2px solid {b_col};'>
                    <td style='padding: 10px; border-right: 1px solid {b_col}; text-align: right;'>TOTAL MARKS</td><td style='padding: 10px; border-right: 1px solid {b_col};'>{st_data.get('total_full', 0)}</td><td style='padding: 10px; color:#000;'>{tot_obt}</td>
                </tr>
            </table>
            <div style='text-align: center; font-weight: bold; font-size: 14px; margin-top: 20px;'>( {w_tot_en} ) <br><span style='font-size:13px; font-weight:normal;'>({t_w_tot})</span></div>
            <table style='width: 100%; margin-top: 20px; text-align: center; color: {b_col};'>
                <tr>
                    <td style='width: 33%; vertical-align: bottom;'><img src='{bc_url}' style='height: 35px; margin-bottom: 10px;'/><br><div style='font-size: 11px;'>DATE OF PUBLICATION</div><div style='font-weight: bold; font-size: 14px; margin-bottom: 30px;'>{disp_pub_date}</div><div style='border-bottom: 1px solid {b_col}; width: 80%; margin: auto;'></div><div style='font-size: 11px; font-weight: bold; margin-top:5px;'>HM SIGNATURE</div></td>
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
    
    y = t_b_y - 45; c.setFillColorRGB(0,0,0); c.setFont("Helvetica-Bold", 10); c.drawCentredString(300, y, f"( {number_to_words(st_data.get('total_obt', 0))} )")
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
schools_db, students_db = load_data_json()
master_db = load_master_data_json()

# ----------------- STABLE ROUTING -----------------
menu_items = ["Home Page", "New Student Registration", "New School Registration", "Master Login", "School Login", "Results"]
portal_map = {"home": 0, "reg_student": 1, "reg_school": 2, "master": 3, "school": 4, "student": 5}
portal_param = st.query_params.get("portal", "home")
default_idx = portal_map.get(portal_param, 0)

# 🎨 Custom Background Color option in sidebar
st.sidebar.markdown("---")
user_bg_color = st.sidebar.color_picker("🎨 Custom Background Color", "#ffffff")
st.markdown(f"<style>.stApp {{ background-color: {user_bg_color} !important; }}</style>", unsafe_allow_html=True)

menu = st.sidebar.selectbox("🎯 Navigation Menu", menu_items, index=default_idx)

if menu == "Home Page": st.query_params["portal"] = "home"
elif menu == "New Student Registration": st.query_params["portal"] = "reg_student"
elif menu == "New School Registration": st.query_params["portal"] = "reg_school"
elif menu == "Master Login": st.query_params["portal"] = "master"
elif menu == "School Login": st.query_params["portal"] = "school"
elif menu == "Results": st.query_params["portal"] = "student"

classes_list = [str(i) for i in range(1, 11)]
batches_list = [f"{y}-{y+1}" for y in range(2020, 2051)]

# ----------------- HOME PAGE (BEAUTIFUL DYNAMIC UI) -----------------
if menu == "Home Page":
    st.markdown("""
    <style>
    @keyframes colorChange {
        0% { background-color: #e0e7ff; }
        25% { background-color: #fce7f3; }
        50% { background-color: #ffedd5; }
        75% { background-color: #dcfce7; }
        100% { background-color: #e0e7ff; }
    }
    .dynamic-bg-box {
        animation: colorChange 15s infinite alternate;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        margin-bottom: 25px;
        border: 2px solid #cbd5e1;
    }
    .carousel { width: 100%; height: 380px; overflow: hidden; border-radius: 10px; position: relative; border: 4px solid #1e3a8a; box-shadow: 0 4px 10px rgba(0,0,0,0.3); background-color: #000; }
    .marquee-images { white-space: nowrap; height: 100%; display: flex; align-items: center; }
    .marquee-img { height: 350px; border-radius: 10px; margin-right: 20px; object-fit: contain; }
    .carousel-overlay { position: absolute; bottom: 0; background: rgba(30,58,138,0.85); width: 100%; color: white; text-align: center; padding: 12px; font-weight: bold; font-size: 20px; letter-spacing: 1px; }
    
    .login-card { background: white; border: 1px solid #cbd5e1; border-bottom: 5px solid #fbbf24; border-radius: 8px; padding: 25px; margin-bottom: 20px; text-align: center; text-decoration: none; display: block; color: #1e3a8a; box-shadow: 0 4px 6px rgba(0,0,0,0.05); transition: 0.3s; }
    .login-card:hover { background: #f8fafc; border-bottom: 5px solid #1e3a8a; transform: translateY(-3px); box-shadow: 0 8px 15px rgba(0,0,0,0.1); }
    .login-title { font-size: 24px; font-weight: bold; margin-bottom: 8px; }
    .login-sub { font-size: 15px; color: #64748b; }
    </style>
    """, unsafe_allow_html=True)

    # Date Logic for Jayantis/Festivals
    today = datetime.date.today()
    mm_dd = today.strftime("%m-%d")
    
    event_img = ""
    event_title = "Welcome to Advanced School Management System"
    
    if mm_dd == "10-02":
        event_img = "<img class='marquee-img' src='https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Mahatma-Gandhi%2C_studio%2C_1931.jpg/512px-Mahatma-Gandhi%2C_studio%2C_1931.jpg' alt='Gandhi Jayanti'>"
        event_title = "🙏 Happy Gandhi Jayanti 🙏"
    elif mm_dd == "08-15":
        event_img = "<img class='marquee-img' src='https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Flag_of_India.svg/512px-Flag_of_India.svg.png' alt='Independence Day'>"
        event_title = "🇮🇳 Happy Independence Day 🇮🇳"
    elif mm_dd == "01-26":
        event_img = "<img class='marquee-img' src='https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Flag_of_India.svg/512px-Flag_of_India.svg.png' alt='Republic Day'>"
        event_title = "🇮🇳 Happy Republic Day 🇮🇳"
    elif mm_dd == "09-05":
        event_img = "<img class='marquee-img' src='https://upload.wikimedia.org/wikipedia/commons/thumb/d/d1/Dr_Sarvepalli_Radhakrishnan.jpg/512px-Dr_Sarvepalli_Radhakrishnan.jpg' alt='Teachers Day'>"
        event_title = "📚 Happy Teachers' Day 📚"
    elif mm_dd == "01-23":
        event_img = "<img class='marquee-img' src='https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Subhas_Chandra_Bose_NRB.jpg/512px-Subhas_Chandra_Bose_NRB.jpg' alt='Netaji Jayanti'>"
        event_title = "🇮🇳 Happy Netaji Subhas Chandra Bose Jayanti 🇮🇳"

    # Dynamic Background Container with Sliding Photos
    st.markdown(f"""
    <div class="dynamic-bg-box">
        <h2 style='text-align: center; color: #1e3a8a; margin-top: 0;'>🏫 {event_title}</h2>
        <div class="carousel">
            <marquee behavior="scroll" direction="left" scrollamount="10" class="marquee-images" onmouseover="this.stop();" onmouseout="this.start();">
                {event_img}
                <img class="marquee-img" src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Raja_Ravi_Varma_-_Saraswati.jpg/512px-Raja_Ravi_Varma_-_Saraswati.jpg" alt="Saraswati Maa">
                <img class="marquee-img" src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Ganesha_Basohli_miniature_circa_1730_Dubost_p73.jpg/512px-Ganesha_Basohli_miniature_circa_1730_Dubost_p73.jpg" alt="Lord Ganesha">
                <img class="marquee-img" src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Jagannath.jpg/512px-Jagannath.jpg" alt="Lord Jagannath">
                <img class="marquee-img" src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e2/Droupadi_Murmu_Official_Portrait.jpg/512px-Droupadi_Murmu_Official_Portrait.jpg" alt="President of India">
                <img class="marquee-img" src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c0/Official_Photograph_of_Prime_Minister_Narendra_Modi_Portrait.png/512px-Official_Photograph_of_Prime_Minister_Narendra_Modi_Portrait.png" alt="PM of India">
            </marquee>
            <div class="carousel-overlay">Connecting Students, Teachers & Administration Seamlessly</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Running Long Notification
    notice_html = (
        "<div style='background-color: #1e293b; border-radius: 5px; margin-bottom: 25px; border: 1px solid #475569; overflow: hidden; color: #e2e8f0; font-size: 18px; padding: 12px;'>"
        "<marquee direction='left' scrollamount='8'>"
        "<span style='color: #fbbf24; font-weight: bold;'>📢 ନୂଆ ଅପଡେଟ୍: ଛାତ୍ରଛାତ୍ରୀମାନେ ଏବେ ଅନଲାଇନ୍ ରେଜିଷ୍ଟ୍ରେସନ୍ ଏବଂ ପେମେଣ୍ଟ କରିପାରିବେ! &nbsp;&nbsp;|&nbsp;&nbsp; 👨‍💻 Software Developed by: KULU SUTAR &nbsp;&nbsp;|&nbsp;&nbsp; 📞 Helpdesk No: 8910223342 &nbsp;&nbsp;|&nbsp;&nbsp; ✉️ Mail ID: kulusutar123@gmail.com &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 📢 उन्नत स्कूल प्रबंधन प्रणाली में आपका स्वागत है! नए अपडेट के लिए कृपया पोर्टल देखते रहें। &nbsp;&nbsp;|&nbsp;&nbsp; 👨‍💻 डेवलपर: कुलु सुतार &nbsp;&nbsp;|&nbsp;&nbsp; 📞 हेल्पडेस्क: 8910223342 &nbsp;&nbsp;|&nbsp;&nbsp; ✉️ ईमेल: kulusutar123@gmail.com </span>"
        "</marquee>"
        "</div>"
    )
    st.markdown(notice_html, unsafe_allow_html=True)

    # Prominent Action Buttons
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<a href='?portal=reg_school' target='_self' class='login-card'><div class='login-title'>🏫 New School Registration</div><div class='login-sub'>Register your institution</div></a>", unsafe_allow_html=True)
        st.markdown("<a href='?portal=master' target='_self' class='login-card'><div class='login-title'>🏛️ Master Login</div><div class='login-sub'>University / Admin Portal</div></a>", unsafe_allow_html=True)
    with c2:
        st.markdown("<a href='?portal=reg_student' target='_self' class='login-card'><div class='login-title'>👨‍🎓 New Student Registration</div><div class='login-sub'>Apply for admission/exams</div></a>", unsafe_allow_html=True)
        st.markdown("<a href='?portal=school' target='_self' class='login-card'><div class='login-title'>🏫 School Login</div><div class='login-sub'>School / College Portal</div></a>", unsafe_allow_html=True)
    with c3:
        st.markdown("<a href='?portal=student' target='_self' class='login-card' style='height: 94%; display: flex; flex-direction: column; justify-content: center;'><div class='login-title' style='font-size: 32px;'>🎓 Check Results</div><div class='login-sub'>Download Student Rank Card</div></a>", unsafe_allow_html=True)

# ----------------- NEW STUDENT REGISTRATION WITH DYNAMIC FEES & GST -----------------
elif menu == "New Student Registration":
    c_home, c_title = st.columns([1, 8])
    with c_home:
        if st.button("🏠 Home", key="reg_stu_home"):
            st.query_params["portal"] = "home"
            st.rerun()
    with c_title:
        st.subheader("👨‍🎓 New Student Registration & Payment Portal")

    base_fee = float(master_db.get("reg_fee", 150.0))
    gst_pct = float(master_db.get("gst_percent", 18.0))
    gst_amt = round(base_fee * (gst_pct / 100.0), 2)
    total_fee = round(base_fee + gst_amt, 2)

    if 'payment_step' not in st.session_state:
        st.session_state['payment_step'] = False
        st.session_state['temp_student_data'] = None
    if 'stu_reg_success' not in st.session_state:
        st.session_state['stu_reg_success'] = False

    if st.session_state['stu_reg_success']:
        st.success(f"✅ Application Submitted Successfully! Your Registration ID is **{st.session_state['stu_reg_id']}**.")
        st.info("Your application is now pending verification from the Admin/School. Please download your receipt below.")
        
        pdf_file = f"Receipt_{st.session_state['stu_reg_id']}.pdf"
        create_student_receipt_pdf(pdf_file, st.session_state['stu_reg_id'], st.session_state['stu_reg_data'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            with open(pdf_file, "rb") as f:
                st.download_button("📥 Download PDF Receipt", f, file_name=pdf_file, mime="application/pdf")
        with col2:
            if st.button("🖨️ Print Receipt"):
                components.html("<script>window.parent.print();</script>", height=0)
        with col3:
            if st.button("⬅️ Done / Go Back"):
                st.session_state['stu_reg_success'] = False
                st.session_state['stu_reg_id'] = None
                st.session_state['stu_reg_data'] = None
                st.rerun()
                
    elif not st.session_state['payment_step']:
        st.info("Fill your registration details carefully. Verify with the declaration checkbox to proceed to payment.")
        with st.form("student_reg_form"):
            st.markdown("#### 1. School Information")
            c_sc1, c_sc2 = st.columns(2)
            
            active_schools = {k: v for k, v in schools_db.items() if v.get("status", "Active") == "Active"}
            
            if not active_schools:
                st.error("No active schools available for registration.")
                school_sel = None
            else:
                school_options = [f"{k} - {v['name']}" for k, v in active_schools.items()]
                school_sel_str = c_sc1.selectbox("14. Select School Code & Name *", ["--Select--"] + school_options)
                school_sel = school_sel_str.split(" - ")[0] if school_sel_str != "--Select--" else None
                
            st.markdown("#### 2. Personal Details")
            c_n1, c_n2 = st.columns(2)
            stu_name_en = c_n1.text_input("1. Student's Name (English) *")
            stu_name_loc = c_n2.text_input("1. Student's Name (Local Language)")
            
            c_g1, c_g2, c_g3 = st.columns(3)
            stu_gender_en = c_g1.selectbox("2. Gender (English)", ["Male", "Female", "Other"])
            stu_gender_loc = c_g2.text_input("2. Gender (Local Language)")
            stu_category = c_g3.selectbox("Social Category *", SOCIAL_CATEGORIES)
            
            c_d1, c_d2 = st.columns(2)
            stu_dob = c_d1.date_input("3. Date of Birth *", min_value=datetime.date(2000, 1, 1), max_value=datetime.date.today())
            stu_state = c_d2.selectbox("4. State (All India)", list(STATE_LANG_MAP.keys()), index=18)
            
            c_m1, c_m2 = st.columns(2)
            m_name_en = c_m1.text_input("5. Mother's Name (English) *")
            m_name_loc = c_m2.text_input("5. Mother's Name (Local Language)")
            
            c_f1, c_f2 = st.columns(2)
            f_name_en = c_f1.text_input("6. Father's Name (English) *")
            f_name_loc = c_f2.text_input("6. Father's Name (Local Language)")
            
            st.markdown("#### 3. Contact & Identification")
            c_id1, c_id2 = st.columns(2)
            stu_aadhar = c_id1.text_input("7. AADHAAR Number of Student *", max_chars=12)
            stu_phone = c_id2.text_input("10. Mobile No *", max_chars=10)
            
            c_ad1, c_ad2 = st.columns(2)
            stu_address_en = c_ad1.text_area("8. Address (English) *")
            stu_address_loc = c_ad2.text_area("8. Address (Local Language)")
            
            c_loc1, c_loc2 = st.columns(2)
            stu_pin = c_loc1.text_input("9. PIN Code *", max_chars=6)
            stu_minority = c_loc2.selectbox("11. Minority Group", ["No", "Yes - Muslim", "Yes - Christian", "Yes - Sikh", "Yes - Buddhist", "Yes - Parsi", "Yes - Jain"])
            
            c_nat1, c_nat2 = st.columns(2)
            stu_country = c_nat1.selectbox("12. Whether the Student is Indian National?", COUNTRIES)
            stu_bg = c_nat2.selectbox("13. Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"])
            
            st.markdown("#### 4. Photograph Upload")
            stu_photo = st.file_uploader("16. Upload Student Photo (JPG/PNG)", type=['png', 'jpg', 'jpeg'])
            
            st.markdown("#### 5. Declaration")
            declaration = st.checkbox("✅ I hereby declare that all the information provided above is true and correct to the best of my knowledge.")
            
            submitted_stu = st.form_submit_button("Proceed to Payment & Submit")
            
            if submitted_stu:
                if not declaration:
                    st.error("⚠️ Please check the declaration box to confirm your details are correct.")
                elif not school_sel or not sanitize(stu_name_en) or not sanitize(f_name_en) or not sanitize(m_name_en) or not sanitize(stu_aadhar) or not sanitize(stu_phone) or not sanitize(stu_address_en) or not sanitize(stu_pin):
                    st.error("Please fill all the mandatory fields (*).")
                else:
                    temp_reg_id = "REG" + str(random.randint(100000, 999999))
                    has_photo = True if stu_photo else False
                    
                    st.session_state['temp_student_data'] = {
                        "reg_id": temp_reg_id,
                        "school_sel": school_sel,
                        "data": {
                            "name": sanitize(stu_name_en), 
                            "name_local": sanitize(stu_name_loc),
                            "gender": stu_gender_en, 
                            "gender_local": sanitize(stu_gender_loc),
                            "category": stu_category,
                            "father_name": sanitize(f_name_en), 
                            "father_name_local": sanitize(f_name_loc),
                            "mother_name": sanitize(m_name_en), 
                            "mother_name_local": sanitize(m_name_loc),
                            "dob": str(stu_dob), 
                            "blood_group": stu_bg,
                            "aadhaar": sanitize(stu_aadhar),
                            "phone": sanitize(stu_phone),
                            "address": sanitize(stu_address_en),
                            "address_local": sanitize(stu_address_loc),
                            "state": stu_state,
                            "pin_code": sanitize(stu_pin),
                            "nationality": stu_country,
                            "minority": stu_minority,
                            "has_photo": has_photo,
                            "school_code": school_sel,
                            "class": "1", 
                            "batch": "2025-2026",
                            "subjects": {},
                            "total_full": 0, "total_obt": 0, "percentage": 0.0,
                            "result": "N/A", "grade": "N/A", "pub_date": str(datetime.date.today()),
                            "pen_no": "", "apaar_no": "",
                            "payment_mode": "Pending",
                            "base_fee": base_fee,
                            "gst_amt": gst_amt,
                            "total_fee": total_fee,
                            "status": "Pending_Master"
                        }
                    }
                    st.session_state['payment_step'] = True
                    st.rerun()

    if st.session_state.get('payment_step', False):
        st.markdown("### 💳 Secure Payment Gateway")
        temp_obj = st.session_state.get('temp_student_data')
        if temp_obj:
            st.markdown(f"""
            <div style='background-color:#eff6ff; border:1px solid #bfdbfe; padding:15px; border-radius:8px; margin-bottom:15px;'>
                <b>Student Name:</b> {temp_obj['data']['name'].upper()}<br>
                <b>Registration Base Fee:</b> ₹{base_fee:.2f}<br>
                <b>GST ({gst_pct}%):</b> ₹{gst_amt:.2f}<br>
                <hr style='margin:8px 0;'>
                <b style='color:#1e3a8a; font-size:18px;'>Total Payable Amount: ₹{total_fee:.2f}</b>
            </div>
            """, unsafe_allow_html=True)
            
            pay_mode = st.radio("Select Payment Mode", ["Online Payment (UPI/QR)", "Offline Payment (School Counter)"])
            
            if pay_mode == "Online Payment (UPI/QR)":
                master_upi = master_db.get("upi_id", "school@sbi")
                upi_url = f"upi://pay?pa={master_upi}&pn=SchoolRegistration&am={total_fee:.2f}&cu=INR"
                qr_api = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={urllib.parse.quote(upi_url)}"
                
                col_qr, col_form = st.columns([1, 2])
                with col_qr:
                    st.markdown(f"<img src='{qr_api}' style='border:5px solid #1E3A8A; border-radius:10px;'>", unsafe_allow_html=True)
                    st.markdown(f"**UPI ID:** `{master_upi}`")
                    
                with col_form:
                    st.warning(f"Scan the QR code with PhonePe, GPay, or Paytm to pay ₹{total_fee:.2f}.")
                    txn_id = st.text_input("Enter 12-digit Transaction ID / UTR No. *")
                    if st.button("Verify & Submit Final Application", type="primary"):
                        if not txn_id or len(txn_id) < 8:
                            st.error("Please enter a valid Transaction ID to complete registration.")
                        else:
                            reg_data = st.session_state['temp_student_data']
                            reg_data['data']['payment_mode'] = f"Online (₹{total_fee:.2f} - Txn: {sanitize(txn_id)})"
                            reg_data['data']['status'] = "Pending_Master"
                            
                            sch_id = reg_data['school_sel']
                            if sch_id not in students_db:
                                students_db[sch_id] = {}
                            students_db[sch_id][reg_data['reg_id']] = reg_data['data']
                            save_data_json(schools_db, students_db)
                            
                            st.session_state['stu_reg_success'] = True
                            st.session_state['stu_reg_id'] = reg_data['reg_id']
                            st.session_state['stu_reg_data'] = reg_data['data']
                            st.session_state['payment_step'] = False
                            st.session_state['temp_student_data'] = None
                            st.rerun()

            elif pay_mode == "Offline Payment (School Counter)":
                st.info(f"You have selected Offline Payment. Please pay ₹{total_fee:.2f} (Fee: ₹{base_fee:.2f} + GST: ₹{gst_amt:.2f}) at your School Counter.")
                if st.button("Submit Final Application", type="primary"):
                    reg_data = st.session_state['temp_student_data']
                    reg_data['data']['payment_mode'] = f"Offline (₹{total_fee:.2f} - Pending at Counter)"
                    reg_data['data']['status'] = "Pending_Master"
                    
                    sch_id = reg_data['school_sel']
                    if sch_id not in students_db:
                        students_db[sch_id] = {}
                    students_db[sch_id][reg_data['reg_id']] = reg_data['data']
                    save_data_json(schools_db, students_db)
                    
                    st.session_state['stu_reg_success'] = True
                    st.session_state['stu_reg_id'] = reg_data['reg_id']
                    st.session_state['stu_reg_data'] = reg_data['data']
                    st.session_state['payment_step'] = False
                    st.session_state['temp_student_data'] = None
                    st.rerun()
                    
            if st.button("⬅️ Back to Form"):
                st.session_state['payment_step'] = False
                st.rerun()

# ----------------- NEW SCHOOL REGISTRATION WITH DYNAMIC FEES -----------------
elif menu == "New School Registration":
    st.query_params["portal"] = "reg_school"
    c_home, c_title = st.columns([1, 8])
    with c_home:
        if st.button("🏠 Home", key="reg_sch_home"):
            st.query_params["portal"] = "home"
            st.rerun()
    with c_title:
        st.subheader("📝 New School Registration & Payment")

    s_base_fee = float(master_db.get("school_reg_fee", 1000.0))
    s_gst_pct = float(master_db.get("school_gst_percent", 18.0))
    s_gst_amt = round(s_base_fee * (s_gst_pct / 100.0), 2)
    s_total_fee = round(s_base_fee + s_gst_amt, 2)

    if 'school_payment_step' not in st.session_state:
        st.session_state['school_payment_step'] = False
        st.session_state['temp_school_data'] = None
    if 'sch_reg_success' not in st.session_state:
        st.session_state['sch_reg_success'] = False

    if st.session_state['sch_reg_success']:
        st.success("✅ Registration Successful! Your account is PENDING approval from the Master Admin.")
        st.info("Please download your registration receipt below.")
        
        pdf_file = f"School_Receipt_{st.session_state['sch_reg_id']}.pdf"
        create_school_receipt_pdf(pdf_file, st.session_state['sch_reg_id'], st.session_state['sch_reg_data'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            with open(pdf_file, "rb") as f:
                st.download_button("📥 Download PDF Receipt", f, file_name=pdf_file, mime="application/pdf")
        with col2:
            if st.button("🖨️ Print Receipt"):
                components.html("<script>window.parent.print();</script>", height=0)
        with col3:
            if st.button("⬅️ Done / Go Back"):
                st.session_state['sch_reg_success'] = False
                st.session_state['sch_reg_id'] = None
                st.session_state['sch_reg_data'] = None
                st.rerun()

    elif not st.session_state['school_payment_step']:
        st.info("Submit your school details. Wait for the Master Admin to approve and ACTIVATE your account after payment.")
        
        with st.form("school_reg_form"):
            r_id = st.text_input("School ID (Create a Unique ID) *")
            
            c_n1, c_n2 = st.columns(2)
            r_name_en = c_n1.text_input("School Name (English) *")
            r_name_loc = c_n2.text_input("School Name (Local Language) [Optional]")
            
            indian_states = list(STATE_LANG_MAP.keys())
            r_state = st.selectbox("Select State", indian_states, index=18)
            
            c_a1, c_a2 = st.columns(2)
            r_address_en = c_a1.text_area("School Address (English)")
            r_address_loc = c_a2.text_area("School Address (Local Language) [Optional]")
            
            c_h1, c_h2 = st.columns(2)
            r_hm_name = c_h1.text_input("Head Master Name")
            r_hm_phone = c_h2.text_input("Head Master Mobile No.")
            
            c_p1, c_p2 = st.columns(2)
            r_pass = c_p1.text_input("New Password *", type="password")
            r_cpass = c_p2.text_input("Confirm Password *", type="password")
            
            st.markdown("#### 5. Declaration")
            s_declaration = st.checkbox("✅ I hereby declare that all the information provided above is true and correct.")
            
            submitted = st.form_submit_button("Proceed to Payment & Submit")
            if submitted:
                s_id_clean = sanitize(r_id)
                if not s_declaration:
                    st.error("⚠️ Please check the declaration box.")
                elif not s_id_clean or not sanitize(r_name_en) or not r_pass:
                    st.error("Please fill all the mandatory fields (*) including School ID, Name, and Password.")
                elif r_pass != r_cpass:
                    st.error("Passwords do not match!")
                elif s_id_clean in schools_db:
                    st.error("This School ID already exists. Please choose a different ID.")
                else:
                    st.session_state['temp_school_data'] = {
                        "school_id": s_id_clean,
                        "data": {
                            "name": sanitize(r_name_en), 
                            "name_local": sanitize(r_name_loc),
                            "address": sanitize(r_address_en),
                            "address_local": sanitize(r_address_loc),
                            "hm_name": sanitize(r_hm_name),
                            "hm_name_local": "",
                            "hm_phone": sanitize(r_hm_phone),
                            "hm_email": "",
                            "pass": r_pass, 
                            "state": r_state, 
                            "lang": STATE_LANG_MAP[r_state],
                            "status": "Pending_Master_Approval"
                        }
                    }
                    st.session_state['school_payment_step'] = True
                    st.rerun()

    if st.session_state.get('school_payment_step', False):
        st.markdown("### 💳 Secure Payment Gateway for School")
        s_temp_obj = st.session_state.get('temp_school_data')
        if s_temp_obj:
            st.markdown(f"""
            <div style='background-color:#eff6ff; border:1px solid #bfdbfe; padding:15px; border-radius:8px; margin-bottom:15px;'>
                <b>School Name:</b> {s_temp_obj['data']['name'].upper()}<br>
                <b>School Registration Base Fee:</b> ₹{s_base_fee:.2f}<br>
                <b>GST ({s_gst_pct}%):</b> ₹{s_gst_amt:.2f}<br>
                <hr style='margin:8px 0;'>
                <b style='color:#1e3a8a; font-size:18px;'>Total Payable Amount: ₹{s_total_fee:.2f}</b>
            </div>
            """, unsafe_allow_html=True)
            
            s_pay_mode = st.radio("Select Payment Mode", ["Online Payment (UPI/QR)", "Offline Payment (Direct)"])
            
            if s_pay_mode == "Online Payment (UPI/QR)":
                master_upi = master_db.get("upi_id", "school@sbi")
                upi_url = f"upi://pay?pa={master_upi}&pn=SchoolReg&am={s_total_fee:.2f}&cu=INR"
                qr_api = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={urllib.parse.quote(upi_url)}"
                
                col_qr, col_form = st.columns([1, 2])
                with col_qr:
                    st.markdown(f"<img src='{qr_api}' style='border:5px solid #1E3A8A; border-radius:10px;'>", unsafe_allow_html=True)
                    st.markdown(f"**UPI ID:** `{master_upi}`")
                    
                with col_form:
                    st.warning(f"Scan the QR code to pay ₹{s_total_fee:.2f}.")
                    txn_id = st.text_input("Enter 12-digit Transaction ID / UTR No. *")
                    if st.button("Verify & Submit School Registration", type="primary"):
                        if not txn_id or len(txn_id) < 8:
                            st.error("Please enter a valid Transaction ID.")
                        else:
                            reg_data = st.session_state['temp_school_data']
                            reg_data['data']['payment_mode'] = f"Online (₹{s_total_fee:.2f} - Txn: {sanitize(txn_id)})"
                            schools_db[reg_data["school_id"]] = reg_data["data"]
                            save_data_json(schools_db, students_db)
                            
                            st.session_state['sch_reg_success'] = True
                            st.session_state['sch_reg_id'] = reg_data['school_id']
                            st.session_state['sch_reg_data'] = reg_data['data']
                            st.session_state['school_payment_step'] = False
                            st.session_state['temp_school_data'] = None
                            st.rerun()

            elif s_pay_mode == "Offline Payment (Direct)":
                st.info(f"Offline Payment: Please pay ₹{s_total_fee:.2f} to the authorities.")
                if st.button("Submit School Registration", type="primary"):
                    reg_data = st.session_state['temp_school_data']
                    reg_data['data']['payment_mode'] = f"Offline (₹{s_total_fee:.2f} - Pending)"
                    schools_db[reg_data["school_id"]] = reg_data["data"]
                    save_data_json(schools_db, students_db)
                    
                    st.session_state['sch_reg_success'] = True
                    st.session_state['sch_reg_id'] = reg_data['school_id']
                    st.session_state['sch_reg_data'] = reg_data['data']
                    st.session_state['school_payment_step'] = False
                    st.session_state['temp_school_data'] = None
                    st.rerun()
                    
            if st.button("⬅️ Back to Form"):
                st.session_state['school_payment_step'] = False
                st.rerun()

# ----------------- MASTER LOGIN -----------------
elif menu == "Master Login":
    st.query_params["portal"] = "master"
    c_home, c_title = st.columns([1, 8])
    with c_home:
        if st.button("🏠 Home", key="m_home_btn"):
            st.query_params["portal"] = "home"
            st.rerun()
    with c_title:
        st.subheader("🔑 Master Administrator Portal")
    
    if not st.session_state.get('master_logged', False):
        login_mode = st.radio("Choose Action", ["Login", "Forgot Password"])
        
        if login_mode == "Login":
            m_user = st.text_input("Master Username")
            m_pass = st.text_input("Master Password", type="password")
            
            if st.button("Login"):
                if sanitize(m_user) == master_db.get("username") and m_pass == master_db.get("password"):
                    st.session_state['master_logged'] = True
                    st.rerun()
                else:
                    st.error("ଭୁଲ୍ Master ID କିମ୍ବା Password!")
                    
        elif login_mode == "Forgot Password":
            st.info("Recover your Master Account using Mobile or Email OTP")
            verify_contact = st.text_input("Enter Registered Mobile No or Email")
            
            if st.button("Send OTP"):
                if verify_contact == master_db.get("email") or verify_contact == master_db.get("phone"):
                    otp_code = str(random.randint(1000, 9999))
                    st.session_state['master_otp'] = otp_code
                    st.success("OTP Sent Successfully!")
                    st.info(f"📲 [DEMO SIMULATION] Your OTP is: **{otp_code}**")
                else:
                    st.error("Invalid Email or Mobile Number!")
                    
            if 'master_otp' in st.session_state:
                entered_otp = st.text_input("Enter 4-digit OTP")
                if st.button("Verify OTP"):
                    if entered_otp == st.session_state['master_otp']:
                        st.success("OTP Verified! You can now reset your Username and Password.")
                        st.session_state['otp_verified'] = True
                    else:
                        st.error("Invalid OTP!")
                        
            if st.session_state.get('otp_verified', False):
                st.markdown("### 🔄 Reset Master Credentials")
                new_m_user = st.text_input("New Master Username")
                new_m_pass = st.text_input("New Master Password", type="password")
                if st.button("Save New Credentials"):
                    if new_m_user and new_m_pass:
                        master_db["username"] = sanitize(new_m_user)
                        master_db["password"] = new_m_pass
                        save_master_data(master_db)
                        st.success("Master ID & Password successfully updated! Please go to 'Login'.")
                        del st.session_state['master_otp']
                        del st.session_state['otp_verified']
                    else:
                        st.warning("Please fill both fields.")

    else:
        col1, col2 = st.columns([8, 2])
        with col1:
            st.success("Welcome KULU SUTAR! ମାଷ୍ଟର୍ ସିଷ୍ଟମ୍ କୁ ସ୍ୱାଗତମ୍!")
        with col2:
            if st.button("🔴 Logout", key="m_logout"):
                st.session_state['master_logged'] = False
                st.rerun()

        st.markdown("---")
        tab1, tab_pay, tab2, tab3, tab4 = st.tabs([
            "👁️ Manage Schools", 
            "💳 Payment Approvals (School & Student)",
            "🎓 Edit Students Data", 
            "✏️ Edit Registered Schools", 
            "⚙️ Settings (ID/Pass & Fees)"
        ])
        
        with tab1:
            st.markdown("### 🏫 Active/Inactive Schools")
            if not schools_db:
                st.write("କୌଣସି ସ୍କୁଲ୍ ରେଜିଷ୍ଟର୍ ହୋଇନାହିଁ।")
            else:
                for s_id, s_info in list(schools_db.items()):
                    status = s_info.get("status", "Active") 
                    if status == "Pending_Master_Approval":
                        continue 
                        
                    bg = "#f0fdf4" if status == "Active" else "#fef2f2"

                    st.markdown(f"""
                    <div style="border:1px solid #cbd5e1; border-radius:5px; padding:10px; margin-bottom:10px; background-color:{bg};">
                        <b>School ID:</b> {s_id} | <b>Name:</b> {s_info['name']} | <b>State:</b> {s_info.get('state', 'N/A')}<br>
                        <b>HM Name:</b> {s_info.get('hm_name', 'N/A')} | <b>Phone:</b> {s_info.get('hm_phone', 'N/A')} | <b>Email:</b> {s_info.get('hm_email', 'N/A')}<br>
                        <b>Status:</b> <strong>{status}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    c_btn1, c_btn2, c_btn3 = st.columns(3)
                    if status == "Inactive":
                        if c_btn1.button("✅ Make Active", key=f"act_{s_id}"):
                            s_info["status"] = "Active"
                            save_data_json(schools_db, students_db)
                            st.success(f"School {s_id} is now Active!")
                            st.rerun()
                    if status == "Active":
                        if c_btn2.button("🚫 Make Inactive", key=f"deact_{s_id}"):
                            s_info["status"] = "Inactive"
                            save_data_json(schools_db, students_db)
                            st.warning(f"School {s_id} is now Inactive!")
                            st.rerun()
                            
                    if c_btn3.button("🗑️ Delete School", key=f"del_{s_id}"):
                        del schools_db[s_id]
                        if s_id in students_db:
                            del students_db[s_id]
                        save_data_json(schools_db, students_db)
                        st.error(f"School '{s_id}' deleted!")
                        st.rerun()

        with tab_pay:
            st.markdown("### 💳 Verify New School Registrations")
            pending_schools = {k: v for k, v in schools_db.items() if v.get("status") == "Pending_Master_Approval"}
            if pending_schools:
                for s_id, s_info in pending_schools.items():
                    st.markdown(f"""
                    <div style="border:1px solid #cbd5e1; border-radius:5px; padding:10px; margin-bottom:10px; background-color:#fffbeb;">
                        <b>School ID:</b> {s_id} | <b>Name:</b> {s_info['name']}<br>
                        <b style="color:green;">Payment Mode/UTR:</b> {s_info.get('payment_mode', 'N/A')}
                    </div>
                    """, unsafe_allow_html=True)
                    cp1, cp2 = st.columns(2)
                    with cp1:
                        if st.button(f"✅ Approve Payment & Activate", key=f"vps_{s_id}"):
                            s_info["status"] = "Active"
                            save_data_json(schools_db, students_db)
                            st.success(f"School {s_id} Activated!")
                            st.rerun()
                    with cp2:
                        if st.button(f"🚫 Reject (Auto Refund)", key=f"rps_{s_id}"):
                            del schools_db[s_id]
                            save_data_json(schools_db, students_db)
                            st.error(f"School {s_id} Rejected & Refund Initiated.")
                            st.rerun()
            else:
                st.success("No pending School Registrations.")
                
            st.markdown("---")
            st.markdown("### 💳 Verify Student Payments (Master Access)")
            st.info("Approve payments here. Once verified, the application will be sent to the respective school for final admission approval.")
            
            pending_master = []
            for s_id, s_studs in students_db.items():
                for r_no, s_data in s_studs.items():
                    if s_data.get("status") == "Pending_Master":
                        pending_master.append((s_id, r_no, s_data))
                        
            if pending_master:
                for s_id, r_no, p_st in pending_master:
                    st.markdown(f"""
                    <div style="border:1px solid #cbd5e1; border-radius:5px; padding:10px; margin-bottom:10px; background-color:#fffbeb;">
                        <b>Reg ID:</b> {r_no} | <b>School Code:</b> {s_id} | <b>Name:</b> {p_st.get('name', '').upper()}<br>
                        <b>Amount Paid:</b> ₹{p_st.get('total_fee', 0)}<br>
                        <b style="color:green;">Payment Mode/UTR:</b> {p_st.get('payment_mode', 'N/A')}
                    </div>
                    """, unsafe_allow_html=True)
                    c_pay1, c_pay2 = st.columns(2)
                    with c_pay1:
                        if st.button(f"✅ Verify Payment & Send to School", key=f"vp_{r_no}"):
                            p_st["status"] = "Pending_School"
                            save_data_json(schools_db, students_db)
                            st.success(f"Payment for {r_no} verified! Application sent to School.")
                            st.rerun()
                    with c_pay2:
                        if st.button(f"🚫 Reject (Auto Refund)", key=f"rp_{r_no}"):
                            p_st['payment_mode'] = p_st.get('payment_mode', '') + " - [REFUND INITIATED]"
                            p_st['status'] = "Rejected_Refund"
                            save_data_json(schools_db, students_db)
                            st.error(f"Payment rejected and Refund initiated for {r_no}.")
                            st.rerun()
            else:
                st.success("No pending student payments to verify.")

        with tab2:
            st.markdown("### 📋 Manage All Students (Master Access)")
            master_school_sel = st.selectbox("Select School", ["--Select--"] + list(schools_db.keys()))
            if master_school_sel != "--Select--":
                school_students = students_db.get(master_school_sel, {})
                s_lang = schools_db[master_school_sel].get("lang", "English")
                
                approved_students = {k:v for k,v in school_students.items() if v.get('status', 'Approved') == 'Approved'}
                
                if approved_students:
                    m_edit_roll = st.selectbox("Select Student Roll No to Edit/Delete", list(approved_students.keys()))
                    m_curr_st = approved_students[m_edit_roll]
                    
                    st.markdown("#### Edit Student Details")
                    
                    cn1, cn2 = st.columns(2)
                    m_up_name = cn1.text_input("Student Name (English)", value=m_curr_st.get('name',''), key="m_up_n")
                    m_up_name_loc = cn2.text_input(f"Student Name ({s_lang})", value=m_curr_st.get('name_local', ''), key="m_up_n_loc")
                    
                    cf1, cf2 = st.columns(2)
                    m_up_father = cf1.text_input("Father's Name (English)", value=m_curr_st.get('father_name', ''), key="m_up_f")
                    m_up_father_loc = cf2.text_input(f"Father's Name ({s_lang})", value=m_curr_st.get('father_name_local', ''), key="m_up_f_loc")
                    
                    cm1, cm2 = st.columns(2)
                    m_up_mother = cm1.text_input("Mother's Name (English)", value=m_curr_st.get('mother_name', ''), key="m_up_m")
                    m_up_mother_loc = cm2.text_input(f"Mother's Name ({s_lang})", value=m_curr_st.get('mother_name_local', ''), key="m_up_m_loc")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        genders = ["Male", "Female", "Other"]
                        g_val = m_curr_st.get('gender', 'Male')
                        m_up_gender = st.selectbox("Gender", genders, index=genders.index(g_val) if g_val in genders else 0, key="m_up_gen")
                        m_up_pen = st.text_input("PEN NO", value=m_curr_st.get('pen_no', ''), key="m_up_pen")
                        cls_val = m_curr_st.get('class', '1')
                        m_up_cls = st.selectbox("Class", classes_list, index=classes_list.index(cls_val) if cls_val in classes_list else 0, key="m_up_c")
                        
                    with c2:
                        db_dob_val = m_curr_st.get('dob', '')
                        disp_edit_dob = db_dob_val
                        if db_dob_val.count('-') == 2:
                            parts = db_dob_val.split('-')
                            if len(parts[0]) == 4:
                                disp_edit_dob = f"{parts[2]}-{parts[1]}-{parts[0]}"
                        
                        m_up_dob_input = st.text_input("DOB (DD-MM-YYYY)", value=disp_edit_dob, key="m_up_d")
                        m_up_apaar = st.text_input("APAAR NO", value=m_curr_st.get('apaar_no', ''), key="m_up_apaar")
                        b_val = m_curr_st.get('batch', '2025-2026')
                        b_idx = batches_list.index(b_val) if b_val in batches_list else 5
                        m_up_batch = st.selectbox("Batch", batches_list, index=b_idx, key="m_up_batch")
                        
                        prev_pub_str = m_curr_st.get('pub_date', str(datetime.date.today()))
                        try:
                            p_y, p_m, p_d = prev_pub_str.split('-')
                            d_val = datetime.date(int(p_y), int(p_m), int(p_d))
                        except:
                            d_val = datetime.date.today()
                        m_up_pub_date = st.date_input("Publication Date", value=d_val, key="m_up_pub_date")
                    
                    st.markdown("#### 📚 Edit Subjects & Marks")
                    m_subjects = m_curr_st.get('subjects', {})
                    new_m_subjects = {}
                    m_tot_full = 0
                    m_tot_obt = 0
                    
                    if m_subjects:
                        for sub_name, sub_info in m_subjects.items():
                            sc1, sc2, sc3 = st.columns(3)
                            with sc1:
                                u_sub = st.text_input("Subject Name", value=sub_name, key=f"m_sub_{sub_name}")
                            with sc2:
                                u_f = st.number_input("Full Mark", value=float(sub_info['full']), key=f"m_f_{sub_name}")
                            with sc3:
                                u_o = st.number_input("Obtained Mark", value=float(sub_info['obt']), key=f"m_o_{sub_name}")
                            if u_sub:
                                new_m_subjects[sanitize(u_sub)] = {"full": u_f, "obt": u_o}
                                m_tot_full += u_f
                                m_tot_obt += u_o
                    else:
                        st.info("No detailed subjects found. Using only total marks.")
                        m_tot_full = float(m_curr_st.get('total_full', 300))
                        m_tot_obt = float(m_curr_st.get('total_obt', 0))

                    st.info(f"📊 **Auto Summary:** Total Marks: {m_tot_obt}/{m_tot_full}")
                    
                    col_sv, col_dl = st.columns(2)
                    with col_sv:
                        if st.button("💾 Force Update Record"):
                            m_up_dob_save = sanitize(m_up_dob_input)
                            if m_up_dob_input.count('-') == 2:
                                parts = m_up_dob_input.split('-')
                                if len(parts[2]) == 4:
                                    m_up_dob_save = f"{parts[2]}-{parts[1]}-{parts[0]}"
                                    
                            new_per = (m_tot_obt / m_tot_full * 100) if m_tot_full > 0 else 0.0
                            new_res = "PASS" if new_per >= 33 else "FAIL"
                            new_grd = "A1" if new_per >= 90 else "A2" if new_per >= 80 else "B1" if new_per >= 70 else "B2" if new_per >= 60 else "C1" if new_per >= 50 else "C2" if new_per >= 40 else "D" if new_per >= 33 else "F"
                            
                            students_db[master_school_sel][m_edit_roll].update({
                                "name": sanitize(m_up_name), "name_local": sanitize(m_up_name_loc),
                                "gender": m_up_gender, "pen_no": sanitize(m_up_pen), "apaar_no": sanitize(m_up_apaar),
                                "father_name": sanitize(m_up_father), "father_name_local": sanitize(m_up_father_loc),
                                "mother_name": sanitize(m_up_mother), "mother_name_local": sanitize(m_up_mother_loc),
                                "dob": m_up_dob_save, "class": m_up_cls, "batch": m_up_batch, "pub_date": str(m_up_pub_date),
                                "subjects": new_m_subjects if new_m_subjects else m_subjects,
                                "total_obt": m_tot_obt, "total_full": m_tot_full, 
                                "percentage": round(new_per, 2), "result": new_res, "grade": new_grd
                            })
                            save_data_json(schools_db, students_db)
                            st.success(f"Roll No {m_edit_roll} data updated successfully!")
                            
                    with col_dl:
                        if st.button("🗑️ Delete Student (Master Only)", type="primary"):
                            del students_db[master_school_sel][m_edit_roll]
                            save_data_json(schools_db, students_db)
                            st.success("Student deleted successfully!")
                            st.rerun()
                else:
                    st.warning("No Approved students in this school.")

        with tab3:
            st.markdown("### ✏️ Edit Registered Schools")
            if schools_db:
                selected_edit_school = st.selectbox("Select School ID to Edit", list(schools_db.keys()))
                curr_s_data = schools_db[selected_edit_school]
                
                st.markdown("#### School Details")
                c_se1, c_se2 = st.columns(2)
                edit_s_name = c_se1.text_input("Edit School Name (English)", value=curr_s_data.get('name', ''))
                edit_s_name_loc = c_se2.text_input("Edit School Name (Local Language)", value=curr_s_data.get('name_local', ''))
                
                indian_states = list(STATE_LANG_MAP.keys())
                curr_state = curr_s_data.get('state', 'Odisha')
                state_idx = indian_states.index(curr_state) if curr_state in indian_states else 18
                edit_s_state = st.selectbox("Edit School State", indian_states, index=state_idx)
                
                st.markdown("#### Head Master Details")
                c_hm1, c_hm2 = st.columns(2)
                edit_hm_name = c_hm1.text_input("Edit HM Name (English)", value=curr_s_data.get('hm_name', ''))
                edit_hm_name_loc = c_hm2.text_input("Edit HM Name (Local Language)", value=curr_s_data.get('hm_name_local', ''))
                
                c_c1, c_c2 = st.columns(2)
                edit_hm_phone = c_c1.text_input("Edit HM Mobile No.", value=curr_s_data.get('hm_phone', ''))
                edit_hm_email = c_c2.text_input("Edit HM Email ID", value=curr_s_data.get('hm_email', ''))
                
                edit_s_pass = st.text_input("Edit School Password (Leave blank to keep current)", type="password")
                
                if st.button("Update School Profile"):
                    if edit_s_name:
                        curr_s_data.update({
                            "name": sanitize(edit_s_name),
                            "name_local": sanitize(edit_s_name_loc),
                            "hm_name": sanitize(edit_hm_name),
                            "hm_name_local": sanitize(edit_hm_name_loc),
                            "hm_phone": sanitize(edit_hm_phone),
                            "hm_email": sanitize(edit_hm_email),
                            "state": edit_s_state,
                            "lang": STATE_LANG_MAP[edit_s_state]
                        })
                        if edit_s_pass:
                            curr_s_data["pass"] = edit_s_pass
                            
                        save_data_json(schools_db, students_db)
                        st.success(f"School Profile Updated! The portal language is now set to {STATE_LANG_MAP[edit_s_state]}.")
                    else:
                        st.warning("Please fill all the mandatory details.")
            else:
                st.warning("No schools registered yet.")

        with tab4:
            st.markdown("### ⚙️ Update Master Profile, Payment, GST & Registration Fees")
            up_m_user = st.text_input("Master Username", value=master_db.get("username", ""))
            up_m_pass = st.text_input("New Master Password", type="password")
            up_m_email = st.text_input("Recovery Email (For OTP)", value=master_db.get("email", ""))
            up_m_phone = st.text_input("Recovery Phone Number (For OTP)", value=master_db.get("phone", ""))
            
            st.markdown("#### 💳 Fee Configuration & Online Payment UPI")
            up_m_upi = st.text_input("Online Payment UPI ID (e.g. school@sbi)", value=master_db.get("upi_id", "school@sbi"))
            
            c_f1, c_f2 = st.columns(2)
            up_base_fee = c_f1.number_input("Student Registration Base Fee (₹)", value=float(master_db.get("reg_fee", 150.0)), min_value=0.0, step=10.0)
            up_gst_pct = c_f2.number_input("Student GST Percentage (%)", value=float(master_db.get("gst_percent", 18.0)), min_value=0.0, max_value=100.0, step=1.0)
            
            c_s1, c_s2 = st.columns(2)
            up_sch_fee = c_s1.number_input("School Registration Base Fee (₹)", value=float(master_db.get("school_reg_fee", 1000.0)), min_value=0.0, step=100.0)
            up_sch_gst = c_s2.number_input("School GST Percentage (%)", value=float(master_db.get("school_gst_percent", 18.0)), min_value=0.0, max_value=100.0, step=1.0)
            
            if st.button("Save Profile & Fee Settings"):
                master_db["username"] = sanitize(up_m_user)
                master_db["email"] = sanitize(up_m_email)
                master_db["phone"] = sanitize(up_m_phone)
                master_db["upi_id"] = sanitize(up_m_upi)
                master_db["reg_fee"] = float(up_base_fee)
                master_db["gst_percent"] = float(up_gst_pct)
                master_db["school_reg_fee"] = float(up_sch_fee)
                master_db["school_gst_percent"] = float(up_sch_gst)
                if up_m_pass:
                    master_db["password"] = up_m_pass
                save_master_data_json(master_db)
                st.success("Master profile, UPI ID, Fees & GST Settings successfully updated!")

# ----------------- SCHOOL LOGIN -----------------
elif menu == "School Login":
    st.query_params["portal"] = "school"
    c_home, c_title = st.columns([1, 8])
    with c_home:
        if st.button("🏠 Home", key="s_home_btn"):
            st.query_params["portal"] = "home"
            st.rerun()
    with c_title:
        st.subheader("🏫 School Portal")
    
    if 'school_logged_id' not in st.session_state:
        st.info("🔗 ଉପରେ ବ୍ରାଉଜର୍‌ରେ ଥିବା ଲିଙ୍କ୍ କୁ କପି କରି ଅନ୍ୟମାନଙ୍କୁ ସ୍କୁଲ୍ ଲଗ୍ଇନ୍ ପାଇଁ ପଠାଇ ପାରିବେ।")
        
        s_id = st.text_input("School ID")
        s_pass = st.text_input("School Password", type="password")
        
        if 'school_captcha' not in st.session_state:
            st.session_state['school_captcha'] = str(random.randint(10000, 99999))
            
        c_cap1, c_cap2 = st.columns([3, 7])
        with c_cap1:
            st.markdown(
                f"<div style='margin-top:10px; margin-bottom:10px;'>"
                f"<b>CAPTCHA:</b> <br>"
                f"<span style='background-color: #f1f5f9; color:#0f172a; "
                f"padding: 5px 20px; font-size: 22px; font-weight: bold; "
                f"letter-spacing: 6px; border: 1px solid #cbd5e1; "
                f"border-radius: 5px; display:inline-block; margin-top:5px;'>"
                f"{st.session_state['school_captcha']}</span></div>", 
                unsafe_allow_html=True
            )
        with c_cap2:
            st.write("<br>", unsafe_allow_html=True)
            if st.button("🔄 Refresh CAPTCHA"):
                st.session_state['school_captcha'] = str(random.randint(10000, 99999))
                st.rerun()
                
        entered_captcha = st.text_input("Enter the CAPTCHA code shown above")
        
        if st.button("Login as School"):
            if entered_captcha != st.session_state['school_captcha']:
                st.error("❌ ଭୁଲ୍ CAPTCHA! ଦୟାକରି ସଠିକ୍ କ୍ୟାପ୍ଚା କୋଡ୍ ଦିଅନ୍ତୁ।")
                st.session_state['school_captcha'] = str(random.randint(10000, 99999))
                st.rerun()
            else:
                s_id_clean = sanitize(s_id)
                if s_id_clean in schools_db and schools_db[s_id_clean]["pass"] == s_pass:
                    sch_status = schools_db[s_id_clean].get("status", "Active")
                    if sch_status == "Active":
                        st.session_state['school_logged_id'] = s_id_clean
                        del st.session_state['school_captcha']
                        st.rerun()
                    elif sch_status == "Pending_Master_Approval":
                        st.error("⏳ ଆପଣଙ୍କ ସ୍କୁଲ୍ ପେମେଣ୍ଟ୍ ବର୍ତ୍ତମାନ ପେଣ୍ଡିଂ (Pending) ଅଛି। ମାଷ୍ଟର୍ ଙ୍କ ଅନୁମୋଦନ ପରେ ଆପଣ ଲଗ୍ଇନ୍ କରିପାରିବେ।")
                    elif sch_status == "Inactive":
                        st.error("🚫 ଆପଣଙ୍କ ସ୍କୁଲ୍ ଆକାଉଣ୍ଟ୍ କୁ ବର୍ତ୍ତମାନ ବନ୍ଦ (Inactive) କରାଯାଇଛି। ଦୟାକରି ମାଷ୍ଟର୍ ଙ୍କ ସହ ଯୋଗାଯୋଗ କରନ୍ତୁ।")
                else:
                    st.error("❌ ଭୁଲ୍ School ID କିମ୍ବା Password!")
                    st.session_state['school_captcha'] = str(random.randint(10000, 99999))
                    st.rerun()
                
    else: 
        cur_school = st.session_state['school_logged_id']
        sch_data = schools_db[cur_school]
        s_lang = sch_data.get("lang", "English")
        s_state = sch_data.get("state", "Unknown State")
        
        col1, col2 = st.columns([8, 2])
        with col1:
            st.info(f"🏫 **{t('School Portal', s_lang)} | School Portal** | ID: {cur_school} | {sch_data['name']} ({s_state})")
        with col2:
            if st.button(f"🔴 {t('Logout', s_lang)} | Logout", key="s_logout"):
                del st.session_state['school_logged_id']
                st.rerun()

        st.markdown("---")
        
        tab_list, tab_approve, tab_add, tab_edit, tab_report = st.tabs([
            f"📋 {t('My Students', s_lang)} | My Students", 
            "✅ Manage Registrations (Approvals)",
            f"➕ {t('Add Student', s_lang)} | Add Student", 
            f"✏️ {t('Edit Student', s_lang)} | Edit Student", 
            f"🖨️ {t('Report Card', s_lang)} | Report Card"
        ])
        
        cur_students = students_db.get(cur_school, {})
        approved_students = {k:v for k,v in cur_students.items() if v.get('status', 'Approved') == 'Approved'}
        pending_students = {k:v for k,v in cur_students.items() if v.get('status') == 'Pending_School'}
        
        with tab_list:
            st.markdown(f"### 📋 {t('My Students', s_lang)} | My Students")
            if approved_students:
                st.write(f"{t('Total Registered', s_lang)} **{len(approved_students)}**")
                search_query = st.text_input(f"🔍 {t('Search', s_lang)} / Search")
                for r_no, s_info in approved_students.items():
                    if search_query.lower() in r_no.lower() or search_query.lower() in s_info['name'].lower() or search_query == "":
                        cols = st.columns([2, 4, 3, 3])
                        cols[0].write(f"**Roll:** {r_no}")
                        cols[1].write(f"**Name:** {s_info['name']}")
                        b_val = s_info.get('batch', 'N/A')
                        cols[2].write(f"**Batch:** {b_val}")
                        cols[3].write(f"**Class:** {s_info.get('class', 'N/A')}")
            else:
                st.warning("No approved students registered in your school yet.")
                
        with tab_approve:
            st.markdown("### ✅ Review Online Student Registrations")
            st.info("Students whose payments are verified by Master Admin will appear here. Verify their details/marks, and Approve.")
            
            if pending_students:
                app_roll = st.selectbox("Select Pending Student Application", list(pending_students.keys()))
                p_st = pending_students[app_roll]
                
                pay_status = p_st.get("payment_mode", "N/A")
                st.success(f"💳 **Payment Status (Master Verified):** {pay_status}")
                
                new_roll_assign = st.text_input("Assign Actual Roll No (IMPORTANT) *", value=app_roll, key="p_new_roll")
                
                st.markdown("#### Review & Complete Details")
                c_up_n1, c_up_n2 = st.columns(2)
                p_name = c_up_n1.text_input("Name (English)", value=p_st.get('name', ''), key="p_name")
                p_name_loc = c_up_n2.text_input(f"Name ({s_lang})", value=p_st.get('name_local', ''), key="p_name_loc")
                
                c_f1, c_f2 = st.columns(2)
                p_father = c_f1.text_input("Father's Name (English)", value=p_st.get('father_name', ''), key="p_f_n")
                p_father_loc = c_f2.text_input(f"Father's Name ({s_lang})", value=p_st.get('father_name_local', ''), key="p_f_n_l")
                
                c_m1, c_m2 = st.columns(2)
                p_mother = c_m1.text_input("Mother's Name (English)", value=p_st.get('mother_name', ''), key="p_m_n")
                p_mother_loc = c_m2.text_input(f"Mother's Name ({s_lang})", value=p_st.get('mother_name_local', ''), key="p_m_n_l")
                
                c_up1, c_up2, c_up3 = st.columns(3)
                with c_up1:
                    gen_list = ["Male", "Female", "Other"]
                    p_gen_val = p_st.get('gender', 'Male')
                    p_gender = st.selectbox("Gender", gen_list, index=gen_list.index(p_gen_val) if p_gen_val in gen_list else 0)
                with c_up2:
                    p_pen = st.text_input("PEN NO", value=p_st.get('pen_no', ''))
                with c_up3:
                    p_apaar = st.text_input("APAAR NO", value=p_st.get('apaar_no', ''))

                db_dob_val = p_st.get('dob', '')
                disp_edit_dob = db_dob_val
                if db_dob_val.count('-') == 2:
                    parts = db_dob_val.split('-')
                    if len(parts[0]) == 4:
                        disp_edit_dob = f"{parts[2]}-{parts[1]}-{parts[0]}"
                        
                p_dob_input = st.text_input("DOB (DD-MM-YYYY)", value=disp_edit_dob, key="p_dob")
                
                c_e1, c_e2 = st.columns(2)
                with c_e1:
                    cls_val = p_st.get('class', '1')
                    p_cls = st.selectbox("Class", classes_list, index=classes_list.index(cls_val) if cls_val in classes_list else 0, key="p_cls")
                with c_e2:
                    b_val = p_st.get('batch', '2025-2026')
                    b_idx = batches_list.index(b_val) if b_val in batches_list else 5
                    p_batch = st.selectbox("Batch", batches_list, index=b_idx, key="p_batch")
                
                st.markdown("#### 📚 Enter Subjects & Marks")
                if 'p_sub_count' not in st.session_state: st.session_state.p_sub_count = 3
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("➕ Add Subject", key="add_sub_p"): st.session_state.p_sub_count += 1
                with col2:
                    if st.button("➖ Remove Subject", key="rem_sub_p") and st.session_state.p_sub_count > 1: st.session_state.p_sub_count -= 1
                
                p_subjects_data = {}
                p_tf, p_to = 0, 0
                
                for i in range(st.session_state.p_sub_count):
                    c1, c2, c3 = st.columns(3)
                    with c1: s_name = st.text_input(f"Subject {i+1}", key=f"p_sn_{i}")
                    with c2: f_m = st.number_input(f"FM {i+1}", value=100.0, key=f"p_fm_{i}")
                    with c3: o_m = st.number_input(f"OM {i+1}", value=0.0, key=f"p_om_{i}")
                    if s_name:
                        p_subjects_data[sanitize(s_name)] = {"full": f_m, "obt": o_m}
                        p_tf += f_m
                        p_to += o_m

                p_per = (p_to / p_tf * 100) if p_tf > 0 else 0.0
                p_res = "PASS" if p_per >= 33 else "FAIL"
                p_grd = "A1" if p_per >= 90 else "A2" if p_per >= 80 else "B1" if p_per >= 70 else "B2" if p_per >= 60 else "C1" if p_per >= 50 else "C2" if p_per >= 40 else "D" if p_per >= 33 else "F"
                
                st.info(f"📊 **Marks Entered:** {p_to}/{p_tf} | Percentage: {p_per:.2f}% | Grade: {p_grd}")
                
                c_act1, c_act2 = st.columns(2)
                with c_act1:
                    if st.button("✅ Approve Student & Save Marks", type="primary"):
                        p_dob_save = sanitize(p_dob_input)
                        if p_dob_input.count('-') == 2:
                            parts = p_dob_input.split('-')
                            if len(parts[2]) == 4: p_dob_save = f"{parts[2]}-{parts[1]}-{parts[0]}"
                        
                        updated_p_data = p_st.copy()
                        updated_p_data.update({
                            "name": sanitize(p_name), "name_local": sanitize(p_name_loc), 
                            "gender": p_gender, "pen_no": sanitize(p_pen), "apaar_no": sanitize(p_apaar),
                            "father_name": sanitize(p_father), "father_name_local": sanitize(p_father_loc),
                            "mother_name": sanitize(p_mother), "mother_name_local": sanitize(p_mother_loc),
                            "dob": p_dob_save, "class": p_cls, "batch": p_batch,
                            "subjects": p_subjects_data, "total_full": p_tf, "total_obt": p_to,
                            "percentage": round(p_per, 2), "result": p_res, "grade": p_grd,
                            "status": "Approved", "pub_date": str(datetime.date.today())
                        })
                        
                        roll_to_save = sanitize(new_roll_assign)
                        if roll_to_save != app_roll:
                            del students_db[cur_school][app_roll]
                            
                        students_db[cur_school][roll_to_save] = updated_p_data
                        save_data_json(schools_db, students_db)
                        st.success(f"Student {roll_to_save} Approved successfully!")
                        st.rerun()
                with c_act2:
                    if st.button("🚫 Reject (Auto Refund Initiated)"):
                        p_st['payment_mode'] = p_st.get('payment_mode', '') + " - [REFUND INITIATED]"
                        p_st['status'] = "Rejected_Refund"
                        students_db[cur_school][app_roll] = p_st
                        save_data_json(schools_db, students_db)
                        st.error(f"Application for {app_roll} Rejected. Payment Refund Process Automatically Initiated.")
                        st.rerun()
            else:
                st.success("No pending applications at the moment.")
                
        with tab_add:
            st.markdown(f"### 📝 {t('Add Student', s_lang)} | Add Student Direct (Pre-Approved)")
            
            c_roll, c_gen = st.columns(2)
            roll_no = c_roll.text_input(f"Roll No / {t('ROLL NO', s_lang)}", key="add_roll")
            gender = c_gen.selectbox("Gender", ["Male", "Female", "Other"], key="add_gen")
            
            st.markdown("---")
            c_n1, c_n2 = st.columns(2)
            st_name = c_n1.text_input(f"Student Name (English)", key="add_name")
            st_name_loc = c_n2.text_input(f"Student Name ({s_lang}) [Optional]", key="add_name_loc")
            
            father_name = c_n1.text_input(f"Father's Name (English)", key="add_father")
            father_name_loc = c_n2.text_input(f"Father's Name ({s_lang}) [Optional]", key="add_father_loc")
            
            mother_name = c_n1.text_input(f"Mother's Name (English)", key="add_mother")
            mother_name_loc = c_n2.text_input(f"Mother's Name ({s_lang}) [Optional]", key="add_mother_loc")
            st.markdown("---")
            
            c_p1, c_p2 = st.columns(2)
            pen_no = c_p1.text_input(f"PEN NO / {t('PEN NO', s_lang)}", key="add_pen")
            apaar_no = c_p2.text_input(f"APAAR NO / {t('APAAR NO', s_lang)}", key="add_apaar")
            
            min_date = datetime.date(2000, 1, 1)
            max_date = datetime.date(2065, 12, 31)
            dob = st.date_input(f"DOB (YYYY-MM-DD) / {t('DOB', s_lang)}", min_value=min_date, max_value=max_date, key="add_dob")
            
            c_c1, c_c2 = st.columns(2)
            with c_c1:
                cls = st.selectbox(f"Class / {t('CLASS', s_lang)}", classes_list, key="add_class")
            with c_c2:
                add_batch = st.selectbox("Batch", batches_list, index=5, key="add_batch")
            
            opt_pub_date = st.date_input(
                f"Results Publication Date (Optional / {t('DATE OF PUBLICATION', s_lang)})", 
                value=datetime.date.today(),
                key="add_pub_date"
            )
            
            st.markdown("#### 📚 Subject Add / Remove & Marks")
            if 'num_subjects' not in st.session_state:
                st.session_state.num_subjects = 3
                
            col1, col2 = st.columns(2)
            with col1:
                if st.button("➕ Add Subject"):
                    st.session_state.num_subjects += 1
            with col2:
                if st.button("➖ Remove Subject") and st.session_state.num_subjects > 1:
                    st.session_state.num_subjects -= 1
                    
            subjects_data = {}
            total_full_mark = 0
            total_obt_mark = 0
            
            for i in range(st.session_state.num_subjects):
                c1, c2, c3 = st.columns(3)
                with c1:
                    s_name = st.text_input(f"Subject {i+1} Name", value=f"Subject {i+1}", key=f"s_name_{i}")
                with c2:
                    f_mark = st.number_input("Full Mark", value=100.0, key=f"f_mark_{i}")
                with c3:
                    o_mark = st.number_input("Obtained Mark", value=0.0, key=f"o_mark_{i}")
                
                if s_name:
                    subjects_data[sanitize(s_name)] = {"full": f_mark, "obt": o_mark}
                    total_full_mark += f_mark
                    total_obt_mark += o_mark

            percentage = (total_obt_mark / total_full_mark * 100) if total_full_mark > 0 else 0.0
            result = "PASS" if percentage >= 33 else "FAIL"
            grade = "A1" if percentage >= 90 else "A2" if percentage >= 80 else "B1" if percentage >= 70 else "B2" if percentage >= 60 else "C1" if percentage >= 50 else "C2" if percentage >= 40 else "D" if percentage >= 33 else "F"
            
            st.info(f"📊 **Auto Summary:** Total Marks: {total_obt_mark}/{total_full_mark} | Percentage: {percentage:.2f}% | Result: **{result}** | Grade: **{grade}**")
            
            c_save, c_clear = st.columns(2)
            with c_save:
                if st.button("💾 Save Student Data"):
                    if roll_no and st_name:
                        roll_no_clean = sanitize(roll_no)
                        new_data = {
                            "name": sanitize(st_name), "name_local": sanitize(st_name_loc),
                            "gender": gender, "pen_no": sanitize(pen_no), "apaar_no": sanitize(apaar_no),
                            "father_name": sanitize(father_name), "father_name_local": sanitize(father_name_loc),
                            "mother_name": sanitize(mother_name), "mother_name_local": sanitize(mother_name_loc),
                            "dob": str(dob), "class": cls, "batch": add_batch, 
                            "pub_date": str(opt_pub_date), 
                            "subjects": subjects_data,
                            "total_full": total_full_mark, "total_obt": total_obt_mark,
                            "percentage": round(percentage, 2), "result": result, "grade": grade,
                            "status": "Approved", "payment_mode": "Direct Entry"
                        }
                        if cur_school not in students_db:
                            students_db[cur_school] = {}
                        students_db[cur_school][roll_no_clean] = new_data
                        save_data_json(schools_db, students_db)
                        st.success(f"Roll No {roll_no_clean} Data Saved & Approved!")
                    else:
                        st.error("Roll No and Student Name required.")
            with c_clear:
                if st.button("🧹 Clear Form"):
                    st.rerun()

        with tab_edit:
            st.markdown(f"### ✏️ {t('Edit Student', s_lang)} | Edit Student")
            if approved_students:
                edit_roll = st.selectbox("Select Roll No", list(approved_students.keys()), key="edit_roll_sel")
                curr_st = approved_students[edit_roll]
                
                c_up_n1, c_up_n2 = st.columns(2)
                up_name = c_up_n1.text_input("Edit Name (English)", value=curr_st.get('name', ''))
                up_name_loc = c_up_n2.text_input(f"Edit Name ({s_lang})", value=curr_st.get('name_local', ''))
                
                up_father = c_up_n1.text_input("Edit Father's Name (English)", value=curr_st.get('father_name', ''))
                up_father_loc = c_up_n2.text_input(f"Edit Father's Name ({s_lang})", value=curr_st.get('father_name_local', ''))
                
                up_mother = c_up_n1.text_input("Edit Mother's Name (English)", value=curr_st.get('mother_name', ''))
                up_mother_loc = c_up_n2.text_input(f"Edit Mother's Name ({s_lang})", value=curr_st.get('mother_name_local', ''))
                
                st.markdown("---")
                c_up1, c_up2, c_up3 = st.columns(3)
                with c_up1:
                    genders = ["Male", "Female", "Other"]
                    g_val = curr_st.get('gender', 'Male')
                    up_gender = st.selectbox("Edit Gender", genders, index=genders.index(g_val) if g_val in genders else 0)
                with c_up2:
                    up_pen = st.text_input(f"Edit PEN NO / {t('PEN NO', s_lang)}", value=curr_st.get('pen_no', ''))
                with c_up3:
                    up_apaar = st.text_input(f"Edit APAAR NO / {t('APAAR NO', s_lang)}", value=curr_st.get('apaar_no', ''))

                db_dob_val = curr_st.get('dob', '')
                disp_edit_dob = db_dob_val
                if db_dob_val.count('-') == 2:
                    parts = db_dob_val.split('-')
                    if len(parts[0]) == 4:
                        disp_edit_dob = f"{parts[2]}-{parts[1]}-{parts[0]}"
                        
                up_dob_input = st.text_input(f"Edit DOB (DD-MM-YYYY) / {t('DOB', s_lang)}", value=disp_edit_dob)
                
                c_e1, c_e2 = st.columns(2)
                with c_e1:
                    cls_val = curr_st.get('class', '1')
                    up_cls = st.selectbox(f"Edit Class / {t('CLASS', s_lang)}", classes_list, index=classes_list.index(cls_val) if cls_val in classes_list else 0)
                with c_e2:
                    b_val = curr_st.get('batch', '2025-2026')
                    b_idx = batches_list.index(b_val) if b_val in batches_list else 5
                    up_batch = st.selectbox("Edit Batch", batches_list, index=b_idx)
                
                prev_pub_str = curr_st.get('pub_date', str(datetime.date.today()))
                try:
                    p_y, p_m, p_d = prev_pub_str.split('-')
                    d_val = datetime.date(int(p_y), int(p_m), int(p_d))
                except:
                    d_val = datetime.date.today()
                    
                up_pub_date = st.date_input(
                    f"Edit Results Publication Date (Optional / {t('DATE OF PUBLICATION', s_lang)})", 
                    value=d_val, 
                    key="edit_pub_date"
                )
                
                st.markdown("#### 📚 Edit Subjects & Marks")
                up_subjects = curr_st.get('subjects', {})
                new_up_subjects = {}
                up_tot_full = 0
                up_tot_obt = 0
                
                if up_subjects:
                    for sub_name, sub_info in up_subjects.items():
                        sc1, sc2, sc3 = st.columns(3)
                        with sc1:
                            u_sub = st.text_input("Subject Name", value=sub_name, key=f"s_sub_{sub_name}")
                        with sc2:
                            u_f = st.number_input("Full Mark", value=float(sub_info['full']), key=f"s_f_{sub_name}")
                        with sc3:
                            u_o = st.number_input("Obtained Mark", value=float(sub_info['obt']), key=f"s_o_{sub_name}")
                        if u_sub:
                            new_up_subjects[sanitize(u_sub)] = {"full": u_f, "obt": u_o}
                            up_tot_full += u_f
                            up_tot_obt += u_o
                else:
                    st.info("No detailed subjects found. Using only total marks.")
                    up_tot_full = float(curr_st.get('total_full', 300))
                    up_tot_obt = float(curr_st.get('total_obt', 0))

                st.info(f"📊 **Auto Summary:** Total Marks: {up_tot_obt}/{up_tot_full}")
                
                if st.button("💾 Save Updated Record"):
                    up_dob_save = sanitize(up_dob_input)
                    if up_dob_input.count('-') == 2:
                        parts = up_dob_input.split('-')
                        if len(parts[2]) == 4:
                            up_dob_save = f"{parts[2]}-{parts[1]}-{parts[0]}"
                            
                    new_per = (up_tot_obt / up_tot_full * 100) if up_tot_full > 0 else 0.0
                    new_res = "PASS" if new_per >= 33 else "FAIL"
                    new_grd = "A1" if new_per >= 90 else "A2" if new_per >= 80 else "B1" if new_per >= 70 else "B2" if new_per >= 60 else "C1" if new_per >= 50 else "C2" if new_per >= 40 else "D" if new_per >= 33 else "F"
                    
                    students_db[cur_school][edit_roll].update({
                        "name": sanitize(up_name), "name_local": sanitize(up_name_loc), 
                        "gender": up_gender, "pen_no": sanitize(up_pen), "apaar_no": sanitize(up_apaar),
                        "father_name": sanitize(up_father), "father_name_local": sanitize(up_father_loc),
                        "mother_name": sanitize(up_mother), "mother_name_local": sanitize(up_mother_loc),
                        "dob": up_dob_save, "class": up_cls, "batch": up_batch, 
                        "pub_date": str(up_pub_date),
                        "subjects": new_up_subjects if new_up_subjects else up_subjects,
                        "total_obt": up_tot_obt, "total_full": up_tot_full, 
                        "percentage": round(new_per, 2), "result": new_res, "grade": new_grd
                    })
                    save_data_json(schools_db, students_db)
                    st.success("Record Updated!")
            else:
                st.warning("No approved students available to edit.")

        with tab_report:
            st.markdown(f"### 🖨️ {t('Report Card', s_lang)} | Report Card")
            if approved_students:
                rep_roll = st.selectbox("Select Student Roll No for Report", list(approved_students.keys()), key="rep_sel")
                st_data = approved_students[rep_roll]
                school_name_en = sch_data['name']
                school_name_loc = sch_data.get('name_local', '')
                
                st.markdown(generate_result_card_html(school_name_en, school_name_loc, st_data, rep_roll, s_lang), unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    pdf_file = f"Report_{rep_roll}.pdf"
                    create_pdf(pdf_file, school_name_en, st_data, rep_roll)
                    with open(pdf_file, "rb") as f:
                        st.download_button("📥 Download PDF Report", f, file_name=pdf_file, mime="application/pdf", key="dl_sch")
                with col2:
                    if st.button("🖨️ Print Result Card", key="print_sch"):
                        components.html("<script>window.parent.print();</script>", height=0)
            else:
                st.warning("No students available.")

# ----------------- ZERO-CRASH RESULTS PORTAL (SUPPORTS 1 CRORE+ USERS) -----------------
elif menu == "Results":
    st.query_params["portal"] = "student"
    c_home, c_title = st.columns([1, 8])
    with c_home:
        if st.button("🏠 Home", key="st_home_btn"):
            st.query_params["portal"] = "home"
            st.rerun()
    with c_title:
        st.subheader("🎓 Results Portal")
        
    st.info(
        "🔗 **English:** No School ID is required here. Search using only your Roll Number or Name. \n\n"
        "🔗 **हिन्दी:** यहाँ किसी School ID की आवश्यकता नहीं है। कृपया केवल अपना रोल नंबर या नाम दर्ज करके खोजें। \n\n"
        "🔗 **ଓଡ଼ିଆ:** ଏଠାରେ କୌଣସି School ID ଦରକାର ନାହିଁ। କେବଳ Roll Number କିମ୍ବା Name ଦେଇ ସର୍ଚ୍ଚ କରନ୍ତୁ।"
    )
    
    st_search_query = st.text_input("Roll Number OR Student Name (ରୋଲ୍ ନମ୍ବର କିମ୍ବା ନାମ ଦିଅନ୍ତୁ)")
    st_dob_input = st.text_input("Date of Birth (DD-MM-YYYY)")
    
    if st.button("View Result"):
        if st_search_query and st_dob_input:
            sq_low = sanitize(st_search_query.strip().lower())
            ndob = normalize_dob(st_dob_input)
            
            found_student = None
            found_roll = None
            found_school_id = None
            
            for s_id, school_students in students_db.items():
                if st_search_query in school_students:
                    potential_student = school_students[st_search_query]
                    if normalize_dob(potential_student.get("dob", "")) == ndob and potential_student.get("status", "Approved") == "Approved":
                        found_student = potential_student
                        found_roll = st_search_query
                        found_school_id = s_id
                        break
                
                if not found_student:
                    for r_no, s_info in school_students.items():
                        if s_info.get("name", "").strip().lower() == sq_low:
                            if normalize_dob(s_info.get("dob", "")) == ndob:
                                if s_info.get("status", "Approved") == "Approved":
                                    found_student = s_info
                                    found_roll = r_no
                                    found_school_id = s_id
                                    break
                
                if found_student:
                    break
            
            if found_student:
                sch = schools_db.get(found_school_id, {})
                school_name_en = sch.get('name', 'Unknown School')
                school_name_loc = sch.get('name_local', '')
                s_lang = sch.get("lang", "English")
                
                student_name = found_student.get('name', '').upper()
                st.success(
                    f"🎉 **Welcome {student_name}!** Your result is given below:  \n"
                    f"🎉 **ସ୍ୱାଗତମ୍ {student_name}!** ଆପଣଙ୍କ ରେଜଲ୍ଟ ତଳେ ଦିଆଗଲା:"
                )
                
                st.markdown(generate_result_card_html(school_name_en, school_name_loc, found_student, found_roll, s_lang), unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    pdf_file = f"Result_{found_roll}.pdf"
                    create_pdf(pdf_file, school_name_en, found_student, found_roll)
                    with open(pdf_file, "rb") as f:
                        st.download_button("📥 Download PDF", f, file_name=pdf_file, mime="application/pdf", key="dl_stu")
                
                with col2:
                    if st.button("🖨️ Print Result Card", key="print_stu"):
                        components.html("<script>window.parent.print();</script>", height=0)
            else:
                pending_found = False
                for s_id, school_students in students_db.items():
                    for r_no, s_info in school_students.items():
                        if (r_no == st_search_query or s_info.get("name", "").strip().lower() == sq_low) and normalize_dob(s_info.get("dob", "")) == ndob:
                            status = s_info.get("status")
                            if status == "Pending_Master":
                                st.warning("⏳ Your payment is currently being verified by the Master Admin. Please check back later.")
                                pending_found = True
                                break
                            elif status == "Pending_School":
                                st.warning("⏳ Payment Verified! Your application is pending final admission approval from the School.")
                                pending_found = True
                                break
                            elif status == "Rejected_Refund":
                                st.error("❌ Your application was REJECTED by the school. Your payment has been automatically initiated for REFUND to your original bank account.")
                                pending_found = True
                                break
                    if pending_found: break
                
                if not pending_found:
                    st.error("❌ କୌଣସି ରେକର୍ଡ ମିଳିଲା ନାହିଁ! ଭୁଲ୍ ତଥ୍ୟ (Roll Number/Name କିମ୍ବା DOB) ଦେଇଛନ୍ତି।")
        else:
            st.warning("ଦୟାକରି ସବୁ ତଥ୍ୟ ପୂରଣ କରନ୍ତୁ।")

# --- GLOBAL FOOTER FOR ALL PAGES ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; margin-top: 20px; padding: 15px; background: linear-gradient(90deg, #1e3a8a, #9333ea); color: white; border-radius: 8px; font-weight: bold; font-size: 18px; box-shadow: 0 4px 6px rgba(0,0,0,0.2);'>
    👨‍💻 Software Developed by: <span style='color: #fbbf24; font-size: 20px; text-shadow: 1px 1px 2px #000;'>KULU SUTAR</span> &nbsp;&nbsp;|&nbsp;&nbsp; 📞 Mob: <span style='color: #fbbf24;'>8910223342</span> &nbsp;&nbsp;|&nbsp;&nbsp; ✉️ Mail: <span style='color: #fbbf24;'>kulusutar123@gmail.com</span>
</div>
""", unsafe_allow_html=True)
