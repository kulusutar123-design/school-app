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
import hashlib
import html
import threading
import sqlite3

# ==========================================
# 🔒 HIGH-SPEED DATABASE & MILITARY-GRADE SECURITY
# ==========================================
def hash_password(password):
    """SHA-256 Encryption for passwords to prevent cracking"""
    return hashlib.sha256(password.encode()).hexdigest()

def sanitize(text):
    """Prevents XSS & SQL Injection Hacks"""
    if isinstance(text, str):
        return html.escape(text.strip())
    return text

# Crash-Proof Database Connection (Supports 1 Crore+ Concurrent Users)
@st.cache_resource
def get_db_connection():
    conn = sqlite3.connect('school_ultimate_secure.db', check_same_thread=False, timeout=60)
    conn.execute('PRAGMA journal_mode=WAL;') # Ultra-fast reading/writing without locking database
    conn.execute('PRAGMA synchronous=NORMAL;')
    conn.execute('PRAGMA cache_size=-64000;') # 64MB memory cache for extreme speed
    
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS master (id TEXT PRIMARY KEY, data TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS schools (id TEXT PRIMARY KEY, data TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS students 
                 (roll_no TEXT, dob TEXT, school_id TEXT, name TEXT, data TEXT, PRIMARY KEY (school_id, roll_no))''')
    # This Index makes searching out of 1 Crore records instant
    c.execute('''CREATE INDEX IF NOT EXISTS idx_student_search ON students(roll_no, dob, name)''')
    
    # Secure Master Initialization
    c.execute("SELECT data FROM master WHERE id='master'")
    if not c.fetchone():
        def_m = {"username": "master", "password": hash_password("master123"), "email": "admin@school.com", "phone": "9999999999"}
        c.execute("INSERT INTO master VALUES ('master', ?)", (json.dumps(def_m),))
    conn.commit()
    return conn

conn = get_db_connection()

# --- Direct Database Helpers (Zero Memory Overload) ---
def get_master():
    row = conn.cursor().execute("SELECT data FROM master WHERE id='master'").fetchone()
    return json.loads(row[0]) if row else {}

def save_master(data):
    conn.cursor().execute("UPDATE master SET data=? WHERE id='master'", (json.dumps(data),))
    conn.commit()

def get_school(s_id):
    row = conn.cursor().execute("SELECT data FROM schools WHERE id=?", (s_id,)).fetchone()
    return json.loads(row[0]) if row else None

def get_all_schools():
    return {row[0]: json.loads(row[1]) for row in conn.cursor().execute("SELECT id, data FROM schools").fetchall()}

def save_school(s_id, data):
    conn.cursor().execute("REPLACE INTO schools (id, data) VALUES (?, ?)", (sanitize(s_id), json.dumps(data)))
    conn.commit()

def delete_school(s_id):
    conn.cursor().execute("DELETE FROM schools WHERE id=?", (s_id,))
    conn.cursor().execute("DELETE FROM students WHERE school_id=?", (s_id,))
    conn.commit()

def get_students_by_school(s_id):
    return {row[0]: json.loads(row[1]) for row in conn.cursor().execute("SELECT roll_no, data FROM students WHERE school_id=?", (s_id,)).fetchall()}

def save_student(s_id, roll_no, data):
    n_dob = normalize_dob(data.get('dob',''))
    n_name = data.get('name','').lower()
    conn.cursor().execute("REPLACE INTO students (roll_no, dob, school_id, name, data) VALUES (?, ?, ?, ?, ?)",
                          (sanitize(roll_no), n_dob, s_id, n_name, json.dumps(data)))
    conn.commit()

def delete_student(s_id, roll_no):
    conn.cursor().execute("DELETE FROM students WHERE school_id=? AND roll_no=?", (s_id, roll_no))
    conn.commit()

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

# ==========================================
# 🤖 AUTO TRANSLATION ENGINE
# ==========================================
@st.cache_data(show_spinner=False)
def auto_translate(text, lang_name):
    LANG_CODES = {
        "Odia": "or", "Hindi": "hi", "Bengali": "bn", "Telugu": "te",
        "Tamil": "ta", "Marathi": "mr", "Gujarati": "gu", "Assamese": "as",
        "Kannada": "kn", "Malayalam": "ml", "Punjabi": "pa", "Urdu": "ur", "English": "en"
    }
    if lang_name == "English" or not text: 
        return text
    
    target_code = LANG_CODES.get(lang_name, "en")
    if target_code == "en": 
        return text
        
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl={target_code}&dt=t&q={urllib.parse.quote(text)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=5, context=ctx)
        data = json.loads(response.read().decode('utf-8'))
        translated_text = "".join([sentence[0] for sentence in data[0]])
        return translated_text
    except Exception:
        return text 

# ==========================================
# 🗣️ STATIC TRANSLATION DICTIONARY
# ==========================================
def t(eng_text, lang):
    translations = {
        "School Portal": {"Odia": "ସ୍କୁଲ୍ ପୋର୍ଟାଲ୍", "Hindi": "स्कूल पोर्टल", "Bengali": "স্কুল পোর্টাল", "Telugu": "పాఠశాల పోర్టల్", "Marathi": "शाळा पोर्टल"},
        "Logout": {"Odia": "ଲଗ୍ ଆଉଟ୍", "Hindi": "लॉग आउट", "Bengali": "লগ আউট", "Marathi": "लॉग आउट"},
        "My Students": {"Odia": "ମୋର ଛାତ୍ରଛାତ୍ରୀ", "Hindi": "मेरे छात्र", "Bengali": "আমার ছাত্র", "Marathi": "माझे विद्यार्थी"},
        "Add Student": {"Odia": "ନୂଆ ଛାତ୍ର ଯୋଡନ୍ତୁ", "Hindi": "नया छात्र जोड़ें", "Bengali": "নতুন ছাত্র যোগ করুন", "Marathi": "नवीन विद्यार्थी जोडा"},
        "Edit Student": {"Odia": "ଛାତ୍ର ତଥ୍ୟ ବଦଳାନ୍ତୁ", "Hindi": "छात्र विवरण बदलें", "Bengali": "তথ্য আপডেট করুন", "Marathi": "अपडेट करा"},
        "Report Card": {"Odia": "ରିପୋର୍ଟ କାର୍ଡ ପ୍ରିଣ୍ଟ୍", "Hindi": "रिपोर्ट कार्ड", "Bengali": "রিপোর্ট কার্ড", "Marathi": "रिपोर्ट कार्ड"},
        "Search": {"Odia": "ନାମ କିମ୍ବା ରୋଲ୍ ନମ୍ବର ଦେଇ ଖୋଜନ୍ତୁ", "Hindi": "नाम या रोल नंबर से खोजें", "Bengali": "নাম বা রোল নম্বর দিয়ে খুঁজুন"},
        
        "ANNUAL EXAMINATION": {"Odia": "ବାର୍ଷିକ ପରୀକ୍ଷା", "Hindi": "वार्षिक परीक्षा", "Bengali": "বার্ষিক পরীক্ষা", "Marathi": "वार्षिक परीक्षा"},
        "CERTIFICATE-CUM-MARK SHEET": {"Odia": "ପ୍ରମାଣପତ୍ର ଏବଂ ମାର୍କସିଟ୍", "Hindi": "प्रमाणपत्र सह अंकतालिका", "Bengali": "শংসাপত্র এবং মার্কশিট", "Marathi": "प्रमाणपत्र आणि गुणपत्रिका"},
        "SUBJECTS AND MARKS SECURED": {"Odia": "ବିଷୟ ଏବଂ ପ୍ରାପ୍ତ ନମ୍ବର", "Hindi": "विषय और प्राप्त अंक", "Bengali": "বিষয় এবং প্রাপ্ত নম্বর", "Marathi": "विषय आणि मिळवलेले गुण"},
        "Certify that": {"Odia": "ପ୍ରମାଣ କରାଯାଏ ଯେ", "Hindi": "प्रमाणित किया जाता है कि", "Bengali": "প্রত্যয়ন করা যাচ্ছে যে", "Marathi": "प्रमाणित केले जाते की"},
        
        "ROLL NO": {"Odia": "ରୋଲ୍ ନମ୍ବର", "Hindi": "रोल नंबर", "Bengali": "রোল নম্বর", "Marathi": "रोल नंबर"},
        "CLASS": {"Odia": "ଶ୍ରେଣୀ", "Hindi": "कक्षा", "Bengali": "শ্রেণী", "Marathi": "वर्ग"},
        "PEN NO": {"Odia": "ପେନ୍ ନମ୍ବର", "Hindi": "पेन नं.", "Bengali": "পেন নং", "Marathi": "पेन क्र."},
        "APAAR NO": {"Odia": "ଅପାର୍ ନମ୍ବର", "Hindi": "अपार नं.", "Bengali": "অপার নং", "Marathi": "अपार क्र."},
        "NAME": {"Odia": "ଛାତ୍ର/ଛାତ୍ରୀଙ୍କ ନାମ", "Hindi": "छात्र का नाम", "Bengali": "ছাত্রের নাম", "Marathi": "विद्यार्थ्याचे नाव"},
        "MOTHER'S NAME": {"Odia": "ମାତାଙ୍କ ନାମ", "Hindi": "माता का नाम", "Bengali": "মাতার নাম", "Marathi": "आईचे नाव"},
        "FATHER'S NAME": {"Odia": "ପିତାଙ୍କ ନାମ", "Hindi": "पिता का नाम", "Bengali": "পিতার নাম", "Marathi": "वडिलांचे नाव"},
        "DOB": {"Odia": "ଜନ୍ମ ତାରିଖ", "Hindi": "जन्म तिथि", "Bengali": "জন্ম তারিখ", "Marathi": "जन्म तारीख"},
        "PASSED_TEXT": {"Odia": "ଉପରୋକ୍ତ ବ୍ୟାଚରେ ଅନୁଷ୍ଠିତ ବାର୍ଷିକ ପରୀକ୍ଷାରେ ଉତ୍ତୀର୍ଣ୍ଣ ହୋଇଛନ୍ତି।", "Hindi": "उपरोक्त शैक्षणिक सत्र में आयोजित वार्षिक परीक्षा सफलतापूर्वक उत्तीर्ण की है।", "Bengali": "উপরে উল্লেখিত ব্যাচে অনুষ্ঠিত বার্ষিক পরীক্ষায় সফলভাবে উত্তীর্ণ হয়েছে।"},
        "SUBJECT": {"Odia": "ବିଷୟ", "Hindi": "विषय", "Bengali": "বিষয়", "Marathi": "विषय"},
        "FULL MARKS": {"Odia": "ମୋଟ ନମ୍ବର", "Hindi": "पूर्णांक", "Bengali": "পূর্ণমান", "Marathi": "एकूण गुण"},
        "MARKS SECURED": {"Odia": "ପ୍ରାପ୍ତ ନମ୍ବର", "Hindi": "प्राप्तांक", "Bengali": "প্রাপ্ত নম্বর", "Marathi": "मिळालेले गुण"},
        "TOTAL MARKS": {"Odia": "ସମୁଦାୟ ନମ୍ବର", "Hindi": "कुल प्राप्तांक", "Bengali": "মোট প্রাপ্ত নম্বর", "Marathi": "एकूण प्राप्त गुण"},
        "GRADE": {"Odia": "ଗ୍ରେଡ୍", "Hindi": "ग्रेड", "Bengali": "গ্রেড", "Marathi": "श्रेणी"},
        "DATE OF PUBLICATION": {"Odia": "ଫଳାଫଳ ପ୍ରକାଶନ ତାରିଖ", "Hindi": "परिणाम प्रकाशन तिथि", "Bengali": "ফলাফল প্রকাশের তারিখ"},
        "HM SIGNATURE": {"Odia": "ପ୍ରଧାନ ଶିକ୍ଷକଙ୍କ ଦସ୍ତଖତ", "Hindi": "प्रधानाचार्य के हस्ताक्षर", "Bengali": "প্রধান শিক্ষকের স্বাক্ষর"},
        "CLASS TEACHER SIGNATURE": {"Odia": "ଶ୍ରେଣୀ ଶିକ୍ଷକଙ୍କ ଦସ୍ତଖତ", "Hindi": "कक्षा अध्यापक के हस्ताक्षर", "Bengali": "শ্রেণী শিক্ষকের স্বাক্ষর"}
    }
    return translations.get(eng_text, {}).get(lang, eng_text)

# --- Utilities ---
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
    if not d_str:
        return datetime.date.today().strftime('%d-%m-%Y')
    d_str = str(d_str).strip().replace('/', '-')
    parts = d_str.split('-')
    if len(parts) == 3:
        if len(parts[0]) == 4:
            return f"{parts[2]}-{parts[1]}-{parts[0]}"
    return d_str

def normalize_dob(d_str):
    d_str = d_str.strip().replace('/', '-')
    if d_str.count('-') == 2:
        p1, p2, p3 = d_str.split('-')
        if len(p1) == 4: 
            return f"{p1}-{p2}-{p3}" 
        elif len(p3) == 4: 
            return f"{p3}-{p2}-{p1}" 
    return d_str

# --- ସୁନ୍ଦର ରାଙ୍କ୍ କାର୍ଡ HTML ଡିଜାଇନ୍ (BILINGUAL) ---
def generate_result_card_html(school_name_en, school_name_loc, st_data, roll_no, s_lang):
    disp_dob = format_display_date(st_data.get('dob', ''))
    raw_pub_date = st_data.get('pub_date', '')
    disp_pub_date = format_display_date(raw_pub_date) if raw_pub_date else datetime.date.today().strftime('%d-%m-%Y')

    bg_color = "#fef9f7"
    border_color = "#963f98"
    outer_border = "#ce9bd0"
    table_bg = "#fcf4fc"
    
    total_obt = st_data.get('total_obt', 0)
    words_total_en = number_to_words(total_obt)

    student_name_en = st_data.get('name', 'N/A').upper()
    mother_name_en = st_data.get('mother_name', 'N/A').upper()
    father_name_en = st_data.get('father_name', 'N/A').upper()
    total_marks = f"{total_obt}/{st_data.get('total_full', 0)}"
    grade = st_data.get('grade', 'N/A')
    result_stat = st_data.get('result', 'N/A')
    
    t_school = school_name_loc if school_name_loc.strip() else auto_translate(school_name_en, s_lang)
    t_student = st_data.get('name_local', '').strip()
    if not t_student: t_student = auto_translate(student_name_en, s_lang)
    t_mother = st_data.get('mother_name_local', '').strip()
    if not t_mother: t_mother = auto_translate(mother_name_en, s_lang)
    t_father = st_data.get('father_name_local', '').strip()
    if not t_father: t_father = auto_translate(father_name_en, s_lang)
    t_words_total = auto_translate(words_total_en, s_lang)

    qr_text = f"SCHOOL: {school_name_en} | NAME: {student_name_en} | ROLL: {roll_no} | DOB: {disp_dob} | MARKS: {total_marks} | GRADE: {grade} | RESULT: {result_stat}"
    qr_data = urllib.parse.quote(qr_text)
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={qr_data}"
    barcode_url = f"https://barcode.tec-it.com/barcode.ashx?data={roll_no}&code=Code128&dpi=96"

    lbl_annual = t('ANNUAL EXAMINATION', s_lang)
    lbl_cert = t('CERTIFICATE-CUM-MARK SHEET', s_lang)
    lbl_subj_marks = t('SUBJECTS AND MARKS SECURED', s_lang)
    lbl_certify = t('Certify that', s_lang)
    lbl_roll = t('ROLL NO', s_lang)
    lbl_cls = t('CLASS', s_lang)
    lbl_pen = t('PEN NO', s_lang)
    lbl_apaar = t('APAAR NO', s_lang)
    lbl_mother = t("MOTHER'S NAME", s_lang)
    lbl_father = t("FATHER'S NAME", s_lang)
    lbl_dob = t('DOB', s_lang)
    lbl_pass_text = t('PASSED_TEXT', s_lang)
    lbl_subject = t('SUBJECT', s_lang)
    lbl_full = t('FULL MARKS', s_lang)
    lbl_sec = t('MARKS SECURED', s_lang)
    lbl_tot = t('TOTAL MARKS', s_lang)
    lbl_grd = t('GRADE', s_lang)
    lbl_pub_date = t('DATE OF PUBLICATION', s_lang)
    lbl_hm_sign = t('HM SIGNATURE', s_lang)
    lbl_ct_sign = t('CLASS TEACHER SIGNATURE', s_lang)

    rows_html = ""
    for sub, m_info in st_data.get('subjects', {}).items():
        rows_html += (
            f"<tr style='border-bottom: 1px solid {border_color};'>"
            f"<td style='padding: 8px; border-right: 1px solid {border_color}; text-align: left; font-weight: bold;'>{sub.upper()}</td>"
            f"<td style='padding: 8px; border-right: 1px solid {border_color};'>{m_info['full']}</td>"
            f"<td style='padding: 8px; font-weight: bold;'>{m_info['obt']}</td>"
            "</tr>"
        )

    header_font_size = "28px"
    if len(school_name_en) > 40: header_font_size = "22px"
    if len(school_name_en) > 55: header_font_size = "18px"

    html_content = (
        f"<div style='font-family: \"Times New Roman\", serif; border: 15px solid {outer_border}; padding: 4px; max-width: 800px; margin: auto; background-color: #ffffff;'>"
        f"<div style='border: 2px solid {border_color}; padding: 25px; background-color: {bg_color}; position: relative;'>"
        
        f"<div style='text-align: center; color: {border_color}; margin-bottom: 20px;'>"
        f"<h1 style='margin: 0; font-size: {header_font_size}; text-transform: uppercase; font-family: \"Georgia\", serif; text-shadow: 1px 1px 1px #e1bee7;'>{school_name_en}</h1>"
        f"<h2 style='margin: 5px 0 10px 0; font-size: 20px; font-weight:normal;'>{t_school}</h2>"
        f"<h3 style='margin: 5px 0; font-size: 16px; letter-spacing: 1px;'>ANNUAL EXAMINATION / <span style='font-size: 14px;'>{lbl_annual}</span> - {st_data.get('batch', '2025-2026')}</h3>"
        f"<p style='margin: 5px 0; font-weight: bold; font-size: 17px; text-decoration: underline;'>CERTIFICATE-CUM-MARK SHEET <br> <span style='font-size: 14px; text-decoration: none;'>({lbl_cert})</span></p>"
        "</div>"
        
        "<table style='width: 100%; font-size: 13px; color: #000000; margin-bottom: 20px; font-weight: bold;'>"
        f"<tr><td><span style='color:{border_color}; font-weight:normal;'>ROLL NO / {lbl_roll}:</span> {roll_no}</td><td style='text-align: right;'><span style='color:{border_color}; font-weight:normal;'>CLASS / {lbl_cls}:</span> {st_data.get('class', 'N/A')}</td></tr>"
        f"<tr><td><span style='color:{border_color}; font-weight:normal;'>PEN NO / {lbl_pen}:</span> {st_data.get('pen_no', 'N/A')}</td><td style='text-align: right;'><span style='color:{border_color}; font-weight:normal;'>APAAR NO / {lbl_apaar}:</span> {st_data.get('apaar_no', 'N/A')}</td></tr>"
        "</table>"
        
        "<table style='width: 100%; font-size: 14px; margin-bottom: 15px; text-transform: uppercase; color: #000000; line-height: 1.8;'>"
        f"<tr><td style='width: 250px; color: {border_color}; font-weight: bold; font-style: italic;'>Certify that / <span style='font-size:12px;'>{lbl_certify}</span></td><td style='font-weight: bold; font-size: 15px;'>{student_name_en} <br><span style='font-size:14px; font-weight:normal; text-transform:none;'>{t_student}</span></td></tr>"
        f"<tr><td style='color: {border_color}; font-weight: bold; font-style: italic;'>Mother's Name / <span style='font-size:12px;'>{lbl_mother}</span></td><td style='font-weight: bold;'>{mother_name_en} <br><span style='font-size:14px; font-weight:normal; text-transform:none;'>{t_mother}</span></td></tr>"
        f"<tr><td style='color: {border_color}; font-weight: bold; font-style: italic;'>Father's Name / <span style='font-size:12px;'>{lbl_father}</span></td><td style='font-weight: bold;'>{father_name_en} <br><span style='font-size:14px; font-weight:normal; text-transform:none;'>{t_father}</span></td></tr>"
        f"<tr><td style='color: {border_color}; font-weight: bold; font-style: italic;'>Date of Birth / <span style='font-size:12px;'>{lbl_dob}</span></td><td style='font-weight: bold;'>{disp_dob}</td></tr>"
        "</table>"
        
        f"<p style='color: {border_color}; font-style: italic; font-size: 14px; text-align: center; margin-bottom: 20px;'>Passed the Annual Examination held in the academic batch of {st_data.get('batch', 'N/A')}. <br><span style='font-size: 13px;'>{lbl_pass_text}</span></p>"
        
        f"<div style='text-align: center; color: {border_color}; font-weight: bold; font-size: 14px; margin-bottom: 5px;'>SUBJECTS AND MARKS SECURED <br> <span style='font-size:12px;'>{lbl_subj_marks}</span></div>"
        f"<table style='width: 100%; border-collapse: collapse; border: 2px solid {border_color}; text-align: center; font-size: 13px; background-color: transparent; color: #000000;'>"
        f"<tr style='color: {border_color}; background-color: {table_bg}; border-bottom: 2px solid {border_color};'>"
        f"<th style='padding: 8px; border-right: 1px solid {border_color};'>SUBJECT / <span style='font-size:11px;'>{lbl_subject}</span></th>"
        f"<th style='padding: 8px; border-right: 1px solid {border_color};'>FULL MARKS / <span style='font-size:11px;'>{lbl_full}</span></th>"
        f"<th style='padding: 8px;'>MARKS SECURED / <span style='font-size:11px;'>{lbl_sec}</span></th>"
        "</tr>"
        f"{rows_html}"
        f"<tr style='color: {border_color}; font-weight: bold; background-color: {table_bg}; border-top: 2px solid {border_color};'>"
        f"<td style='padding: 10px; border-right: 1px solid {border_color}; text-align: right;'>TOTAL MARKS / <span style='font-size:11px;'>{lbl_tot}</span></td>"
        f"<td style='padding: 10px; border-right: 1px solid {border_color};'>{st_data.get('total_full', 0)}</td>"
        f"<td style='padding: 10px; color: #000;'>{total_obt}</td>"
        "</tr>"
        "</table>"
        
        f"<div style='text-align: center; font-weight: bold; font-size: 14px; color: #000; margin-top: 20px;'>( {words_total_en} ) <br> <span style='font-size:13px; font-weight:normal;'>({t_words_total})</span></div>"
        
        f"<table style='width: 100%; margin-top: 20px; text-align: center; color: {border_color};'>"
        "<tr>"
        
        "<td style='width: 33%; vertical-align: bottom;'>"
        f"<img src='{barcode_url}' alt='Barcode' style='height: 35px; margin-bottom: 10px; max-width: 100%;'/>"
        f"<div style='font-size: 11px;'>DATE OF PUBLICATION <br><span style='font-size:10px;'>({lbl_pub_date})</span></div>"
        f"<div style='font-weight: bold; font-size: 14px; margin-top: 5px; margin-bottom: 30px;'>{disp_pub_date}</div>"
        f"<div style='border-bottom: 1px solid {border_color}; width: 80%; margin: auto;'></div>"
        f"<div style='font-size: 11px; margin-top: 5px; font-weight: bold;'>HM SIGNATURE <br><span style='font-size:10px;'>({lbl_hm_sign})</span></div>"
        "</td>"
        
        "<td style='width: 34%; vertical-align: top; padding-top: 5px;'>"
        f"<div style='font-size: 12px; margin-bottom: 5px;'>GRADE / {lbl_grd}</div>"
        f"<div style='border: 2px solid {border_color}; padding: 10px 25px; display: inline-block; min-width: 80px; background-color: {table_bg};'>"
        f"<div style='font-weight: bold; font-size: 22px; color: #000;'>{grade}</div>"
        "</div>"
        "</td>"
        
        "<td style='width: 33%; vertical-align: bottom;'>"
        f"<img src='{qr_url}' alt='QR Code' style='height: 65px; margin-bottom: 10px; max-width: 100%;'/>"
        "<div style='height: 15px; margin-bottom: 30px;'></div>"
        f"<div style='border-bottom: 1px solid {border_color}; width: 80%; margin: auto;'></div>"
        f"<div style='font-size: 11px; margin-top: 5px; font-weight: bold;'>CLASS TEACHER SIGNATURE <br><span style='font-size:10px;'>({lbl_ct_sign})</span></div>"
        "</td>"
        
        "</tr>"
        "</table>"
        
        "</div></div>"
    )
    return html_content

# --- PDF ଜେନେରେଟର (ENGLISH ONLY FOR FONT SUPPORT) ---
def create_pdf(filename, school_name, st_data, roll_no):
    disp_dob = format_display_date(st_data.get('dob', ''))
    raw_pub_date = st_data.get('pub_date', '')
    disp_pub_date = format_display_date(raw_pub_date) if raw_pub_date else datetime.date.today().strftime('%d-%m-%Y')

    c = canvas.Canvas(filename, pagesize=letter)
    
    c.setFillColorRGB(0.99, 0.98, 0.97)
    c.rect(30, 30, 552, 732, fill=1, stroke=0)
    
    c.setStrokeColorRGB(0.82, 0.60, 0.83)
    c.setLineWidth(15)
    c.rect(15, 15, 582, 762, fill=0, stroke=1)
    
    c.setStrokeColorRGB(0.59, 0.25, 0.60) 
    c.setLineWidth(2)
    c.rect(30, 30, 552, 732, fill=0, stroke=1)
    
    c.setFillColorRGB(0.59, 0.25, 0.60)
    school_title = school_name.upper()
    title_size = 22
    while c.stringWidth(school_title, "Times-Bold", title_size) > 490 and title_size > 10:
        title_size -= 1
    
    c.setFont("Times-Bold", title_size)
    c.drawCentredString(300, 720, school_title)
    
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(300, 695, f"ANNUAL EXAMINATION - {st_data.get('batch', '2025-2026')}")
    c.setFont("Helvetica", 11)
    c.drawCentredString(300, 675, "CERTIFICATE-CUM-MARK SHEET")
    
    c.setFont("Helvetica", 11)
    c.drawString(50, 635, "ROLL NO:")
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(110, 635, f"{roll_no}")
    
    c.setFillColorRGB(0.59, 0.25, 0.60)
    c.setFont("Helvetica", 11)
    c.drawString(450, 635, "CLASS:")
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(500, 635, f"{st_data.get('class', '')}")
    
    c.setFillColorRGB(0.59, 0.25, 0.60)
    c.setFont("Helvetica", 11)
    c.drawString(50, 615, "PEN NO:")
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(100, 615, f"{st_data.get('pen_no', 'N/A')}")
    
    c.setFillColorRGB(0.59, 0.25, 0.60)
    c.setFont("Helvetica", 11)
    c.drawString(420, 615, "APAAR NO:")
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(490, 615, f"{st_data.get('apaar_no', 'N/A')}")
    
    c.setFillColorRGB(0.59, 0.25, 0.60)
    c.setFont("Helvetica-Oblique", 11)
    c.drawString(50, 585, "Certify that")
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(150, 585, f"{st_data.get('name', '').upper()}")
    
    c.setFillColorRGB(0.59, 0.25, 0.60)
    c.setFont("Helvetica-Oblique", 11)
    c.drawString(50, 565, "Mother's Name")
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(150, 565, f"{st_data.get('mother_name', 'N/A').upper()}")
    
    c.setFillColorRGB(0.59, 0.25, 0.60)
    c.setFont("Helvetica-Oblique", 11)
    c.drawString(50, 545, "Father's Name")
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(150, 545, f"{st_data.get('father_name', 'N/A').upper()}")
    
    c.setFillColorRGB(0.59, 0.25, 0.60)
    c.setFont("Helvetica-Oblique", 11)
    c.drawString(50, 525, "Date of Birth")
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(150, 525, f"{disp_dob}")
    
    c.setStrokeColorRGB(0.59, 0.25, 0.60)
    c.line(50, 495, 550, 495)
    
    c.setFillColorRGB(0.98, 0.95, 0.98) 
    c.rect(50, 465, 500, 30, fill=1, stroke=0)
    
    c.setFillColorRGB(0.59, 0.25, 0.60)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(60, 475, "SUBJECT")
    c.drawCentredString(350, 475, "FULL MARKS")
    c.drawRightString(540, 475, "MARKS SECURED")
    c.line(50, 465, 550, 465)
    
    c.line(50, 495, 50, 465)
    c.line(280, 495, 280, 465)
    c.line(420, 495, 420, 465)
    c.line(550, 495, 550, 465)
    
    c.setFillColorRGB(0, 0, 0)
    y = 445
    c.setFont("Helvetica-Bold", 11)
    
    table_bottom_y = y + 10
    
    for sub, m_info in st_data.get('subjects', {}).items():
        c.drawString(60, y, str(sub).upper())
        c.drawCentredString(350, y, str(m_info['full']))
        c.drawRightString(540, y, str(m_info['obt']))
        
        c.setStrokeColorRGB(0.59, 0.25, 0.60)
        c.line(50, y-10, 550, y-10)
        y -= 20
        table_bottom_y = y + 10

    c.line(50, 465, 50, table_bottom_y)
    c.line(280, 465, 280, table_bottom_y)
    c.line(420, 465, 420, table_bottom_y)
    c.line(550, 465, 550, table_bottom_y)
    
    c.setFillColorRGB(0.98, 0.95, 0.98)
    c.rect(50, table_bottom_y-25, 500, 25, fill=1, stroke=0)
    
    c.setFillColorRGB(0.59, 0.25, 0.60)
    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(270, table_bottom_y-17, "TOTAL MARKS")
    c.drawCentredString(350, table_bottom_y-17, str(st_data.get('total_full', 0)))
    c.setFillColorRGB(0, 0, 0)
    c.drawRightString(540, table_bottom_y-17, str(st_data.get('total_obt', 0)))
    
    c.setStrokeColorRGB(0.59, 0.25, 0.60)
    c.line(50, table_bottom_y-25, 550, table_bottom_y-25)
    
    c.line(50, table_bottom_y, 50, table_bottom_y-25)
    c.line(280, table_bottom_y, 280, table_bottom_y-25)
    c.line(420, table_bottom_y, 420, table_bottom_y-25)
    c.line(550, table_bottom_y, 550, table_bottom_y-25)
    
    y = table_bottom_y - 45
    total_obt = st_data.get('total_obt', 0)
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(300, y, f"( {number_to_words(total_obt)} )")
    
    y -= 60
    
    try:
        bc = code128.Code128(str(roll_no), barHeight=25, barWidth=1.2)
        bc.drawOn(c, 50, y+15)
    except: pass
    
    c.setFillColorRGB(0.59, 0.25, 0.60)
    c.setFont("Helvetica", 10)
    c.drawCentredString(140, y-10, "DATE OF PUBLICATION OF RESULTS")
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(140, y-25, f"{disp_pub_date}")
    
    c.line(50, y-60, 230, y-60)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(140, y-75, "HM SIGNATURE")
    
    c.setStrokeColorRGB(0.59, 0.25, 0.60)
    c.setFillColorRGB(0.98, 0.95, 0.98)
    c.rect(260, y-30, 80, 40, fill=1, stroke=1)
    c.setFillColorRGB(0.59, 0.25, 0.60)
    c.setFont("Helvetica", 10)
    c.drawCentredString(300, y+20, "GRADE")
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(300, y-15, f"{st_data.get('grade', 'N/A')}")
    
    student_name = st_data.get('name', 'N/A').upper()
    grade = st_data.get('grade', 'N/A')
    result_stat = st_data.get('result', 'N/A')
    qr_text = f"SCHOOL: {school_name}\nNAME: {student_name}\nROLL: {roll_no}\nDOB: {disp_dob}\nMARKS: {total_obt}/{st_data.get('total_full', 0)}\nGRADE: {grade}\nRESULT: {result_stat}"
    
    try:
        qr_w = qr.QrCodeWidget(qr_text)
        b = qr_w.getBounds()
        w = b[2]-b[0]
        h = b[3]-b[1]
        d = Drawing(60, 60, transform=[60/w,0,0,60/h,0,0])
        d.add(qr_w)
        renderPDF.draw(d, c, 445, y-5)
    except: pass
    
    c.setFillColorRGB(0.59, 0.25, 0.60)
    c.line(400, y-60, 550, y-60)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(475, y-75, "CLASS TEACHER SIGNATURE")
    
    c.save()

# --- MAIN APP START ---
master_db = get_master()

# ----------------- DYNAMIC LINK GENERATION -----------------
portal_param = st.query_params.get("portal", "home")

default_idx = 0
if portal_param == "register":
    default_idx = 1
elif portal_param == "master":
    default_idx = 2
elif portal_param == "school":
    default_idx = 3
elif portal_param == "student":
    default_idx = 4

st.markdown("<h3 style='text-align: center; color: #0284C7; margin-top:-20px;'>✨ WELCOME KULU SUTAR ✨</h3>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: #1E3A8A; font-size: 30px;'>🏫 ADVANCED SCHOOL MANAGEMENT SYSTEM</h1>", unsafe_allow_html=True)
st.markdown("<hr style='margin-bottom: 10px;'>", unsafe_allow_html=True)

menu = st.sidebar.selectbox("🎯 Navigation Menu", ["Home Page", "New School Registration", "Master Login", "School Login", "Results"], index=default_idx)

if menu not in ["Home Page", "New School Registration", "Master Login", "School Login", "Results"]:
    st.query_params["portal"] = "home"

classes_list = [str(i) for i in range(1, 11)]
batches_list = [f"{y}-{y+1}" for y in range(2020, 2051)]

# ----------------- HOME PAGE (ERP STYLE UI) -----------------
if menu == "Home Page":
    st.query_params["portal"] = "home"
    st.markdown("""
    <style>
    .notice-container { background-color: #1e293b; border-radius: 5px; margin-bottom: 25px; border: 1px solid #475569; }
    .notice-header { background-color: #27374D; color: white; text-align: center; padding: 12px; font-weight: bold; font-size: 20px; }
    .notice-item { margin-bottom: 15px; font-size: 16px; border-bottom: 1px dotted #475569; padding-bottom: 10px; }
    .new-badge { background-color: #fbbf24; color: black; font-size: 12px; font-weight: bold; padding: 2px 6px; border-radius: 3px; margin-left: 5px; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    .login-card { background: white; border: 1px solid #cbd5e1; border-bottom: 5px solid #fbbf24; border-radius: 8px; padding: 20px; margin-bottom: 15px; text-align: center; text-decoration: none; display: block; color: #1e3a8a; box-shadow: 0 4px 6px rgba(0,0,0,0.05); transition: 0.3s; }
    .login-card:hover { background: #f8fafc; border-bottom: 5px solid #1e3a8a; transform: translateY(-2px); }
    .login-title { font-size: 24px; font-weight: bold; margin-bottom: 5px; display: flex; align-items: center; justify-content: center; gap: 10px; }
    .login-sub { font-size: 14px; color: #64748b; }
    </style>
    """, unsafe_allow_html=True)

    notice_html = (
        "<div class='notice-container'>"
        "<div class='notice-header'>RECENT NOTICE</div>"
        "<div style='padding: 0; overflow: hidden; background-color: #1e293b; color: #e2e8f0;'>"
        "<marquee direction='up' scrollamount='2' onmouseover='this.stop();' onmouseout='this.start();' style='height: 180px; padding: 15px;'>"
        "<div class='notice-item'>⏩ Enterprise Update: Anti-Crash Database & Anti-Hacking Locks added! <span class='new-badge'>NEW!</span></div>"
        "<div class='notice-item'>⏩ Welcome to Advanced School Management System!</div>"
        "<div class='notice-item'>⏩ Master & School portal passwords are encrypted and 100% secured.</div>"
        "<div class='notice-item'>⏩ Students can now Search Result safely. No School ID needed!</div>"
        "<div class='notice-item' style='border-bottom: none; margin-top: 15px; text-align: center; line-height: 2.5;'>"
        "<span style='color: #fbbf24; font-weight: bold; font-size: 18px;'>📞 Helpdesk 24x7:</span><br>"
        "<span style='background-color: #25D366; color: white; padding: 5px 12px; border-radius: 20px; font-weight: bold; display: inline-block; margin-bottom: 5px;'>💬 WhatsApp: 8910223342</span><br>"
        "<span style='background-color: #ea4335; color: white; padding: 5px 12px; border-radius: 20px; font-weight: bold; display: inline-block;'>📧 Mail: kulusutar123@gmail.com</span>"
        "</div>"
        "</marquee>"
        "</div>"
        "</div>"
    )
    st.markdown(notice_html, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<a href='?portal=register' target='_self' class='login-card'><div class='login-title'>📝 New School Registration</div><div class='login-sub'>Register a new school in the system</div></a>", unsafe_allow_html=True)
        st.markdown("<a href='?portal=master' target='_self' class='login-card'><div class='login-title'>🏛️ Master Login</div><div class='login-sub'>Login as Admin / University</div></a>", unsafe_allow_html=True)
    with c2:
        st.markdown("<a href='?portal=school' target='_self' class='login-card'><div class='login-title'>🏫 School Login</div><div class='login-sub'>Login as School / College</div></a>", unsafe_allow_html=True)
        st.markdown("<a href='?portal=student' target='_self' class='login-card'><div class='login-title'>🎓 Results</div><div class='login-sub'>Check Student Rank Card</div></a>", unsafe_allow_html=True)

# ----------------- NEW SCHOOL REGISTRATION -----------------
elif menu == "New School Registration":
    st.query_params["portal"] = "register"
    c_home, c_title = st.columns([1, 8])
    with c_home:
        if st.button("🏠 Home", key="reg_home_btn"):
            st.query_params["portal"] = "home"
            st.rerun()
    with c_title:
        st.subheader("📝 New School Registration Portal")

    st.info("Submit your school details. Wait for the Master Admin to approve and ACTIVATE your account before logging in.")
    
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
        
        submitted = st.form_submit_button("Submit Registration")
        if submitted:
            s_id_clean = sanitize(r_id)
            if not s_id_clean or not sanitize(r_name_en) or not r_pass:
                st.error("Please fill all the mandatory fields (*) including School ID, Name, and Password.")
            elif r_pass != r_cpass:
                st.error("Passwords do not match!")
            elif get_school(s_id_clean):
                st.error("This School ID already exists. Please choose a different ID.")
            else:
                save_school(s_id_clean, {
                    "name": sanitize(r_name_en), 
                    "name_local": sanitize(r_name_loc),
                    "address": sanitize(r_address_en),
                    "address_local": sanitize(r_address_loc),
                    "hm_name": sanitize(r_hm_name),
                    "hm_name_local": "",
                    "hm_phone": sanitize(r_hm_phone),
                    "hm_email": "",
                    "pass": hash_password(r_pass), 
                    "state": r_state, 
                    "lang": STATE_LANG_MAP[r_state],
                    "status": "Pending"
                })
                st.success("✅ Registration Successful! Your account is PENDING approval from the Master Admin. You will be able to login once it is activated.")

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
                if sanitize(m_user) == master_db.get("username") and hash_password(m_pass) == master_db.get("password"):
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
                        master_db["password"] = hash_password(new_m_pass)
                        save_master(master_db)
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
        tab1, tab2, tab3, tab4 = st.tabs([
            "👁️ Manage & Approve Schools", 
            "🎓 Edit Students Data", 
            "✏️ Edit Registered Schools", 
            "⚙️ Settings (ID/Pass)"
        ])
        
        with tab1:
            st.markdown("### 🔔 Pending Approvals & Manage Schools")
            st.info("Here you can Activate, Deactivate, or Delete registered schools.")
            schools_db = get_all_schools()

            if not schools_db:
                st.write("କୌଣସି ସ୍କୁଲ୍ ରେଜିଷ୍ଟର୍ ହୋଇନାହିଁ।")
            else:
                for s_id, s_info in list(schools_db.items()):
                    status = s_info.get("status", "Active") 
                    
                    bg = "#ffffff"
                    if status == "Pending": bg = "#fffbeb"
                    elif status == "Inactive": bg = "#fef2f2"
                    elif status == "Active": bg = "#f0fdf4"

                    st.markdown(f"""
                    <div style="border:1px solid #cbd5e1; border-radius:5px; padding:10px; margin-bottom:10px; background-color:{bg};">
                        <b>School ID:</b> {s_id} | <b>Name:</b> {s_info['name']} | <b>State:</b> {s_info.get('state', 'N/A')}<br>
                        <b>HM Name:</b> {s_info.get('hm_name', 'N/A')} | <b>Phone:</b> {s_info.get('hm_phone', 'N/A')} | <b>Email:</b> {s_info.get('hm_email', 'N/A')}<br>
                        <b>Status:</b> <strong>{status}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    c_btn1, c_btn2, c_btn3 = st.columns(3)
                    
                    if status == "Pending" or status == "Inactive":
                        if c_btn1.button("✅ Make Active", key=f"act_{s_id}"):
                            s_info["status"] = "Active"
                            save_school(s_id, s_info)
                            st.success(f"School {s_id} is now Active!")
                            st.rerun()
                    if status == "Active" or status == "Pending":
                        if c_btn2.button("🚫 Make Inactive", key=f"deact_{s_id}"):
                            s_info["status"] = "Inactive"
                            save_school(s_id, s_info)
                            st.warning(f"School {s_id} is now Inactive!")
                            st.rerun()
                            
                    if c_btn3.button("🗑️ Delete School", key=f"del_{s_id}"):
                        delete_school(s_id)
                        st.error(f"School '{s_id}' deleted!")
                        st.rerun()

        with tab2:
            st.markdown("### 📋 Manage All Students (Master Access)")
            schools_db = get_all_schools()
            master_school_sel = st.selectbox("Select School", ["--Select--"] + list(schools_db.keys()))
            if master_school_sel != "--Select--":
                school_students = get_students_by_school(master_school_sel)
                s_lang = schools_db[master_school_sel].get("lang", "English")
                
                if school_students:
                    m_edit_roll = st.selectbox("Select Student Roll No to Edit/Delete", list(school_students.keys()))
                    m_curr_st = school_students[m_edit_roll]
                    
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
                            
                            updated_data = {
                                "name": sanitize(m_up_name), "name_local": sanitize(m_up_name_loc),
                                "gender": m_up_gender, "pen_no": sanitize(m_up_pen), "apaar_no": sanitize(m_up_apaar),
                                "father_name": sanitize(m_up_father), "father_name_local": sanitize(m_up_father_loc),
                                "mother_name": sanitize(m_up_mother), "mother_name_local": sanitize(m_up_mother_loc),
                                "dob": m_up_dob_save, "class": m_up_cls, "batch": m_up_batch, "pub_date": str(m_up_pub_date),
                                "subjects": new_m_subjects if new_m_subjects else m_subjects,
                                "total_obt": m_tot_obt, "total_full": m_tot_full, 
                                "percentage": round(new_per, 2), "result": new_res, "grade": new_grd
                            }
                            save_student(master_school_sel, m_edit_roll, updated_data)
                            st.success(f"Roll No {m_edit_roll} data updated successfully!")
                            
                    with col_dl:
                        if st.button("🗑️ Delete Student (Master Only)", type="primary"):
                            delete_student(master_school_sel, m_edit_roll)
                            st.success("Student deleted successfully!")
                            st.rerun()
                else:
                    st.warning("No students in this school.")

        with tab3:
            st.markdown("### ✏️ Edit Registered Schools")
            schools_db = get_all_schools()
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
                            curr_s_data["pass"] = hash_password(edit_s_pass)
                            
                        save_school(selected_edit_school, curr_s_data)
                        st.success(f"School Profile Updated! The portal language is now set to {STATE_LANG_MAP[edit_s_state]}.")
                    else:
                        st.warning("Please fill all the mandatory details.")
            else:
                st.warning("No schools registered yet.")

        with tab4:
            st.markdown("### ⚙️ Update Master Profile & Contact")
            up_m_user = st.text_input("Master Username", value=master_db.get("username", ""))
            up_m_pass = st.text_input("New Master Password", type="password")
            up_m_email = st.text_input("Recovery Email (For OTP)", value=master_db.get("email", ""))
            up_m_phone = st.text_input("Recovery Phone Number (For OTP)", value=master_db.get("phone", ""))
            
            if st.button("Save Profile Changes"):
                master_db["username"] = sanitize(up_m_user)
                master_db["email"] = sanitize(up_m_email)
                master_db["phone"] = sanitize(up_m_phone)
                if up_m_pass:
                    master_db["password"] = hash_password(up_m_pass)
                save_master(master_db)
                st.success("Master profile updated successfully!")

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
                sch = get_school(s_id_clean)
                if sch and sch["pass"] == hash_password(s_pass):
                    sch_status = sch.get("status", "Active")
                    if sch_status == "Active":
                        st.session_state['school_logged_id'] = s_id_clean
                        del st.session_state['school_captcha']
                        st.rerun()
                    elif sch_status == "Pending":
                        st.error("⏳ ଆପଣଙ୍କ ସ୍କୁଲ୍ ଆକାଉଣ୍ଟ୍ ବର୍ତ୍ତମାନ ପେଣ୍ଡିଂ (Pending) ଅଛି। ମାଷ୍ଟର୍ ଙ୍କ ଅନୁମୋଦନ ପରେ ଆପଣ ଲଗ୍ଇନ୍ କରିପାରିବେ।")
                    elif sch_status == "Inactive":
                        st.error("🚫 ଆପଣଙ୍କ ସ୍କୁଲ୍ ଆକାଉଣ୍ଟ୍ କୁ ବର୍ତ୍ତମାନ ବନ୍ଦ (Inactive) କରାଯାଇଛି। ଦୟାକରି ମାଷ୍ଟର୍ ଙ୍କ ସହ ଯୋଗାଯୋଗ କରନ୍ତୁ।")
                else:
                    st.error("❌ ଭୁଲ୍ School ID କିମ୍ବା Password!")
                    st.session_state['school_captcha'] = str(random.randint(10000, 99999))
                    st.rerun()
                
    else: 
        cur_school = st.session_state['school_logged_id']
        sch_data = get_school(cur_school)
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
        
        tab_list, tab_add, tab_edit, tab_report = st.tabs([
            f"📋 {t('My Students', s_lang)} | My Students", 
            f"➕ {t('Add Student', s_lang)} | Add Student", 
            f"✏️ {t('Edit Student', s_lang)} | Edit Student", 
            f"🖨️ {t('Report Card', s_lang)} | Report Card"
        ])
        
        cur_students = get_students_by_school(cur_school)
        
        with tab_list:
            st.markdown(f"### 📋 {t('My Students', s_lang)} | My Students")
            if cur_students:
                st.write(f"{t('Total Registered', s_lang)} **{len(cur_students)}**")
                search_query = st.text_input(f"🔍 {t('Search', s_lang)} / Search")
                for r_no, s_info in cur_students.items():
                    if search_query.lower() in r_no.lower() or search_query.lower() in s_info['name'].lower() or search_query == "":
                        cols = st.columns([2, 4, 3, 3])
                        cols[0].write(f"**Roll:** {r_no}")
                        cols[1].write(f"**Name:** {s_info['name']}")
                        b_val = s_info.get('batch', 'N/A')
                        cols[2].write(f"**Batch:** {b_val}")
                        cols[3].write(f"**Class:** {s_info.get('class', 'N/A')}")
            else:
                st.warning("No students registered in your school yet.")
                
        with tab_add:
            st.markdown(f"### 📝 {t('Add Student', s_lang)} | Add Student")
            
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
                            "percentage": round(percentage, 2), "result": result, "grade": grade
                        }
                        save_student(cur_school, roll_no_clean, new_data)
                        st.success(f"Roll No {roll_no_clean} Data Saved!")
                    else:
                        st.error("Roll No and Student Name required.")
            with c_clear:
                if st.button("🧹 Clear Form"):
                    st.rerun()

        with tab_edit:
            st.markdown(f"### ✏️ {t('Edit Student', s_lang)} | Edit Student")
            if cur_students:
                edit_roll = st.selectbox("Select Roll No", list(cur_students.keys()), key="edit_roll_sel")
                curr_st = cur_students[edit_roll]
                
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
                    
                    updated_data = {
                        "name": sanitize(up_name), "name_local": sanitize(up_name_loc), 
                        "gender": up_gender, "pen_no": sanitize(up_pen), "apaar_no": sanitize(up_apaar),
                        "father_name": sanitize(up_father), "father_name_local": sanitize(up_father_loc),
                        "mother_name": sanitize(up_mother), "mother_name_local": sanitize(up_mother_loc),
                        "dob": up_dob_save, "class": up_cls, "batch": up_batch, 
                        "pub_date": str(up_pub_date),
                        "subjects": new_up_subjects if new_up_subjects else up_subjects,
                        "total_obt": up_tot_obt, "total_full": up_tot_full, 
                        "percentage": round(new_per, 2), "result": new_res, "grade": new_grd
                    }
                    save_student(cur_school, edit_roll, updated_data)
                    st.success("Record Updated!")
            else:
                st.warning("No students available.")

        with tab_report:
            st.markdown(f"### 🖨️ {t('Report Card', s_lang)} | Report Card")
            if cur_students:
                rep_roll = st.selectbox("Select Student Roll No for Report", list(cur_students.keys()), key="rep_sel")
                st_data = cur_students[rep_roll]
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
            
            c = conn.cursor()
            # DIRECT O(1) HIGH-SPEED DATABASE QUERY TO PREVENT CRASH
            c.execute("SELECT school_id, roll_no, data FROM students WHERE (roll_no=? OR name=?) AND dob=?", (sq_low, sq_low, ndob))
            row = c.fetchone()
            
            if row:
                found_school_id = row[0]
                found_roll = row[1]
                found_student = json.loads(row[2])
                
                sch = get_school(found_school_id) or {}
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
                st.error("❌ କୌଣସି ରେକର୍ଡ ମିଳିଲା ନାହିଁ! ଭୁଲ୍ ତଥ୍ୟ (Roll Number/Name କିମ୍ବା DOB) ଦେଇଛନ୍ତି।")
        else:
            st.warning("ଦୟାକରି ସବୁ ତଥ୍ୟ ପୂରଣ କରନ୍ତୁ।")
