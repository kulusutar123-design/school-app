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

# ==========================================
# 🌐 APP URL SETTING
# ==========================================
APP_URL = "http://localhost:8501"

# ପେଜ୍ ସେଟିଂ
st.set_page_config(page_title="Advanced School Management System", layout="centered")

# --- HIDE STREAMLIT DEFAULT MENU & HEADER ---
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
# 🗣️ MULTI-LANGUAGE TRANSLATION ENGINE
# ==========================================
def t(eng_text, lang):
    translations = {
        # School Portal UI
        "School Portal": {
            "Odia": "ସ୍କୁଲ୍ ପୋର୍ଟାଲ୍", "Hindi": "स्कूल पोर्टल", "Bengali": "স্কুল পোর্টাল", 
            "Telugu": "పాఠశాల పోర్టల్", "Tamil": "பள்ளி போர்டல்", "Marathi": "शाळा पोर्टल", "Gujarati": "શાળા પોર્ટલ"
        },
        "Logout": {
            "Odia": "ଲଗ୍ ଆଉଟ୍", "Hindi": "लॉग आउट", "Bengali": "লগ আউট", 
            "Telugu": "లాగ్ అవుట్", "Tamil": "வெளியேறு", "Marathi": "लॉग आउट", "Gujarati": "લૉગ આઉટ"
        },
        "My Students": {
            "Odia": "ମୋର ଛାତ୍ରଛାତ୍ରୀ", "Hindi": "मेरे छात्र", "Bengali": "আমার ছাত্র",
            "Telugu": "నా విద్యార్థులు", "Tamil": "என் மாணவர்கள்", "Marathi": "माझे विद्यार्थी", "Gujarati": "મારા વિદ્યાર્થીઓ"
        },
        "Add Student": {
            "Odia": "ନୂଆ ଛାତ୍ର ଯୋଡନ୍ତୁ", "Hindi": "नया छात्र जोड़ें", "Bengali": "নতুন ছাত্র যোগ করুন",
            "Telugu": "కొత్త విద్యార్థిని జోడించండి", "Tamil": "புதிய மாணவரைச் சேர்க்கவும்", "Marathi": "नवीन विद्यार्थी जोडा", "Gujarati": "નવો વિદ્યાર્થી ઉમેરો"
        },
        "Edit Student": {
            "Odia": "ଛାତ୍ର ତଥ୍ୟ ବଦଳାନ୍ତୁ", "Hindi": "छात्र विवरण बदलें", "Bengali": "তথ্য আপডেট করুন",
            "Telugu": "విద్యార్థి సమాచారం నవీకరించండి", "Tamil": "மாணவர் விவரங்களை புதுப்பிக்கவும்", "Marathi": "विद्यार्थी माहिती अपडेट करा", "Gujarati": "વિદ્યાર્થી માહિતી અપડેટ કરો"
        },
        "Report Card": {
            "Odia": "ରିପୋର୍ଟ କାର୍ଡ ପ୍ରିଣ୍ଟ୍", "Hindi": "रिपोर्ट कार्ड", "Bengali": "রিপোর্ট কার্ড",
            "Telugu": "రిపోర్ట్ కార్డ్", "Tamil": "மதிப்பெண் அட்டை", "Marathi": "रिपोर्ट कार्ड", "Gujarati": "રિપોર્ટ કાર્ડ"
        },
        "Search": {
            "Odia": "ନାମ କିମ୍ବା ରୋଲ୍ ନମ୍ବର ଦେଇ ଖୋଜନ୍ତୁ", "Hindi": "नाम या रोल नंबर से खोजें", "Bengali": "নাম বা রোল নম্বর দিয়ে খুঁজুন",
            "Telugu": "పేరు లేదా రోల్ నంబర్ ద్వారా శోధించండి", "Tamil": "பெயர் அல்லது பதிவு எண் மூலம் தேடவும்", "Marathi": "नाव किंवा रोल नंबरने शोधा", "Gujarati": "નામ અથવા રોલ નંબર દ્વારા શોધો"
        },
        "Total Registered": {
            "Odia": "ମୋଟ ପଞ୍ଜିକୃତ:", "Hindi": "कुल पंजीकृत:", "Bengali": "মোট নিবন্ধিত:",
            "Telugu": "మొత్తం నమోదైనవి:", "Tamil": "மொத்தம் பதிவு செய்யப்பட்டவை:", "Marathi": "एकूण नोंदणीकृत:", "Gujarati": "કુલ નોંધાયેલ:"
        },
        
        # Certificate Labels
        "ANNUAL EXAMINATION": {
            "Odia": "ବାର୍ଷିକ ପରୀକ୍ଷା", "Hindi": "वार्षिक परीक्षा", "Bengali": "বার্ষিক পরীক্ষা",
            "Telugu": "వార్షిక పరీక్ష", "Tamil": "ஆண்டுத் தேர்வு", "Marathi": "वार्षिक परीक्षा", "Gujarati": "વાર્ષિક પરીક્ષા"
        },
        "CERTIFICATE-CUM-MARK SHEET": {
            "Odia": "ପ୍ରମାଣପତ୍ର ଏବଂ ମାର୍କସିଟ୍", "Hindi": "प्रमाणपत्र सह अंकतालिका", "Bengali": "শংসাপত্র এবং মার্কশিট",
            "Telugu": "ధృవీకరణ పత్రం మరియు మార్కుల జాబితా", "Tamil": "சான்றிதழ் மற்றும் மதிப்பெண் பட்டியல்", "Marathi": "प्रमाणपत्र आणि गुणपत्रिका", "Gujarati": "પ્રમાણપત્ર અને ગુણપત્રક"
        },
        "ROLL NO": {
            "Odia": "ରୋଲ୍ ନମ୍ବର", "Hindi": "रोल नंबर", "Bengali": "রোল নম্বর",
            "Telugu": "రోల్ నంబర్", "Tamil": "பதிவு எண்", "Marathi": "रोल नंबर", "Gujarati": "રોલ નંબર"
        },
        "CLASS": {
            "Odia": "ଶ୍ରେଣୀ", "Hindi": "कक्षा", "Bengali": "শ্রেণী",
            "Telugu": "తరగతి", "Tamil": "வகுப்பு", "Marathi": "वर्ग", "Gujarati": "ધોરણ"
        },
        "PEN NO": {
            "Odia": "ପେନ୍ ନମ୍ବର", "Hindi": "पेन नं.", "Bengali": "পেন নং",
            "Telugu": "పెన్ నం.", "Tamil": "பென் எண்", "Marathi": "पेन क्र.", "Gujarati": "પેન નં."
        },
        "APAAR NO": {
            "Odia": "ଅପାର୍ ନମ୍ବର", "Hindi": "अपार नं.", "Bengali": "অপার নং",
            "Telugu": "అపార్ నం.", "Tamil": "அபார் எண்", "Marathi": "अपार क्र.", "Gujarati": "અપાર નં."
        },
        "NAME": {
            "Odia": "ଛାତ୍ର/ଛାତ୍ରୀଙ୍କ ନାମ", "Hindi": "छात्र का नाम", "Bengali": "ছাত্রের নাম",
            "Telugu": "విద్యార్థి పేరు", "Tamil": "மாணவர் பெயர்", "Marathi": "विद्यार्थ्याचे नाव", "Gujarati": "વિદ્યાર્થીનું નામ"
        },
        "MOTHER'S NAME": {
            "Odia": "ମାତାଙ୍କ ନାମ", "Hindi": "माता का नाम", "Bengali": "মাতার নাম",
            "Telugu": "తల్లి పేరు", "Tamil": "தாயின் பெயர்", "Marathi": "आईचे नाव", "Gujarati": "માતાનું નામ"
        },
        "FATHER'S NAME": {
            "Odia": "ପିତାଙ୍କ ନାମ", "Hindi": "पिता का नाम", "Bengali": "পিতার নাম",
            "Telugu": "తండ్రి పేరు", "Tamil": "தந்தையின் பெயர்", "Marathi": "वडिलांचे नाव", "Gujarati": "પિતાનું નામ"
        },
        "DOB": {
            "Odia": "ଜନ୍ମ ତାରିଖ", "Hindi": "जन्म तिथि", "Bengali": "জন্ম তারিখ",
            "Telugu": "పుట్టిన తేదీ", "Tamil": "பிறந்த தேதி", "Marathi": "जन्म तारीख", "Gujarati": "જન્મ તારીખ"
        },
        "PASSED_TEXT": {
            "Odia": "ଉପରୋକ୍ତ ବ୍ୟାଚରେ ଅନୁଷ୍ଠିତ ବାର୍ଷିକ ପରୀକ୍ଷାରେ ଉତ୍ତୀର୍ଣ୍ଣ ହୋଇଛନ୍ତି।",
            "Hindi": "उपरोक्त शैक्षणिक सत्र में आयोजित वार्षिक परीक्षा सफलतापूर्वक उत्तीर्ण की है।",
            "Bengali": "উপরে উল্লেখিত ব্যাচে অনুষ্ঠিত বার্ষিক পরীক্ষায় সফলভাবে উত্তীর্ণ হয়েছে।",
            "Telugu": "పైన పేర్కొన్న విద్యా సంవత్సరంలో నిర్వహించిన వార్షిక పరీక్షలో ఉత్తీర్ణులయ్యారు.",
            "Tamil": "மேற்கண்ட கல்வி ஆண்டில் நடைபெற்ற ஆண்டுத் தேர்வில் தேர்ச்சி பெற்றுள்ளார்.",
            "Marathi": "शैक्षणिक सत्रात घेण्यात आलेली वार्षिक परीक्षा यशस्वीरित्या उत्तीर्ण केली आहे.",
            "Gujarati": "ઉપરોક્ત શૈક્ષણિક સત્રમાં લેવાયેલ વાર્ષિક પરીક્ષા સફળતાપૂર્વક પાસ કરેલ છે."
        },
        "SUBJECT": {
            "Odia": "ବିଷୟ", "Hindi": "विषय", "Bengali": "বিষয়",
            "Telugu": "విషయం", "Tamil": "பாடம்", "Marathi": "विषय", "Gujarati": "વિષય"
        },
        "FULL MARKS": {
            "Odia": "ମୋଟ ନମ୍ବର", "Hindi": "पूर्णांक", "Bengali": "পূর্ণমান",
            "Telugu": "గరిష్ట మార్కులు", "Tamil": "மொத்த மதிப்பெண்கள்", "Marathi": "एकूण गुण", "Gujarati": "કુલ ગુણ"
        },
        "MARKS SECURED": {
            "Odia": "ପ୍ରାପ୍ତ ନମ୍ବର", "Hindi": "प्राप्तांक", "Bengali": "প্রাপ্ত নম্বর",
            "Telugu": "పొందిన మార్కులు", "Tamil": "பெற்ற மதிப்பெண்கள்", "Marathi": "मिळालेले गुण", "Gujarati": "મેળવેલ ગુણ"
        },
        "TOTAL MARKS": {
            "Odia": "ସମୁଦାୟ ନମ୍ବର", "Hindi": "कुल प्राप्तांक", "Bengali": "মোট প্রাপ্ত নম্বর",
            "Telugu": "మొత్తం మార్కులు", "Tamil": "மொத்த மதிப்பெண்", "Marathi": "एकूण प्राप्त गुण", "Gujarati": "કુલ મેળવેલ ગુણ"
        },
        "GRADE": {
            "Odia": "ଗ୍ରେଡ୍", "Hindi": "ग्रेड", "Bengali": "গ্রেড",
            "Telugu": "గ్రేడ్", "Tamil": "தரம்", "Marathi": "श्रेणी", "Gujarati": "ગ્રેડ"
        },
        "DATE OF PUBLICATION": {
            "Odia": "ଫଳାଫଳ ପ୍ରକାଶନ ତାରିଖ", "Hindi": "परिणाम प्रकाशन तिथि", "Bengali": "ফলাফল প্রকাশের তারিখ",
            "Telugu": "ఫలితాల ప్రకటన తేదీ", "Tamil": "முடிவுகள் வெளியான தேதி", "Marathi": "निकाल जाहीर झाल्याची तारीख", "Gujarati": "પરિણામ જાહેર થયાની તારીખ"
        },
        "HM SIGNATURE": {
            "Odia": "ପ୍ରଧାନ ଶିକ୍ଷକଙ୍କ ଦସ୍ତଖତ", "Hindi": "प्रधानाचार्य के हस्ताक्षर", "Bengali": "প্রধান শিক্ষকের স্বাক্ষর",
            "Telugu": "ప్రధానోపాధ్యాయుని సంతకం", "Tamil": "தலைமை ஆசிரியர் கையொப்பம்", "Marathi": "मुख्याध्यापकांची स्वाक्षरी", "Gujarati": "આચાર્યની સહી"
        },
        "CLASS TEACHER SIGNATURE": {
            "Odia": "ଶ୍ରେଣୀ ଶିକ୍ଷକଙ୍କ ଦସ୍ତଖତ", "Hindi": "कक्षा अध्यापक के हस्ताक्षर", "Bengali": "শ্রেণী শিক্ষকের স্বাক্ষর",
            "Telugu": "తరగతి ఉపాధ్యాయుని సంతకం", "Tamil": "வகுப்பு ஆசிரியர் கையொப்பம்", "Marathi": "वर्ग शिक्षकांची स्वाक्षरी", "Gujarati": "વર્ગ શિક્ષકની સહી"
        }
    }
    return translations.get(eng_text, {}).get(lang, eng_text)

# --- Number to Words Converter ---
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

# --- ଡାଟା ଲୋଡ୍ ଓ ସେଭ୍ ଫଙ୍କସନ୍ ---
def load_master_data():
    default_master = {"username": "master", "password": "master123", "email": "admin@school.com", "phone": "9999999999"}
    if os.path.exists(MASTER_FILE):
        try:
            with open(MASTER_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if content.strip():
                    return json.loads(content)
        except Exception:
            pass
    return default_master

def save_master_data(data):
    with open(MASTER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def load_data():
    schools = {"S001": {"name": "LAXMI NARAYAN GIRLS HIGH SCHOOL, BANASAR KALYANI", "pass": "admin123", "state": "Odisha", "lang": "Odia"}}
    students = {}
    
    if os.path.exists(SCHOOLS_FILE):
        try:
            with open(SCHOOLS_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if content.strip():
                    schools = json.loads(content)
        except Exception:
            pass
            
    if os.path.exists(STUDENTS_FILE):
        try:
            with open(STUDENTS_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if content.strip():
                    students = json.loads(content)
        except Exception:
            pass
            
    return schools, students

def save_data(schools, students):
    with open(SCHOOLS_FILE, "w", encoding="utf-8") as f:
        json.dump(schools, f, indent=4)
    with open(STUDENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(students, f, indent=4)

# --- ସୁନ୍ଦର ରାଙ୍କ୍ କାର୍ଡ HTML ଡିଜାଇନ୍ (BILINGUAL AUTO-CONVERT) ---
def generate_result_card_html(school_name, st_data, roll_no, s_lang):
    raw_dob = st_data.get('dob', '')
    disp_dob = raw_dob
    if len(raw_dob.split('-')) == 3:
        y, m, d = raw_dob.split('-')
        if len(y) == 4:
            disp_dob = f"{d}-{m}-{y}"

    bg_color = "#fef9f7"
    border_color = "#963f98"
    outer_border = "#ce9bd0"
    table_bg = "#fcf4fc"
    
    total_obt = st_data.get('total_obt', 0)
    words_total = number_to_words(total_obt)

    student_name = st_data.get('name', 'N/A').upper()
    total_marks = f"{total_obt}/{st_data.get('total_full', 0)}"
    grade = st_data.get('grade', 'N/A')
    result_stat = st_data.get('result', 'N/A')
    
    qr_text = f"SCHOOL: {school_name} | NAME: {student_name} | ROLL: {roll_no} | DOB: {disp_dob} | MARKS: {total_marks} | GRADE: {grade} | RESULT: {result_stat}"
    qr_data = urllib.parse.quote(qr_text)
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={qr_data}"
    barcode_url = f"https://barcode.tec-it.com/barcode.ashx?data={roll_no}&code=Code128&dpi=96"

    # Pre-calculated translations to avoid syntax issues
    lbl_annual = t('ANNUAL EXAMINATION', s_lang)
    lbl_cert = t('CERTIFICATE-CUM-MARK SHEET', s_lang)
    lbl_roll = t('ROLL NO', s_lang)
    lbl_cls = t('CLASS', s_lang)
    lbl_pen = t('PEN NO', s_lang)
    lbl_apaar = t('APAAR NO', s_lang)
    lbl_name = t('NAME', s_lang)
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
    if len(school_name) > 40: header_font_size = "22px"
    if len(school_name) > 55: header_font_size = "18px"

    html_content = (
        f"<div style='font-family: \"Times New Roman\", serif; border: 15px solid {outer_border}; padding: 4px; max-width: 800px; margin: auto; background-color: #ffffff;'>"
        f"<div style='border: 2px solid {border_color}; padding: 25px; background-color: {bg_color}; position: relative;'>"
        
        f"<div style='text-align: center; color: {border_color}; margin-bottom: 20px;'>"
        f"<h1 style='margin: 0; font-size: {header_font_size}; text-transform: uppercase; font-family: \"Georgia\", serif; text-shadow: 1px 1px 1px #e1bee7;'>{school_name}</h1>"
        f"<h3 style='margin: 5px 0; font-size: 16px; letter-spacing: 1px;'>ANNUAL EXAMINATION / <span style='font-size: 14px;'>{lbl_annual}</span> - {st_data.get('batch', '2025-2026')}</h3>"
        f"<p style='margin: 5px 0; font-weight: bold; font-size: 17px; text-decoration: underline;'>CERTIFICATE-CUM-MARK SHEET <br> <span style='font-size: 14px; text-decoration: none;'>({lbl_cert})</span></p>"
        "</div>"
        
        "<table style='width: 100%; font-size: 13px; color: #000000; margin-bottom: 20px; font-weight: bold;'>"
        f"<tr><td><span style='color:{border_color}; font-weight:normal;'>ROLL NO / {lbl_roll}:</span> {roll_no}</td><td style='text-align: right;'><span style='color:{border_color}; font-weight:normal;'>CLASS / {lbl_cls}:</span> {st_data.get('class', 'N/A')}</td></tr>"
        f"<tr><td><span style='color:{border_color}; font-weight:normal;'>PEN NO / {lbl_pen}:</span> {st_data.get('pen_no', 'N/A')}</td><td style='text-align: right;'><span style='color:{border_color}; font-weight:normal;'>APAAR NO / {lbl_apaar}:</span> {st_data.get('apaar_no', 'N/A')}</td></tr>"
        "</table>"
        
        "<table style='width: 100%; font-size: 14px; margin-bottom: 15px; text-transform: uppercase; color: #000000; line-height: 1.8;'>"
        f"<tr><td style='width: 240px; color: {border_color}; font-weight: bold; font-style: italic;'>Certify that / <span style='font-size:12px;'>{lbl_name}</span></td><td style='font-weight: bold; font-size: 16px;'>{student_name}</td></tr>"
        f"<tr><td style='color: {border_color}; font-weight: bold; font-style: italic;'>Mother's Name / <span style='font-size:12px;'>{lbl_mother}</span></td><td style='font-weight: bold;'>{st_data.get('mother_name', 'N/A').upper()}</td></tr>"
        f"<tr><td style='color: {border_color}; font-weight: bold; font-style: italic;'>Father's Name / <span style='font-size:12px;'>{lbl_father}</span></td><td style='font-weight: bold;'>{st_data.get('father_name', 'N/A').upper()}</td></tr>"
        f"<tr><td style='color: {border_color}; font-weight: bold; font-style: italic;'>Date of Birth / <span style='font-size:12px;'>{lbl_dob}</span></td><td style='font-weight: bold;'>{disp_dob}</td></tr>"
        "</table>"
        
        f"<p style='color: {border_color}; font-style: italic; font-size: 14px; text-align: center; margin-bottom: 20px;'>Passed the Annual Examination held in the academic batch of {st_data.get('batch', 'N/A')}. <br><span style='font-size: 13px;'>{lbl_pass_text}</span></p>"
        
        f"<div style='text-align: center; color: {border_color}; font-weight: bold; font-size: 14px; margin-bottom: 5px;'>SUBJECTS AND MARKS SECURED</div>"
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
        
        f"<div style='text-align: center; font-weight: bold; font-size: 14px; color: #000; margin-top: 20px;'>( {words_total} )</div>"
        
        f"<table style='width: 100%; margin-top: 20px; text-align: center; color: {border_color};'>"
        "<tr>"
        
        "<td style='width: 33%; vertical-align: bottom;'>"
        f"<img src='{barcode_url}' alt='Barcode' style='height: 35px; margin-bottom: 10px; max-width: 100%;'/>"
        f"<div style='font-size: 11px;'>DATE OF PUBLICATION <br><span style='font-size:10px;'>({lbl_pub_date})</span></div>"
        f"<div style='font-weight: bold; font-size: 14px; margin-top: 5px; margin-bottom: 30px;'>{datetime.date.today().strftime('%d/%m/%Y')}</div>"
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

# --- PDF ଜେନେରେଟର (CLEAN ENGLISH PRINTING TO AVOID GLYPH ERRORS) ---
def create_pdf(filename, school_name, st_data, roll_no):
    raw_dob = st_data.get('dob', '')
    disp_dob = raw_dob
    if len(raw_dob.split('-')) == 3:
        y, m, d = raw_dob.split('-')
        if len(y) == 4:
            disp_dob = f"{d}-{m}-{y}"
            
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
    c.drawCentredString(140, y-25, f"{datetime.date.today().strftime('%d/%m/%Y')}")
    
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
schools_db, students_db = load_data()
master_db = load_master_data()

# ----------------- DYNAMIC LINK GENERATION -----------------
portal_param = st.query_params.get("portal", "home")

default_idx = 0
if portal_param == "master":
    default_idx = 1
elif portal_param == "school":
    default_idx = 2
elif portal_param == "student":
    default_idx = 3

st.markdown("<h3 style='text-align: center; color: #0284C7; margin-top:-20px;'>✨ WELCOME KULU SUTAR ✨</h3>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: #1E3A8A; font-size: 30px;'>🏫 ADVANCED SCHOOL MANAGEMENT SYSTEM</h1>", unsafe_allow_html=True)
st.markdown("<hr style='margin-bottom: 10px;'>", unsafe_allow_html=True)

menu = st.sidebar.selectbox("🎯 Navigation Menu", ["Home Page", "Master Login", "School Login", "Results"], index=default_idx)

if menu == "Home Page":
    st.query_params["portal"] = "home"
elif menu == "Master Login":
    st.query_params["portal"] = "master"
elif menu == "School Login":
    st.query_params["portal"] = "school"
elif menu == "Results":
    st.query_params["portal"] = "student"

classes_list = [str(i) for i in range(1, 11)]
batches_list = [f"{y}-{y+1}" for y in range(2020, 2051)]

# ----------------- HOME PAGE (ERP STYLE UI) -----------------
if menu == "Home Page":
    st.markdown("""
    <style>
    .notice-container { background-color: #1e293b; border-radius: 5px; margin-bottom: 25px; border: 1px solid #475569; }
    .notice-header { background-color: #27374D; color: white; text-align: center; padding: 12px; font-weight: bold; font-size: 20px; }
    .notice-item { margin-bottom: 15px; font-size: 16px; border-bottom: 1px dotted #475569; padding-bottom: 10px; }
    .new-badge { background-color: #fbbf24; color: black; font-size: 12px; font-weight: bold; padding: 2px 6px; border-radius: 3px; margin-left: 5px; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    .login-card { background-color: white; border: 1px solid #cbd5e1; border-bottom: 5px solid #fbbf24; border-radius: 8px; padding: 20px; margin-bottom: 15px; text-align: center; text-decoration: none; display: block; color: #1e3a8a; box-shadow: 0 4px 6px rgba(0,0,0,0.05); transition: 0.3s; }
    .login-card:hover { background-color: #f8fafc; border-bottom: 5px solid #1e3a8a; transform: translateY(-2px); }
    .login-title { font-size: 24px; font-weight: bold; margin-bottom: 5px; display: flex; align-items: center; justify-content: center; gap: 10px; }
    .login-sub { font-size: 14px; color: #64748b; }
    </style>
    """, unsafe_allow_html=True)

    notice_html = (
        "<div class='notice-container'>"
        "<div class='notice-header'>RECENT NOTICE</div>"
        "<div style='padding: 0; overflow: hidden; background-color: #1e293b; color: #e2e8f0;'>"
        "<marquee direction='up' scrollamount='2' onmouseover='this.stop();' onmouseout='this.start();' style='height: 180px; padding: 15px;'>"
        "<div class='notice-item'>⏩ Welcome to Advanced School Management System! <span class='new-badge'>NEW!</span></div>"
        "<div class='notice-item'>⏩ Master & School portal passwords are encrypted and secured.</div>"
        "<div class='notice-item'>⏩ Online Student Rank Card generation is now active for all classes.</div>"
        "<div class='notice-item'>⏩ Students can now Search Result by Batch, Roll No OR Name. No School ID needed! <span class='new-badge'>UPDATE!</span></div>"
        "<div class='notice-item'>⏩ APAAR and PEN details have been integrated into the system.</div>"
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

    st.markdown("""
    <a href="?portal=master" target="_self" class="login-card" style="text-decoration: none;">
        <div class="login-title">🏛️ Master Login</div>
        <div class="login-sub">Click here to login as Admin / University</div>
    </a>
    <a href="?portal=school" target="_self" class="login-card" style="text-decoration: none;">
        <div class="login-title">🏫 School Login</div>
        <div class="login-sub">Click here to login as School / College</div>
    </a>
    <a href="?portal=student" target="_self" class="login-card" style="text-decoration: none;">
        <div class="login-title">🎓 Results</div>
        <div class="login-sub">Click here to check Student Rank Card</div>
    </a>
    """, unsafe_allow_html=True)

# ----------------- MASTER LOGIN -----------------
elif menu == "Master Login":
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
                if m_user == master_db["username"] and m_pass == master_db["password"]:
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
                        master_db["username"] = new_m_user
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
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 All IDs & Schools", "🏫 Register School", "🎓 Edit Students Data", "✏️ Edit Registered Schools", "⚙️ Settings (Change ID/Pass)"])
        
        with tab1:
            st.markdown("### 👁️ System Overview & Manage Schools")
            st.info("🔒 ଏହି ମାଷ୍ଟର୍ ପ୍ୟାନେଲ୍ କେବଳ ଆପଣ ହିଁ ଦେଖିପାରିବେ।")
            st.success("🔗 **Share Direct School Login Link:** `?portal=school`")

            st.markdown("#### 🏫 Registered Schools (View & Delete):")
            if not schools_db:
                st.write("କୌଣସି ସ୍କୁଲ୍ ରେଜିଷ୍ଟର୍ ହୋଇନାହିଁ।")
            else:
                for s_id, s_info in list(schools_db.items()):
                    c_1, c_2, c_3 = st.columns([2, 4, 2])
                    c_1.write(f"**School ID:** {s_id} | State: {s_info.get('state', 'N/A')}")
                    c_2.write(f"**Name:** {s_info['name']}")
                    if c_3.button(f"🗑️ Delete School", key=f"del_school_{s_id}"):
                        del schools_db[s_id]
                        if s_id in students_db:
                            del students_db[s_id]
                        save_data(schools_db, students_db)
                        st.success(f"School '{s_id}' ସମ୍ପୂର୍ଣ୍ଣ ରୂପେ ଡିଲିଟ୍ ହୋଇଗଲା!")
                        st.rerun()
                
            st.markdown("#### 🎓 Registered Student IDs:")
            total_students = 0
            for s_id, studs in students_db.items():
                for r_no, st_info in studs.items():
                    b_info = st_info.get("batch", "N/A")
                    st.write(f"- **Student ID:** {r_no} | **School ID:** {s_id} | Name: {st_info['name']} | Batch: {b_info}")
                    total_students += 1
            if total_students == 0:
                st.write("No students registered yet.")

        with tab2:
            st.markdown("### Register New School")
            new_s_id = st.text_input("New School ID (e.g. S002)")
            new_s_name = st.text_input("School Name")
            
            indian_states = list(STATE_LANG_MAP.keys())
            new_s_state = st.selectbox("Select State (ରାଜ୍ୟ ବାଛନ୍ତୁ)", indian_states, index=18) 
            
            new_s_pass = st.text_input("School Password", type="password")
            
            if new_s_state:
                new_s_lang = STATE_LANG_MAP[new_s_state]
                st.info(f"🌐 System Language for this school will be: **{new_s_lang}**")

            if st.button("Create School Account"):
                if new_s_id and new_s_name and new_s_pass:
                    schools_db[new_s_id] = {
                        "name": new_s_name, 
                        "pass": new_s_pass, 
                        "state": new_s_state, 
                        "lang": STATE_LANG_MAP[new_s_state]
                    }
                    save_data(schools_db, students_db)
                    st.success(f"ସ୍କୁଲ୍ '{new_s_name}' ସଫଳତାର ସହ ପଞ୍ଜୀକୃତ ହୋଇଗଲା! (State: {new_s_state})")
                else:
                    st.warning("ସମସ୍ତ ଫିଲ୍ଡ ପୂରଣ କରନ୍ତୁ।")
                    
        with tab3:
            st.markdown("### 📋 Manage All Students (Master Access)")
            master_school_sel = st.selectbox("Select School", ["--Select--"] + list(schools_db.keys()))
            if master_school_sel != "--Select--":
                school_students = students_db.get(master_school_sel, {})
                if school_students:
                    m_edit_roll = st.selectbox("Select Student Roll No to Edit/Delete", list(school_students.keys()))
                    m_curr_st = school_students[m_edit_roll]
                    
                    st.markdown("#### Edit Student Details")
                    c1, c2 = st.columns(2)
                    with c1:
                        m_up_name = st.text_input("Student Name", value=m_curr_st['name'], key="m_up_n")
                        m_up_father = st.text_input("Father's Name", value=m_curr_st.get('father_name', ''), key="m_up_f")
                        genders = ["Male", "Female", "Other"]
                        g_val = m_curr_st.get('gender', 'Male')
                        m_up_gender = st.selectbox("Gender", genders, index=genders.index(g_val) if g_val in genders else 0, key="m_up_gen")
                        m_up_pen = st.text_input("PEN NO", value=m_curr_st.get('pen_no', ''), key="m_up_pen")
                        
                        cls_val = m_curr_st.get('class', '1')
                        m_up_cls = st.selectbox("Class", classes_list, index=classes_list.index(cls_val) if cls_val in classes_list else 0, key="m_up_c")
                        
                    with c2:
                        m_up_dob = st.text_input("DOB (YYYY-MM-DD)", value=m_curr_st['dob'], key="m_up_d")
                        m_up_mother = st.text_input("Mother's Name", value=m_curr_st.get('mother_name', ''), key="m_up_m")
                        m_up_apaar = st.text_input("APAAR NO", value=m_curr_st.get('apaar_no', ''), key="m_up_apaar")
                        
                        b_val = m_curr_st.get('batch', '2025-2026')
                        b_idx = batches_list.index(b_val) if b_val in batches_list else 5
                        m_up_batch = st.selectbox("Batch", batches_list, index=b_idx, key="m_up_batch")
                    
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
                                new_m_subjects[u_sub] = {"full": u_f, "obt": u_o}
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
                            new_per = (m_tot_obt / m_tot_full * 100) if m_tot_full > 0 else 0.0
                            new_res = "PASS" if new_per >= 33 else "FAIL"
                            new_grd = "A1" if new_per >= 90 else "A2" if new_per >= 80 else "B1" if new_per >= 70 else "B2" if new_per >= 60 else "C1" if new_per >= 50 else "C2" if new_per >= 40 else "D" if new_per >= 33 else "F"
                            
                            school_students[m_edit_roll].update({
                                "name": m_up_name, "gender": m_up_gender, "pen_no": m_up_pen, "apaar_no": m_up_apaar,
                                "father_name": m_up_father, "mother_name": m_up_mother,
                                "dob": m_up_dob, "class": m_up_cls, "batch": m_up_batch,
                                "subjects": new_m_subjects if new_m_subjects else m_subjects,
                                "total_obt": m_tot_obt, "total_full": m_tot_full, 
                                "percentage": round(new_per, 2), "result": new_res, "grade": new_grd
                            })
                            save_data(schools_db, students_db)
                            st.success(f"Roll No {m_edit_roll} data updated successfully!")
                            
                    with col_dl:
                        if st.button("🗑️ Delete Student (Master Only)", type="primary"):
                            del school_students[m_edit_roll]
                            save_data(schools_db, students_db)
                            st.success("Student deleted successfully!")
                            st.rerun()
                else:
                    st.warning("No students in this school.")

        with tab4:
            st.markdown("### ✏️ Edit Registered Schools")
            if schools_db:
                selected_edit_school = st.selectbox("Select School ID to Edit", list(schools_db.keys()))
                curr_s_data = schools_db[selected_edit_school]
                
                edit_s_name = st.text_input("Edit School Name", value=curr_s_data.get('name', ''))
                
                indian_states = list(STATE_LANG_MAP.keys())
                curr_state = curr_s_data.get('state', 'Odisha')
                state_idx = indian_states.index(curr_state) if curr_state in indian_states else 18
                edit_s_state = st.selectbox("Edit School State", indian_states, index=state_idx)
                
                edit_s_pass = st.text_input("Edit School Password", value=curr_s_data.get('pass', ''), type="password")
                
                if st.button("Update School Profile"):
                    if edit_s_name and edit_s_pass:
                        schools_db[selected_edit_school].update({
                            "name": edit_s_name,
                            "pass": edit_s_pass,
                            "state": edit_s_state,
                            "lang": STATE_LANG_MAP[edit_s_state]
                        })
                        save_data(schools_db, students_db)
                        st.success(f"School Profile Updated! The portal language is now set to {STATE_LANG_MAP[edit_s_state]}.")
                    else:
                        st.warning("Please fill all the details.")
            else:
                st.warning("No schools registered yet.")

        with tab5:
            st.markdown("### ⚙️ Update Master Profile & Contact")
            up_m_user = st.text_input("Master Username", value=master_db.get("username", ""))
            up_m_pass = st.text_input("Master Password", value=master_db.get("password", ""), type="password")
            up_m_email = st.text_input("Recovery Email (For OTP)", value=master_db.get("email", ""))
            up_m_phone = st.text_input("Recovery Phone Number (For OTP)", value=master_db.get("phone", ""))
            
            if st.button("Save Profile Changes"):
                master_db.update({"username": up_m_user, "password": up_m_pass, "email": up_m_email, "phone": up_m_phone})
                save_master_data(master_db)
                st.success("Master profile updated successfully!")

# ----------------- SCHOOL LOGIN -----------------
elif menu == "School Login":
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
            elif s_id in schools_db and schools_db[s_id]["pass"] == s_pass:
                st.session_state['school_logged_id'] = s_id
                del st.session_state['school_captcha']
                st.rerun()
            else:
                st.error("❌ ଭୁଲ୍ School ID କିମ୍ବା Password!")
                st.session_state['school_captcha'] = str(random.randint(10000, 99999))
                st.rerun()
                
    else: 
        cur_school = st.session_state['school_logged_id']
        s_lang = schools_db[cur_school].get("lang", "English")
        s_state = schools_db[cur_school].get("state", "Unknown State")
        
        col1, col2 = st.columns([8, 2])
        with col1:
            st.info(f"🏫 **{t('School Portal', s_lang)} | School Portal** | ID: {cur_school} | {schools_db[cur_school]['name']} ({s_state})")
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
        
        with tab_list:
            st.markdown(f"### 📋 {t('My Students', s_lang)} | My Students")
            school_students = students_db.get(cur_school, {})
            if school_students:
                st.write(f"{t('Total Registered', s_lang)} **{len(school_students)}**")
                search_query = st.text_input(f"🔍 {t('Search', s_lang)} / Search")
                for r_no, s_info in school_students.items():
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
            roll_no = st.text_input("Roll No (Student ID)", key="add_roll")
            st_name = st.text_input("Student Name", key="add_name")
            
            c_new1, c_new2, c_new3 = st.columns(3)
            with c_new1:
                gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="add_gen")
            with c_new2:
                pen_no = st.text_input("PEN NO", key="add_pen")
            with c_new3:
                apaar_no = st.text_input("APAAR NO", key="add_apaar")
                
            father_name = st.text_input("Father's Name", key="add_father")
            mother_name = st.text_input("Mother's Name", key="add_mother")
            
            min_date = datetime.date(2000, 1, 1)
            max_date = datetime.date(2065, 12, 31)
            dob = st.date_input("DOB (YYYY-MM-DD)", min_value=min_date, max_value=max_date, key="add_dob")
            
            c_c1, c_c2 = st.columns(2)
            with c_c1:
                cls = st.selectbox("Class", classes_list, key="add_class")
            with c_c2:
                add_batch = st.selectbox("Batch", batches_list, index=5, key="add_batch")
            
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
                    subjects_data[s_name] = {"full": f_mark, "obt": o_mark}
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
                        if cur_school not in students_db:
                            students_db[cur_school] = {}
                        students_db[cur_school][roll_no] = {
                            "name": st_name, "gender": gender, "pen_no": pen_no, "apaar_no": apaar_no,
                            "father_name": father_name, "mother_name": mother_name,
                            "dob": str(dob), "class": cls, "batch": add_batch, "subjects": subjects_data,
                            "total_full": total_full_mark, "total_obt": total_obt_mark,
                            "percentage": round(percentage, 2), "result": result, "grade": grade
                        }
                        save_data(schools_db, students_db)
                        st.success(f"Roll No {roll_no} Data Saved!")
                    else:
                        st.error("Roll No and Student Name required.")
            with c_clear:
                if st.button("🧹 Clear Form"):
                    st.rerun()

        with tab_edit:
            st.markdown(f"### ✏️ {t('Edit Student', s_lang)} | Edit Student")
            school_students = students_db.get(cur_school, {})
            if school_students:
                edit_roll = st.selectbox("Select Roll No", list(school_students.keys()), key="edit_roll_sel")
                curr_st = school_students[edit_roll]
                
                up_name = st.text_input("Edit Name", value=curr_st['name'])
                
                c_up1, c_up2, c_up3 = st.columns(3)
                with c_up1:
                    genders = ["Male", "Female", "Other"]
                    g_val = curr_st.get('gender', 'Male')
                    up_gender = st.selectbox("Edit Gender", genders, index=genders.index(g_val) if g_val in genders else 0)
                with c_up2:
                    up_pen = st.text_input("Edit PEN NO", value=curr_st.get('pen_no', ''))
                with c_up3:
                    up_apaar = st.text_input("Edit APAAR NO", value=curr_st.get('apaar_no', ''))

                up_father = st.text_input("Edit Father's Name", value=curr_st.get('father_name', ''))
                up_mother = st.text_input("Edit Mother's Name", value=curr_st.get('mother_name', ''))
                up_dob = st.text_input("Edit DOB (YYYY-MM-DD)", value=curr_st['dob'])
                
                c_e1, c_e2 = st.columns(2)
                with c_e1:
                    cls_val = curr_st.get('class', '1')
                    up_cls = st.selectbox("Edit Class", classes_list, index=classes_list.index(cls_val) if cls_val in classes_list else 0)
                with c_e2:
                    b_val = curr_st.get('batch', '2025-2026')
                    b_idx = batches_list.index(b_val) if b_val in batches_list else 5
                    up_batch = st.selectbox("Edit Batch", batches_list, index=b_idx)
                
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
                            new_up_subjects[u_sub] = {"full": u_f, "obt": u_o}
                            up_tot_full += u_f
                            up_tot_obt += u_o
                else:
                    st.info("No detailed subjects found. Using only total marks.")
                    up_tot_full = float(curr_st.get('total_full', 300))
                    up_tot_obt = float(curr_st.get('total_obt', 0))

                st.info(f"📊 **Auto Summary:** Total Marks: {up_tot_obt}/{up_tot_full}")
                
                if st.button("💾 Save Updated Record"):
                    new_per = (up_tot_obt / up_tot_full * 100) if up_tot_full > 0 else 0.0
                    new_res = "PASS" if new_per >= 33 else "FAIL"
                    new_grd = "A1" if new_per >= 90 else "A2" if new_per >= 80 else "B1" if new_per >= 70 else "B2" if new_per >= 60 else "C1" if new_per >= 50 else "C2" if new_per >= 40 else "D" if new_per >= 33 else "F"
                    
                    school_students[edit_roll].update({
                        "name": up_name, "gender": up_gender, "pen_no": up_pen, "apaar_no": up_apaar,
                        "father_name": up_father, "mother_name": up_mother,
                        "dob": up_dob, "class": up_cls, "batch": up_batch,
                        "subjects": new_up_subjects if new_up_subjects else up_subjects,
                        "total_obt": up_tot_obt, "total_full": up_tot_full, 
                        "percentage": round(new_per, 2), "result": new_res, "grade": new_grd
                    })
                    save_data(schools_db, students_db)
                    st.success("Record Updated!")
            else:
                st.warning("No students available.")

        with tab_report:
            st.markdown(f"### 🖨️ {t('Report Card', s_lang)} | Report Card")
            school_students = students_db.get(cur_school, {})
            if school_students:
                rep_roll = st.selectbox("Select Student Roll No for Report", list(school_students.keys()), key="rep_sel")
                st_data = school_students[rep_roll]
                school_name = schools_db[cur_school]['name']
                
                st.markdown(generate_result_card_html(school_name, st_data, rep_roll, s_lang), unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    pdf_file = f"Report_{rep_roll}.pdf"
                    create_pdf(pdf_file, school_name, st_data, rep_roll)
                    with open(pdf_file, "rb") as f:
                        st.download_button("📥 Download PDF Report", f, file_name=pdf_file, mime="application/pdf", key="dl_sch")
                with col2:
                    if st.button("🖨️ Print Result Card", key="print_sch"):
                        components.html("<script>window.parent.print();</script>", height=0)
            else:
                st.warning("No students available.")

# ----------------- RESULTS PORTAL -----------------
elif menu == "Results":
    url_roll = st.query_params.get("roll", "")
    url_dob = st.query_params.get("dob", "")
    
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
    
    col_c, col_b = st.columns(2)
    with col_c:
        st_class = st.selectbox("Select Class (1 to 10)", classes_list, key="st_login_class") 
    with col_b:
        st_batch = st.selectbox("Select Batch", batches_list, index=5, key="st_login_batch")
        
    st_search_query = st.text_input("Roll Number OR Student Name (ରୋଲ୍ ନମ୍ବର କିମ୍ବା ନାମ ଦିଅନ୍ତୁ)", value=url_roll, key="st_login_search")
    st_dob_input = st.text_input("Date of Birth (DD-MM-YYYY)", value=url_dob, key="st_login_dob")
    
    if st.button("View Result") or (url_roll and url_dob):
        found_student = None
        found_roll = None
        found_school_id = None
        
        search_query_lower = st_search_query.strip().lower()
        
        db_dob_format = st_dob_input.strip()
        if db_dob_format.count('-') == 2:
            p1, p2, p3 = db_dob_format.split('-')
            if len(p1) == 2 and len(p3) == 4:
                db_dob_format = f"{p3}-{p2}-{p1}"
        
        for s_id, school_students in students_db.items():
            if st_search_query in school_students:
                potential_student = school_students[st_search_query]
                if potential_student["dob"] == db_dob_format and potential_student.get("class") == st_class and potential_student.get("batch", "2025-2026") == st_batch:
                    found_student = potential_student
                    found_roll = st_search_query
                    found_school_id = s_id
                    break
            
            if not found_student:
                for r_no, s_info in school_students.items():
                    if s_info.get("name", "").strip().lower() == search_query_lower:
                        if s_info["dob"] == db_dob_format and s_info.get("class") == st_class and s_info.get("batch", "2025-2026") == st_batch:
                            found_student = s_info
                            found_roll = r_no
                            found_school_id = s_id
                            break
            
            if found_student:
                break
                
        if found_student:
            student_name = found_student.get('name', '').upper()
            st.success(
                f"🎉 **Welcome {student_name}!** Your result is given below:  \n"
                f"🎉 **स्वागत है {student_name}!** आपका परिणाम नीचे दिया गया है:  \n"
                f"🎉 **ସ୍ୱାଗତମ୍ {student_name}!** ଆପଣଙ୍କ ରେଜଲ୍ଟ ତଳେ ଦିଆଗଲା:"
            )
            school_name = schools_db[found_school_id]['name']
            s_lang = schools_db[found_school_id].get("lang", "English")
            
            st.markdown(generate_result_card_html(school_name, found_student, found_roll, s_lang), unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                pdf_file = f"Result_{found_roll}.pdf"
                create_pdf(pdf_file, school_name, found_student, found_roll)
                with open(pdf_file, "rb") as f:
                    st.download_button("📥 Download PDF", f, file_name=pdf_file, mime="application/pdf", key="dl_stu")
            
            with col2:
                if st.button("🖨️ Print Result Card", key="print_stu"):
                    components.html("<script>window.parent.print();</script>", height=0)
        else:
            if not st_search_query or not st_dob_input:
                st.warning("ଦୟାକରି ସବୁ ତଥ୍ୟ ପୂରଣ କରନ୍ତୁ।")
            else:
                st.error("❌ କୌଣସି ରେକର୍ଡ ମିଳିଲା ନାହିଁ! ଭୁଲ୍ ତଥ୍ୟ (Roll Number/Name, DOB, Class କିମ୍ବା Batch) ଦେଇଛନ୍ତି।")
