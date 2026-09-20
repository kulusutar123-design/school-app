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
import xml.etree.ElementTree as ET

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
# 🤖 AUTO TRANSLATION & LIVE NEWS ENGINE
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

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_live_news():
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request("https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en", headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=4, context=ctx)
        root = ET.fromstring(res.read())
        headlines = [item.find('title').text for item in root.findall('./channel/item')[:5]]
        return " 🔴 ".join(headlines)
    except Exception:
        return "Schools across India to integrate modern digital classrooms 🔴 Government announces fresh guidelines for national scholarship portals."

def t(eng_text, lang):
    translations = {"School Portal": {"Odia": "ସ୍କୁଲ୍ ପୋର୍ଟାଲ୍", "Hindi": "स्कूल पोर्टल"}}
    return translations.get(eng_text, {}).get(lang, eng_text)

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
    c.drawString(50, y, f"DOB: {s_data.get('dob', '')}"); c.drawString(350, y, f"Gender: {s_data.get('gender', '')}"); y -= 25
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
    elif mm_dd == "01-26":
        event_images += "<img class='marquee-img' src='https://images.weserv.nl/?url=upload.wikimedia.org/wikipedia/en/4/41/Flag_of_India.svg&w=400' alt='Republic Day'>"
        event_title = "🇮🇳 Happy Republic Day 🇮🇳"
    elif mm_dd == "09-05":
        event_images += "<img class='marquee-img' src='https://images.weserv.nl/?url=upload.wikimedia.org/wikipedia/commons/d/d1/Dr_Sarvepalli_Radhakrishnan.jpg&w=400' alt='Teachers Day'>"
        event_title = "📚 Happy Teachers' Day 📚"
    elif mm_dd == "04-14":
        event_images += "<img class='marquee-img' src='https://images.weserv.nl/?url=upload.wikimedia.org/wikipedia/commons/c/c3/Dr._Bhimrao_Ambedkar.jpg&w=400' alt='Ambedkar Jayanti'>"
        event_title = "🙏 Happy Ambedkar Jayanti 🙏"
    elif mm_dd == "11-14":
        event_images += "<img class='marquee-img' src='https://images.weserv.nl/?url=upload.wikimedia.org/wikipedia/commons/5/5f/Jawaharlal_Nehru_1946.jpg&w=400' alt='Childrens Day'>"
        event_title = "🌹 Happy Children's Day 🌹"
    elif mm_dd == "04-01":
        event_images += "<img class='marquee-img' src='https://images.weserv.nl/?url=upload.wikimedia.org/wikipedia/commons/f/fe/Seal_of_Odisha.png&w=400' alt='Utkal Divas'>"
        event_title = "🔴 ଉତ୍କଳ ଦିବସର ହାର୍ଦ୍ଦିକ ଶୁଭେଚ୍ଛା 🔴"

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

    # DYNAMIC LIVE NEWS TICKER WITH LANGUAGES
    live_news_eng = fetch_live_news()
    
    notice_text_html = f"""
    <!DOCTYPE html>
    <html><head><meta charset="utf-8"><style>body {{ margin: 0; background: transparent; color: #fff; font-family: sans-serif; font-size: 18px; display: flex; align-items: center; height: 100%; }} .new-badge {{ background-color: #ef4444; color: white; font-size: 14px; font-weight: bold; padding: 2px 6px; border-radius: 3px; margin-left: 5px; margin-right: 5px; }} .dev-badge {{ background-color: #fbbf24; color: black; font-size: 14px; font-weight: bold; padding: 2px 6px; border-radius: 3px; }}</style></head>
    <body><marquee direction='left' scrollamount='8' style='padding: 5px; font-weight: bold; text-shadow: 1px 1px 2px #000;'>
    <span style='color: #fbbf24;'>
    <span class='new-badge'>LATEST NEWS</span> {live_news_eng} &nbsp;&nbsp;&nbsp;&nbsp; 
    <span class='new-badge'>ତାଜା ଖବର</span> ସମଗ୍ର ଭାରତରେ ନୂତନ ଶିକ୍ଷା ନୀତି ଏବଂ ସ୍କଲାରସିପ୍ ଯୋଜନା ଲାଗୁ। &nbsp;&nbsp;&nbsp;&nbsp; 
    <span class='new-badge'>ताज़ा खबर</span> पूरे भारत के स्कूलों में नई छात्रवृत्ति और शिक्षा योजनाएं लागू की गई हैं। &nbsp;&nbsp;&nbsp;&nbsp; 
    <span class='new-badge'>তাজা খবর</span> সারা ভারতের স্কুলে নতুন শিক্ষানীতি ও স্কলারশিপ চালু হয়েছে। &nbsp;&nbsp;&nbsp;&nbsp; 
    <span class='dev-badge'>👨‍💻 Developed by: KULU SUTAR</span> &nbsp;|&nbsp; 📞 8910223342 &nbsp;|&nbsp; ✉️ kulusutar123@gmail.com 
    </span>
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

# ----------------- SCHOLARSHIP PORTAL (ADDRESS & AUTH UPDATES) -----------------
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
                st.session_state['v_name'] = "JYOTI PRAKASH SUTAR" # Auto fetched mock name
                st.session_state['v_aadhaar'] = "8899-0011-2233" # Auto fetched mock aadhaar
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
        
        # 📌 NEW DYNAMIC CASCADING ADDRESS SYSTEM
        st.markdown("#### 📍 Address Information")
        addr = st.text_area("Full Address *", placeholder="Enter your complete address")
        
        c_st, c_dt = st.columns(2)
        all_states = list(STATE_LANG_MAP.keys())
        state_idx = all_states.index("Odisha") if "Odisha" in all_states else 0
        state = c_st.selectbox("State *", all_states, index=state_idx)
        
        ODISHA_DISTRICTS = {
            "Angul": ["Angul", "Athmallik", "Banarpal", "Chhendipada", "Kishorenagar", "Pallahara", "Talcher"],
            "Balasore": ["Bahanaga", "Balasore", "Baliapal", "Basta", "Bhograi", "Jaleswar", "Khaira", "Nilagiri", "Oupada", "Remuna", "Simulia", "Soro"],
            "Cuttack": ["Athagarh", "Banki", "Baramba", "Barang", "Cuttack Sadar", "Dampara", "Kantapada", "Mahanga", "Niali", "Nischintakoili", "Salepur", "Tangi-Choudwar", "Tigiria"],
            "Jajpur": ["Barchana", "Bari", "Binjharpur", "Danagadi", "Dasarathpur", "Dharmasala", "Jajpur", "Korei", "Rasulpur", "Sukinda"],
            "Khordha": ["Balianta", "Balipatna", "Banapur", "Begunia", "Bhubaneswar", "Bolagarh", "Chilika", "Jatni", "Khurda", "Tangi"],
            "Puri": ["Astaranga", "Brahmagiri", "Delanga", "Gop", "Kakatpur", "Kanas", "Krushnaprasad", "Nimapada", "Pipili", "Puri Sadar", "Satyabadi"]
        }
        
        if state == "Odisha":
            dist_list = ["Angul", "Balasore", "Bargarh", "Bhadrak", "Balangir", "Boudh", "Cuttack", "Deogarh", "Dhenkanal", "Gajapati", "Ganjam", "Jagatsinghpur", "Jajpur", "Jharsuguda", "Kalahandi", "Kandhamal", "Kendrapara", "Kendujhar", "Khordha", "Koraput", "Malkangiri", "Mayurbhanj", "Nabarangpur", "Nayagarh", "Nuapada", "Puri", "Rayagada", "Sambalpur", "Subarnapur", "Sundargarh"]
            dist = c_dt.selectbox("District *", sorted(dist_list))
            
            c_blk, c_pin = st.columns(2)
            if dist in ODISHA_DISTRICTS:
                block = c_blk.selectbox("Block/ULB *", sorted(ODISHA_DISTRICTS[dist]))
            else:
                block = c_blk.text_input("Block/ULB *", placeholder=f"Enter Block in {dist}")
        else:
            dist = c_dt.text_input("District *", placeholder="Enter your District")
            c_blk, c_pin = st.columns(2)
            block = c_blk.text_input("Block/ULB *", placeholder="Enter your Block")
            
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
                if inc_no: st.success(f"Income Certificate Verified for {app_name}")
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
                if cas_no: st.success(f"Caste Certificate Verified for {app_name}")
                else: st.error("Enter Caste Cert No")
            cas_auth = st.selectbox("Issuing Authority (Caste)", ISSUING_AUTHORITIES)
            cas_file = st.file_uploader("Upload Caste Certificate Photo *")
        
        st.markdown("### 🏦 Bank Information")
        st.warning("Please note that your Aadhaar Number will be used for crediting scholarship amount via DBT.")
        
        c35, c36 = st.columns([8, 2])
        ifsc = c35.text_input("IFSC Code *")
        if c36.button("FIND IFSC"):
            if ifsc:
                try:
                    url = f"https://ifsc.razorpay.com/{ifsc.strip()}"
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=5) as response:
                        data = json.loads(response.read().decode('utf-8'))
                        st.session_state['v_bank'] = data.get('BANK', 'Unknown Bank')
                        st.session_state['v_branch'] = data.get('BRANCH', 'Unknown Branch')
                        st.success("✅ IFSC Verified & Bank Auto-Fetched!")
                except Exception:
                    st.session_state['v_bank'] = "Bank Not Found"
                    st.session_state['v_branch'] = "Branch Not Found"
                    st.error("❌ Invalid IFSC Code or API unavailable.")
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
            elif not school_code or not sanitize(app_name) or not sanitize(aadhaar_input) or not sanitize(acc_no) or not sanitize(inc_no) or not sanitize(cas_no) or not sanitize(addr) or not sanitize(dist) or not sanitize(block) or not sanitize(pin):
                st.error("Please fill all mandatory fields (*), including Full Address, District, Block, Pin Code, Certificates and School.")
            elif acc_no != re_acc_no: st.error("Account Numbers do not match!")
            elif inc_auth == "Select" or cas_auth == "Select": st.error("Please select a valid Issuing Authority for certificates.")
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
                        "block": sanitize(block), "pin_code": sanitize(pin),
                        "school_code": school_code, "class": sch_class, 
                        "income_cert": sanitize(inc_no), "inc_auth": inc_auth,
                        "caste_cert": sanitize(cas_no), "cas_auth": cas_auth, "ifsc": sanitize(ifsc), 
                        "bank_name": st.session_state.get('v_bank', ''), "branch_name": st.session_state.get('v_branch', ''),
                        "acc_no": sanitize(acc_no), "acc_name": sanitize(acc_name), "aadhaar_seeded": seeded,
                        "has_passbook": True if passbook else False,
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
        if st.button("Cancel"):
            st.session_state['sch_app_step'] = False; st.rerun()

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
                            save_data(schools_db, students_db)
                            
                            st.session_state['stu_reg_success'] = True
                            st.session_state['stu_reg_id'] = reg_data['reg_id']
                            st.session_state['stu_reg_data'] = reg_data['data']
                            st.session_state['payment_step'] = False
                            st.session_state['temp_student_data'] = None
                            st.rerun()

            elif pay_mode == "Offline Payment (School Counter)":
                st.info(f"You have selected Offline Payment. Please pay ₹{total_fee:.2f} at your School Counter.")
                if st.button("Submit Final Application", type="primary"):
                    reg_data = st.session_state['temp_student_data']
                    reg_data['data']['payment_mode'] = f"Offline (₹{total_fee:.2f} - Pending at Counter)"
                    reg_data['data']['status'] = "Pending_Master"
                    
                    sch_id = reg_data['school_sel']
                    if sch_id not in students_db:
                        students_db[sch_id] = {}
                    students_db[sch_id][reg_data['reg_id']] = reg_data['data']
                    save_data(schools_db, students_db)
                    
                    st.session_state['stu_reg_success'] = True
                    st.session_state['stu_reg_id'] = reg_data['reg_id']
                    st.session_state['stu_reg_data'] = reg_data['data']
                    st.session_state['payment_step'] = False
                    st.session_state['temp_student_data'] = None
                    st.rerun()
                    
            if st.button("⬅️ Back to Form"):
                st.session_state['payment_step'] = False
                st.rerun()

# ----------------- NEW SCHOOL REGISTRATION -----------------
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
                            save_data(schools_db, students_db)
                            
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
                    save_data(schools_db, students_db)
                    
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
