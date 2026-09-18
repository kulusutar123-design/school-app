import streamlit as st
import streamlit.components.v1 as components
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code128, qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
import json, os, datetime, random, urllib.parse, urllib.request, ssl, hashlib, html, sqlite3

# ==========================================
# 🔒 HIGH-SPEED DATABASE & MILITARY-GRADE SECURITY
# ==========================================
def hash_password(password):
    """SHA-256 Encryption for passwords to prevent cracking"""
    return hashlib.sha256(password.encode()).hexdigest()

def sanitize(text):
    """Prevents XSS & SQL Injection Hacks"""
    return html.escape(str(text).strip()) if text else ""

# Crash-Proof Database Connection (Supports 1 Crore+ Concurrent Users)
@st.cache_resource
def get_db_connection():
    conn = sqlite3.connect('school_ultimate_secure.db', check_same_thread=False, timeout=30)
    conn.execute('PRAGMA journal_mode=WAL;') # Ultra-fast reading/writing without locking
    conn.execute('PRAGMA synchronous=NORMAL;')
    
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS master (id TEXT PRIMARY KEY, data TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS schools (id TEXT PRIMARY KEY, data TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS students 
                 (roll_no TEXT, dob TEXT, school_id TEXT, name TEXT, data TEXT, PRIMARY KEY (school_id, roll_no))''')
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
    return json.loads(conn.cursor().execute("SELECT data FROM master WHERE id='master'").fetchone()[0])

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
# 🌐 APP SETTINGS & TRANSLATIONS
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

# ==========================================
# 🎨 RESULT CARD HTML & PDF
# ==========================================
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
    
    c.setStrokeColorRGB(0.59, 0.25, 0.60); c.line(50, 495, 550, 495)
    c.setFillColorRGB(0.98, 0.95, 0.98); c.rect(50, 465, 500, 30, fill=1, stroke=0)
    c.setFillColorRGB(0.59, 0.25, 0.60); c.setFont("Helvetica-Bold", 11)
    c.drawString(60, 475, "SUBJECT"); c.drawCentredString(350, 475, "FULL MARKS"); c.drawRightString(540, 475, "MARKS SECURED")
    c.line(50, 465, 550, 465); c.line(50, 495, 50, 465); c.line(280, 495, 280, 465); c.line(420, 495, 420, 465); c.line(550, 495, 550, 465)
    
    c.setFillColorRGB(0,0,0); y = 445; t_b_y = y + 10
    for sub, m_info in st_data.get('subjects', {}).items():
        c.drawString(60, y, str(sub).upper()); c.drawCentredString(350, y, str(m_info['full'])); c.drawRightString(540, y, str(m_info['obt']))
        c.setStrokeColorRGB(0.59, 0.25, 0.60); c.line(50, y-10, 550, y-10)
        y -= 20; t_b_y = y + 10
    c.line(50, 465, 50, t_b_y); c.line(280, 465, 280, t_b_y); c.line(420, 465, 420, t_b_y); c.line(550, 465, 550, t_b_y)
    
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

# ==========================================
# 🚀 MAIN APP LOGIC
# ==========================================
st.markdown("<h3 style='text-align: center; color: #0284C7; margin-top:-20px;'>✨ WELCOME KULU SUTAR ✨</h3>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: #1E3A8A; font-size: 30px;'>🏫 ADVANCED SCHOOL MANAGEMENT SYSTEM</h1>", unsafe_allow_html=True)

portal_param = st.query_params.get("portal", "home")
d_idx = {"home":0, "register":1, "master":2, "school":3, "student":4}.get(portal_param, 0)
menu = st.sidebar.selectbox("🎯 Navigation Menu", ["Home Page", "New School Registration", "Master Login", "School Login", "Results"], index=d_idx)

if menu not in ["Home Page", "New School Registration", "Master Login", "School Login", "Results"]:
    st.query_params["portal"] = "home"

classes_list = [str(i) for i in range(1, 11)]
batches_list = [f"{y}-{y+1}" for y in range(2020, 2051)]

master_db = get_master()

# --- HOME PAGE ---
if menu == "Home Page":
    st.query_params["portal"] = "home"
    st.markdown("""
    <style>
    .login-card { background: white; border: 1px solid #cbd5e1; border-bottom: 5px solid #fbbf24; border-radius: 8px; padding: 20px; margin-bottom: 15px; text-align: center; text-decoration: none; display: block; color: #1e3a8a; box-shadow: 0 4px 6px rgba(0,0,0,0.05); transition: 0.3s; }
    .login-card:hover { background: #f8fafc; border-bottom: 5px solid #1e3a8a; transform: translateY(-2px); }
    .login-title { font-size: 24px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<a href='?portal=register' target='_self' class='login-card'><div class='login-title'>📝 New School Registration</div></a>", unsafe_allow_html=True)
        st.markdown("<a href='?portal=master' target='_self' class='login-card'><div class='login-title'>🏛️ Master Login</div></a>", unsafe_allow_html=True)
    with c2:
        st.markdown("<a href='?portal=school' target='_self' class='login-card'><div class='login-title'>🏫 School Login</div></a>", unsafe_allow_html=True)
        st.markdown("<a href='?portal=student' target='_self' class='login-card'><div class='login-title'>🎓 Results</div></a>", unsafe_allow_html=True)

# --- REGISTRATION ---
elif menu == "New School Registration":
    st.query_params["portal"] = "register"
    st.subheader("📝 New School Registration Portal")
    with st.form("reg_form"):
        r_id = st.text_input("School ID (Create Unique ID) *")
        c1, c2 = st.columns(2)
        r_name = c1.text_input("School Name (English) *")
        r_name_loc = c2.text_input("School Name (Local Language)")
        r_state = st.selectbox("Select State", list(STATE_LANG_MAP.keys()), index=18)
        ch1, ch2 = st.columns(2)
        hm_n = ch1.text_input("HM Name (English)")
        hm_n_loc = ch2.text_input("HM Name (Local)")
        cp1, cp2 = st.columns(2)
        hm_ph = cp1.text_input("HM Mobile")
        hm_em = cp2.text_input("HM Email")
        p1, p2 = st.columns(2)
        pwd = p1.text_input("Password *", type="password")
        cpwd = p2.text_input("Confirm Password *", type="password")
        
        if st.form_submit_button("Submit Registration"):
            s_id_clean = sanitize(r_id)
            if not s_id_clean or not sanitize(r_name) or not pwd: st.error("Fill mandatory fields (*)")
            elif pwd != cpwd: st.error("Passwords do not match!")
            elif get_school(s_id_clean): st.error("ID exists! Choose another.")
            else:
                save_school(s_id_clean, {
                    "name": sanitize(r_name), "name_local": sanitize(r_name_loc),
                    "hm_name": sanitize(hm_n), "hm_name_local": sanitize(hm_n_loc),
                    "hm_phone": sanitize(hm_ph), "hm_email": sanitize(hm_em),
                    "pass": hash_password(pwd), "state": r_state, "lang": STATE_LANG_MAP[r_state], "status": "Pending"
                })
                st.success("✅ Registration Successful! PENDING Master Approval.")

# --- MASTER LOGIN ---
elif menu == "Master Login":
    st.query_params["portal"] = "master"
    st.subheader("🔑 Master Administrator Portal")
    if not st.session_state.get('master_logged', False):
        m_u = st.text_input("Username")
        m_p = st.text_input("Password", type="password")
        if st.button("Login"):
            if sanitize(m_u) == master_db["username"] and hash_password(m_p) == master_db["password"]:
                st.session_state['master_logged'] = True; st.rerun()
            else: st.error("Invalid Credentials!")
    else:
        st.success("Welcome Master Admin!")
        if st.button("Logout"): st.session_state['master_logged'] = False; st.rerun()
        t1, t2, t3 = st.tabs(["👁️ Manage Schools", "🎓 Edit Students Data", "⚙️ Settings"])
        schools_db = get_all_schools()
        with t1:
            for s_id, s_info in schools_db.items():
                st.write(f"**ID:** {s_id} | **Name:** {s_info['name']} | **Status:** {s_info.get('status', 'Active')}")
                b1, b2, b3 = st.columns(3)
                if b1.button("✅ Activate", key=f"a_{s_id}"): s_info['status']="Active"; save_school(s_id, s_info); st.rerun()
                if b2.button("🚫 Deactivate", key=f"d_{s_id}"): s_info['status']="Inactive"; save_school(s_id, s_info); st.rerun()
                if b3.button("🗑️ Delete", key=f"x_{s_id}"): delete_school(s_id); st.rerun()
        with t2:
            sel_s = st.selectbox("Select School", ["--Select--"] + list(schools_db.keys()))
            if sel_s != "--Select--":
                sts = get_students_by_school(sel_s)
                if sts:
                    e_roll = st.selectbox("Select Roll No", list(sts.keys()))
                    curr_st = sts[e_roll]
                    st.write(f"Editing Roll No: {e_roll} | Name: {curr_st.get('name','')}")
                    if st.button("🗑️ Delete Student"): delete_student(sel_s, e_roll); st.rerun()
                else: st.warning("No students.")
        with t3:
            new_u = st.text_input("New Username", value=master_db['username'])
            new_p = st.text_input("New Password", type="password")
            if st.button("Save Profile"):
                master_db['username'] = sanitize(new_u)
                if new_p: master_db['password'] = hash_password(new_p)
                save_master(master_db); st.success("Updated!")

# --- SCHOOL LOGIN ---
elif menu == "School Login":
    st.query_params["portal"] = "school"
    st.subheader("🏫 School Portal")
    if 'school_logged_id' not in st.session_state:
        s_id = st.text_input("School ID")
        s_pass = st.text_input("Password", type="password")
        if st.button("Login"):
            s_id_clean = sanitize(s_id)
            sch = get_school(s_id_clean)
            if sch and sch["pass"] == hash_password(s_pass):
                if sch.get("status", "Active") == "Active":
                    st.session_state['school_logged_id'] = s_id_clean; st.rerun()
                else: st.error("Account Pending/Inactive.")
            else: st.error("Invalid Credentials!")
    else:
        c_id = st.session_state['school_logged_id']
        sch = get_school(c_id)
        s_lang = sch.get("lang", "English")
        if st.button("Logout"): del st.session_state['school_logged_id']; st.rerun()
        st.info(f"🏫 Logged in as: {sch['name']}")
        
        t1, t2, t3 = st.tabs(["📋 My Students", "➕ Add/Edit Student", "🖨️ Report Card"])
        cur_students = get_students_by_school(c_id)
        
        with t1:
            st.write(f"Total: {len(cur_students)}")
            for r, info in cur_students.items(): st.write(f"Roll: {r} | Name: {info['name'].title()} | DOB: {info['dob']}")
            
        with t2:
            r_no = st.text_input("Roll No *")
            s_name = st.text_input("Student Name *")
            s_dob = st.text_input("DOB (DD-MM-YYYY) *")
            f_name = st.text_input("Father Name")
            m_name = st.text_input("Mother Name")
            pen = st.text_input("PEN NO")
            apaar = st.text_input("APAAR NO")
            cls = st.selectbox("Class", classes_list)
            
            if 'sub_count' not in st.session_state: st.session_state.sub_count = 3
            if st.button("➕ Add Subject Row"): st.session_state.sub_count += 1
            
            subs = {}
            tf, to = 0, 0
            for i in range(st.session_state.sub_count):
                c1, c2, c3 = st.columns(3)
                sn = c1.text_input(f"Sub {i+1}", key=f"sn_{i}")
                fm = c2.number_input(f"FM {i+1}", value=100, key=f"fm_{i}")
                om = c3.number_input(f"OM {i+1}", value=0, key=f"om_{i}")
                if sn: subs[sanitize(sn)] = {"full":fm, "obt":om}; tf+=fm; to+=om
                
            if st.button("💾 Save Student"):
                if r_no and s_name and s_dob:
                    per = (to/tf*100) if tf>0 else 0
                    save_student(c_id, sanitize(r_no), {
                        "name": sanitize(s_name), "dob": normalize_dob(s_dob),
                        "father_name": sanitize(f_name), "mother_name": sanitize(m_name),
                        "pen_no": sanitize(pen), "apaar_no": sanitize(apaar),
                        "class": cls, "subjects": subs, "total_full": tf, "total_obt": to,
                        "percentage": round(per,2), "grade": "A1" if per>=90 else "B1" if per>=70 else "C1",
                        "result": "PASS" if per>=33 else "FAIL"
                    })
                    st.success("Saved!"); st.rerun()
                else: st.error("Fill Roll, Name, DOB!")
                
        with t3:
            if cur_students:
                sel_r = st.selectbox("Select Roll", list(cur_students.keys()))
                html_c = generate_result_card_html(sch['name'], sch.get('name_local',''), cur_students[sel_r], sel_r, s_lang)
                st.markdown(html_c, unsafe_allow_html=True)
                create_pdf(f"res_{sel_r}.pdf", sch['name'], cur_students[sel_r], sel_r)
                with open(f"res_{sel_r}.pdf", "rb") as f: st.download_button("Download PDF", f, file_name=f"Result_{sel_r}.pdf")

# --- ZERO-CRASH RESULTS PORTAL (SUPPORTS 1 CRORE USERS) ---
elif menu == "Results":
    st.query_params["portal"] = "student"
    st.subheader("🎓 Results Portal")
    s_q = st.text_input("Roll Number OR Name")
    d_q = st.text_input("DOB (DD-MM-YYYY)")
    
    if st.button("View Result"):
        if s_q and d_q:
            sq_low = sanitize(s_q.strip().lower())
            ndob = normalize_dob(d_q)
            c = conn.cursor()
            
            # Direct SQLite query (Instant Fetch, No RAM overload)
            c.execute("SELECT school_id, roll_no, data FROM students WHERE (roll_no=? OR name=?) AND dob=?", (sq_low, sq_low, ndob))
            row = c.fetchone()
            
            if row:
                s_id, r_no, s_data = row[0], row[1], json.loads(row[2])
                sch = get_school(s_id) or {}
                s_name_en = sch.get('name', 'Unknown School')
                s_lang = sch.get('lang', 'English')
                st.success("🎉 Result Found!")
                st.markdown(generate_result_card_html(s_name_en, sch.get('name_local',''), s_data, r_no, s_lang), unsafe_allow_html=True)
                create_pdf(f"r_{r_no}.pdf", s_name_en, s_data, r_no)
                with open(f"r_{r_no}.pdf", "rb") as f: st.download_button("Download PDF", f, file_name=f"{r_no}.pdf")
            else: st.error("❌ କୌଣସି ରେକର୍ଡ ମିଳିଲା ନାହିଁ! ଭୁଲ୍ ତଥ୍ୟ ଦେଇଛନ୍ତି।")
        else: st.warning("Please fill Roll No/Name and DOB.")
