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
    "Select",
    "District Magistrate / Collector",
    "Additional District Magistrate",
    "Sub-divisional Magistrate / Sub-divisional Officer",
    "Executive Magistrates",
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
def create_scholarship_pdf(filename, app_id, s_data):
    c = canvas.Canvas(filename, pagesize=letter)
    c.setStrokeColorRGB(0.1, 0.4, 0.2); c.setLineWidth(4); c.rect(30, 30, 552, 732, stroke=1, fill=0)
    c.setFillColorRGB(0.1, 0.4, 0.2); c.setFont("Times-Bold", 20); c.drawCentredString(300, 710, "SCHOLARSHIP APPLICATION RECEIPT")
    c.setFillColorRGB(0, 0, 0); c.setFont("Helvetica-Bold", 12); c.drawString(50, 670, f"APPLICATION ID: {app_id}")
    c.setFont("Helvetica", 11); y = 640
    c.drawString(50, y, f"Applicant Name: {s_data.get('app_name', '').upper()}"); c.drawString(350, y, f"OTR No: {s_data.get('otr', '')}"); y -= 25
    c.drawString(50, y, f"Aadhaar No: {s_data.get('aadhaar', '')}"); c.drawString(350, y, f"Category: {s_data.get('category', '')}"); y -= 25
    c.drawString(50, y, f"DOB: {s_data.get('dob', '')}"); c.drawString(350, y, f"Gender: {s_data.get('gender', '')}"); y -= 25
    c.drawString(50, y, f"Phone: {s_data.get('mobile', '')}"); c.drawString(350, y, f"School Code: {s_data.get('school_code', '')}"); y -= 35
    c.setStrokeColorRGB(0.8, 0.8, 0.8); c.line(50, y, 550, y); y -= 20
    c.setFont("Helvetica-Bold", 12); c.drawString(50, y, "Certificate & Institute Info"); c.setFont("Helvetica", 11); y -= 20
    c.drawString(50, y, f"Class: {s_data.get('class', '')}"); c.drawString(350, y, f"Income Cert: {s_data.get('income_cert', '')}"); y -= 25
    c.drawString(50, y, f"Caste Cert: {s_data.get('caste_cert', '')}"); y -= 35
    c.setStrokeColorRGB(0.8, 0.8, 0.8); c.line(50, y, 550, y); y -= 20
    c.setFont("Helvetica-Bold", 12); c.drawString(50, y, "Payment & Status"); c.setFont("Helvetica", 11); y -= 20
    c.drawString(50, y, f"Payment Mode: {s_data.get('payment_mode', 'N/A')}"); y -= 25
    c.drawString(50, y, f"Current Status: {s_data.get('status', 'Pending_Master')}"); y -= 40
    c.line(50, y, 550, y); y -= 20
    c.setFont("Helvetica-Oblique", 10); c.drawCentredString(300, y, "Computer-generated receipt. Keep for future reference.")
    try: bc = code128.Code128(str(app_id), barHeight=30, barWidth=1.5); bc.drawOn(c, 50, 40)
    except: pass
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

# ----------------- HOME PAGE (DYNAMIC UI WITH GUARANTEED PHOTO RUNNING) -----------------
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
    .login-card {{ background: rgba(255, 255, 255, 0.95) !important; border: 1px solid #cbd5e1; border-bottom: 5px solid #fbbf24; border-radius: 8px; padding: 25px; margin-bottom: 20px; text-align: center; text-decoration: none; display: block; color: #1e3a8a !important; box-shadow: 0 4px 6px rgba(0,0,0,0.05); transition: 0.3s; }}
    .login-card:hover {{ background: #ffffff !important; border-bottom: 5px solid #1e3a8a; transform: translateY(-3px); box-shadow: 0 8px 15px rgba(0,0,0,0.2); }}
    .login-title {{ font-size: 24px; font-weight: bold; margin-bottom: 8px; color: #1e3a8a !important;}}
    .login-sub {{ font-size: 15px; color: #64748b !important;}}
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
    .marquee-img {{ height: 260px; border-radius: 10px; margin-right: 20px; object-fit: contain; display: inline-block; vertical-align: middle; margin-top: 15px; border: 2px solid #fbbf24; background-color: #fff; padding: 5px; }}
    .carousel-overlay {{ position: absolute; bottom: 0; background: rgba(30,58,138,0.9); width: 100%; color: white; text-align: center; padding: 12px; font-weight: bold; font-size: 20px; letter-spacing: 1px; box-sizing: border-box; }}
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

    st.markdown(f"<div class='glass-panel'><h2 style='text-align: center; color: #fbbf24; margin-top: 0;'>🏫 {event_title}</h2>", unsafe_allow_html=True)
    components.html(carousel_html, height=360)
    st.markdown("</div>", unsafe_allow_html=True)

    notice_text_html = """
    <!DOCTYPE html>
    <html><head><meta charset="utf-8"><style>body { margin: 0; background: transparent; color: #fff; font-family: sans-serif; font-size: 18px; display: flex; align-items: center; height: 100%; } .new-badge { background-color: #fbbf24; color: black; font-size: 14px; font-weight: bold; padding: 2px 6px; border-radius: 3px; margin-left: 5px; }</style></head>
    <body><marquee direction='left' scrollamount='8' style='padding: 5px; font-weight: bold;'>
    <span style='color: #fbbf24;'>📢 ନୂଆ ଅପଡେଟ୍: ଛାତ୍ରଛାତ୍ରୀମାନେ ଏବେ ଅନଲାଇନ୍ ସ୍କଲାରସିପ୍ ଏବଂ ପେମେଣ୍ଟ କରିପାରିବେ! <span class='new-badge'>NEW</span> &nbsp;&nbsp;|&nbsp;&nbsp; 👨‍💻 Software Developed by: KULU SUTAR &nbsp;&nbsp;|&nbsp;&nbsp; 📞 Helpdesk No: 8910223342 &nbsp;&nbsp;|&nbsp;&nbsp; ✉️ Mail ID: kulusutar123@gmail.com </span>
    </marquee></body></html>
    """
    st.markdown("<div class='glass-panel' style='padding: 10px;'>", unsafe_allow_html=True)
    components.html(notice_text_html, height=45)
    st.markdown("</div>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown("<a href='?portal=scholarship' target='_self' class='login-card' style='border-bottom: 5px solid #10b981;'><div class='login-title'>💰 Scholarship</div><div class='login-sub'>Apply Now</div></a>", unsafe_allow_html=True)
    with c2: st.markdown("<a href='?portal=reg_student' target='_self' class='login-card'><div class='login-title'>👨‍🎓 New Student</div><div class='login-sub'>Apply for admission</div></a>", unsafe_allow_html=True)
    with c3: st.markdown("<a href='?portal=reg_school' target='_self' class='login-card'><div class='login-title'>🏫 New School</div><div class='login-sub'>Register institution</div></a>", unsafe_allow_html=True)
    with c4: st.markdown("<a href='?portal=master' target='_self' class='login-card'><div class='login-title'>🏛️ Master Login</div><div class='login-sub'>Admin Portal</div></a>", unsafe_allow_html=True)

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
        st.info("Please provide your OTR number from National Scholarship Portal.")
        
        col_o1, col_o2 = st.columns([8, 2])
        otr_input = col_o1.text_input("OTR No. *", key="otr_inp")
        if col_o2.button("VERIFY OTR"):
            if otr_input: 
                st.session_state['otr_verified'] = True
                st.success("OTR Verified Successfully! Fill the form below.")
            else: st.error("Please enter OTR No.")
            
        if st.session_state['otr_verified']:
            with st.form("scholarship_form"):
                st.markdown("### Basic Information")
                c1, c2, c3 = st.columns(3)
                ac_year = c1.selectbox("Academic Year", ["2026-27", "2027-28"])
                dept = c2.selectbox("Department", ["ST&SC and MBC Welfare Depart", "Higher Education"])
                scheme = c3.selectbox("Scheme", ["Pre Matric", "Post Matric"])
                
                c4, c5 = st.columns(2)
                app_name = c4.text_input("Applicant Name *")
                category = c5.selectbox("Category *", SOCIAL_CATEGORIES)
                
                c6, c7, c8 = st.columns(3)
                gender = c6.radio("Applicant Gender:", ["Male", "Female", "Transgender"])
                religion = c7.selectbox("Religion", ["Select", "Hindu", "Muslim", "Christian", "Other"])
                photo = c8.file_uploader("Profile Photo (jpg, png)")
                
                c9, c10 = st.columns(2)
                dob = c9.date_input("Date of Birth *", min_value=datetime.date(1990, 1, 1), max_value=datetime.date.today())
                aadhaar = c10.text_input("Aadhaar No. *")
                
                c11, c12 = st.columns(2)
                mob_no = c11.text_input("Student/Parent's Mobile No. *")
                email = c12.text_input("Student/Parent's e-Mail")
                
                st.markdown("---")
                c13, c14, c15 = st.columns(3)
                f_name = c13.text_input("Father's Name *")
                f_edu = c14.selectbox("Father Educational Status", ["Select", "Illiterate", "10th", "Graduate"])
                f_occ = c15.selectbox("Father Occupational Status", ["Select", "Farmer", "Service", "Business"])
                
                c16, c17, c18 = st.columns(3)
                m_name = c16.text_input("Mother's Name *")
                m_edu = c17.selectbox("Mother Educational Status", ["Select", "Illiterate", "10th", "Graduate"])
                m_occ = c18.selectbox("Mother Occupational Status", ["Select", "Housewife", "Service", "Business"])
                
                g_name = st.text_input("Guardian Name")
                
                st.markdown("#### Address Information")
                c19, c20, c21 = st.columns(3)
                dist = c19.text_input("District")
                block = c20.text_input("Block/ULB")
                pin = c21.text_input("Pin Code")
                addr = st.text_area("Address")
                
                st.markdown("### Institute / Course Information")
                active_schools = {k: v for k, v in schools_db.items() if v.get("status", "Active") == "Active"}
                school_options = [f"{k} - {v['name']}" for k, v in active_schools.items()]
                c24, c25 = st.columns(2)
                school_sel_str = c24.selectbox("Institute (School) *", ["--Select--"] + school_options)
                sch_class = c25.selectbox("Class *", ["IX", "X", "XI", "XII"])
                school_code = school_sel_str.split(" - ")[0] if school_sel_str != "--Select--" else None
                
                c26, c27 = st.columns(2)
                adm_no = c26.text_input("School Admission No. *")
                adm_date = c27.date_input("School Admission Date *")
                
                st.markdown("### APAAR ID Information")
                has_apaar = st.radio("Do you have APAAR ID?", ["Yes", "No"])
                apaar_id = st.text_input("APAAR ID") if has_apaar == "Yes" else ""
                
                st.markdown("### Certificate Information")
                c33, c34 = st.columns(2)
                with c33:
                    st.markdown("**Income Certificate**")
                    inc_year = st.selectbox("Issuing Year", CERT_YEARS)
                    inc_no = st.text_input("Income Certificate No. *")
                    inc_token = st.text_input("Token No (Income)")
                    inc_whom = st.selectbox("To Whom Issued", RELATIONSHIPS)
                    inc_auth = st.selectbox("Issuing Authority (Income)", ISSUING_AUTHORITIES)
                    inc_file = st.file_uploader("Upload Income Certificate (PDF/JPG)")
                with c34:
                    st.markdown("**Caste Certificate**")
                    cas_year = st.selectbox("Caste Issuing Year", CERT_YEARS)
                    cas_no = st.text_input("Caste Certificate No. *")
                    cas_token = st.text_input("Token No (Caste)")
                    cas_whom = st.selectbox("To Whom Issued (Caste)", RELATIONSHIPS)
                    cas_auth = st.selectbox("Issuing Authority (Caste)", ISSUING_AUTHORITIES)
                    cas_file = st.file_uploader("Upload Caste Certificate (PDF/JPG)")
                
                st.markdown("### Bank Information")
                st.warning("Please note that your Aadhaar Number will be used for crediting scholarship amount via DBT.")
                c35, c36, c37 = st.columns(3)
                ifsc = c35.text_input("IFSC Code *")
                b_name = c36.text_input("Bank Name")
                b_branch = c37.text_input("Branch Name")
                
                c38, c39, c40 = st.columns(3)
                acc_name = c38.text_input("Account Holder Name *")
                acc_no = c39.text_input("Account Number *", type="password")
                re_acc_no = c40.text_input("Re-type Account No. *")
                
                seeded = st.radio("Whether account number seeded with the Aadhaar number?", ["Yes", "No"])
                passbook = st.file_uploader("Upload Passbook Front Page (max 1MB)")
                
                decl = st.checkbox("✅ I declare the above info is true.")
                
                submit_sch = st.form_submit_button("Proceed to Payment & Submit")
                
                if submit_sch:
                    if not decl: st.error("Please accept the declaration.")
                    elif not school_code or not sanitize(app_name) or not sanitize(aadhaar) or not sanitize(acc_no) or not sanitize(inc_no) or not sanitize(cas_no):
                        st.error("Please fill all mandatory fields (*), including Certificates and School.")
                    elif acc_no != re_acc_no: st.error("Account Numbers do not match!")
                    elif inc_auth == "Select" or cas_auth == "Select": st.error("Please select a valid Issuing Authority for certificates.")
                    else:
                        app_id = "SCH" + str(random.randint(1000000, 9999999))
                        st.session_state['temp_sch_data'] = {
                            "app_id": app_id,
                            "data": {
                                "academic_year": ac_year, "scheme": scheme, "app_name": sanitize(app_name),
                                "category": category, "otr": sanitize(otr_input), "gender": gender,
                                "dob": str(dob), "aadhaar": sanitize(aadhaar), "mobile": sanitize(mob_no),
                                "father_name": sanitize(f_name), "mother_name": sanitize(m_name),
                                "school_code": school_code, "class": sch_class, "admission_no": sanitize(adm_no),
                                "apaar_id": sanitize(apaar_id), "income_cert": sanitize(inc_no), "inc_auth": inc_auth,
                                "caste_cert": sanitize(cas_no), "cas_auth": cas_auth, "ifsc": sanitize(ifsc), 
                                "acc_no": sanitize(acc_no), "status": "Pending_Master", "payment_mode": "Pending", "fee": sch_fee
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
        if st.button("Cancel"):
            st.session_state['sch_app_step'] = False; st.rerun()

# ----------------- MASTER LOGIN -----------------
elif menu == "Master Login":
    c_home, c_title = st.columns([1, 8])
    with c_home:
        if st.button("🏠 Home", key="m_home_btn"):
            st.query_params["portal"] = "home"
            st.rerun()
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
                if status == "Pending_Master_Approval": continue 
                st.markdown(f"<div style='border:1px solid #cbd5e1; padding:10px; margin-bottom:10px;'><b>{s_id}</b> | {s_info['name']} | Status: {status}</div>", unsafe_allow_html=True)

        with t2:
            st.markdown("### 💳 Verify Registrations")
            st.info("School and Student Admissions verification logic goes here.")

        with t3:
            st.markdown("### 🎓 Scholarship Verifications (Master)")
            pending_sch = {k: v for k, v in scholarships_db.items() if v.get("status") == "Pending_Master"}
            if pending_sch:
                app_id = st.selectbox("Select Pending Scholarship to Verify", list(pending_sch.keys()))
                s_data = pending_sch[app_id]
                
                st.write(f"Payment Mode: **{s_data.get('payment_mode')}**")
                
                with st.expander("Edit & Verify Data"):
                    e_name = st.text_input("Applicant Name", s_data.get('app_name', ''))
                    e_aadhaar = st.text_input("Aadhaar No", s_data.get('aadhaar', ''))
                    e_inc = st.text_input("Income Cert", s_data.get('income_cert', ''))
                    e_cas = st.text_input("Caste Cert", s_data.get('caste_cert', ''))
                    e_acc = st.text_input("Account No", s_data.get('acc_no', ''))
                    
                    if st.button("✅ Update & Forward to School", type="primary"):
                        s_data['app_name'] = sanitize(e_name)
                        s_data['aadhaar'] = sanitize(e_aadhaar)
                        s_data['income_cert'] = sanitize(e_inc)
                        s_data['caste_cert'] = sanitize(e_cas)
                        s_data['acc_no'] = sanitize(e_acc)
                        s_data['status'] = "Pending_School"
                        
                        scholarships_db[app_id] = s_data
                        save_scholarships(scholarships_db)
                        st.success(f"Scholarship {app_id} verified and sent to school!")
                        st.rerun()
                        
                    if st.button("🚫 Reject Application"):
                        s_data['status'] = "Rejected_Refund"
                        scholarships_db[app_id] = s_data
                        save_scholarships(scholarships_db)
                        st.error("Rejected.")
                        st.rerun()
            else:
                st.success("No pending scholarships.")

        with t4: st.markdown("### 🎓 Edit Students Data")
        with t5: st.markdown("### ⚙️ Settings")

# ----------------- SCHOOL LOGIN -----------------
elif menu == "School Login":
    c_home, c_title = st.columns([1, 8])
    with c_home:
        if st.button("🏠 Home", key="s_home_btn"): st.query_params["portal"] = "home"; st.rerun()
    with c_title: st.subheader("🏫 School Portal")
    
    if 'school_logged_id' not in st.session_state:
        s_id = st.text_input("School ID")
        s_pass = st.text_input("School Password", type="password")
        if st.button("Login as School"):
            s_id_clean = sanitize(s_id)
            if s_id_clean in schools_db and schools_db[s_id_clean]["pass"] == s_pass:
                st.session_state['school_logged_id'] = s_id_clean; st.rerun()
            else: st.error("❌ Invalid ID/Password!")
    else: 
        cur_school = st.session_state['school_logged_id']
        c1, c2 = st.columns([8, 2])
        c1.info(f"🏫 **School Portal** | ID: {cur_school} | {schools_db[cur_school]['name']}")
        if c2.button("🔴 Logout"): del st.session_state['school_logged_id']; st.rerun()

        t1, t2, t3, t4 = st.tabs(["📋 My Students", "✅ Registrations", "🎓 Scholarship Approvals", "🖨️ Report Card"])
        
        with t3:
            st.markdown("### 🎓 Scholarship Approvals")
            sch_list = {k: v for k, v in scholarships_db.items() if v.get("status") == "Pending_School" and v.get("school_code") == cur_school}
            if sch_list:
                a_id = st.selectbox("Select Application", list(sch_list.keys()))
                a_data = sch_list[a_id]
                st.write(f"Applicant: **{a_data.get('app_name')}** | Class: **{a_data.get('class')}**")
                
                if st.button("✅ Final Approve Scholarship", type="primary"):
                    a_data["status"] = "Approved"
                    scholarships_db[a_id] = a_data
                    save_scholarships(scholarships_db)
                    st.success("Approved successfully!")
                    st.rerun()
            else:
                st.success("No pending scholarships for your school.")

# ----------------- RESULTS PORTAL -----------------
elif menu == "Results":
    c_home, c_title = st.columns([1, 8])
    with c_home:
        if st.button("🏠 Home", key="st_home_btn"): st.query_params["portal"] = "home"; st.rerun()
    with c_title: st.subheader("🎓 Results Portal")
    st.info("Search Results Here.")

st.markdown("---")
st.markdown("<div style='text-align: center; padding: 15px; background: linear-gradient(90deg, #1e3a8a, #9333ea); color: white; border-radius: 8px; font-weight: bold;'>👨‍💻 Software Developed by: KULU SUTAR | 📞 Mob: 8910223342 | ✉️ kulusutar123@gmail.com</div>", unsafe_allow_html=True)
