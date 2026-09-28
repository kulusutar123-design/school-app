import streamlit as st
import psycopg2
from psycopg2 import sql
import os

st.set_page_config(page_title="Advanced School Management System", layout="wide", page_icon="🏫")

# ==========================================
# 1. CLOUD DATABASE CONNECTION (PostgreSQL/Supabase)
# ==========================================
@st.cache_resource
def init_connection():
    try:
        # Streamlit Secrets ରୁ ଡାଟାବେସ୍ ଲିଙ୍କ୍ ଆଣିବ
        db_url = st.secrets["DATABASE_URL"]
        conn = psycopg2.connect(db_url)
        return conn
    except Exception as e:
        st.error("⚠️ କ୍ଲାଉଡ୍ ଡାଟାବେସ୍ ଲିଙ୍କ୍ ମିଳୁନାହିଁ! ଦୟାକରି Streamlit Secrets ରେ DATABASE_URL ଦିଅନ୍ତୁ।")
        return None

conn = init_connection()

def init_db():
    if conn is not None:
        c = conn.cursor()
        # PostgreSQL ରେ AUTOINCREMENT ବଦଳରେ SERIAL ବ୍ୟବହାର ହୁଏ
        c.execute('''CREATE TABLE IF NOT EXISTS students (id SERIAL PRIMARY KEY, roll_no TEXT UNIQUE, name TEXT, class TEXT, dob TEXT, password TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS staff (id SERIAL PRIMARY KEY, emp_id TEXT UNIQUE, name TEXT, role TEXT, password TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS results (id SERIAL PRIMARY KEY, roll_no TEXT, subject TEXT, marks INTEGER, total INTEGER)''')
        conn.commit()
        c.close()

init_db()

def run_query(query, params=()):
    if conn is not None:
        c = conn.cursor()
        c.execute(query, params)
        if query.strip().upper().startswith("SELECT"):
            data = c.fetchall()
            c.close()
            return data
        else:
            conn.commit()
            c.close()
            return []
    return []

# ==========================================
# 2. EXACT UI CSS & DESIGN (From Screenshot)
# ==========================================
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url("https://images.unsplash.com/photo-1580582932707-520aed937b7b?q=80&w=2000&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    .marquee-blue { background-color: #2b5797; color: white; padding: 5px; font-weight: bold; text-align: center; font-size: 14px; margin-bottom: 2px;}
    .marquee-black { background-color: #1a1a1a; color: #ffcc00; padding: 6px; font-weight: bold; font-size: 13px; margin-bottom: 2px;}
    .marquee-red { background-color: #b30000; color: white; padding: 6px; font-weight: bold; font-size: 14px; margin-bottom: 20px;}
    
    .glass-box {
        background: rgba(255, 255, 255, 0.85);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
        margin-bottom: 15px;
    }
    
    .stButton > button {
        width: 100%;
        border-radius: 5px;
        font-weight: bold;
        background-color: #f8f9fa;
        color: #333;
        border: 1px solid #ccc;
        margin-bottom: 5px;
        transition: 0.3s;
    }
    .stButton > button:hover {
        background-color: #e2e6ea;
        transform: scale(1.02);
    }
    </style>
""", unsafe_allow_html=True)

if "portal" not in st.session_state:
    st.session_state.portal = "Home"

# ==========================================
# 3. HOME PAGE (FRONTEND REPLICA)
# ==========================================
if st.session_state.portal == "Home":
    st.markdown('<div class="marquee-blue"><marquee>Connecting Students, Teachers & Administration Seamlessly</marquee></div>', unsafe_allow_html=True)
    st.markdown('<div class="marquee-black"><marquee behavior="scroll" direction="left">A Software Developed by: KULU SUTAR | Helpdesk No: 8910223342 | Mail ID: kulusutar123@gmail.com</marquee></div>', unsafe_allow_html=True)
    st.markdown('<div class="marquee-red"><marquee behavior="scroll" direction="left">🚨 Central Government announces new scholarship schemes for brilliant students across India!</marquee></div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown('<div class="glass-box"><h4 style="text-align: center; color: #004080;">🎓 Academic Portal</h4>', unsafe_allow_html=True)
        if st.button("🧑‍🎓 Student Login"): st.session_state.portal = "Student"
        if st.button("👨‍🏫 Staff / Teacher Login"): st.session_state.portal = "Staff"
        if st.button("📅 View Notice Board"): st.session_state.portal = "Notice"
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="glass-box"><h4 style="text-align: center; color: #004080;">👑 Management Portal</h4>', unsafe_allow_html=True)
        if st.button("🛡️ Admin Login"): st.session_state.portal = "Admin"
        if st.button("💰 Fee Collection / Dues"): st.session_state.portal = "Fees"
        if st.button("📊 Attendance System"): st.session_state.portal = "Attendance"
        st.markdown('</div>', unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="glass-box"><h4 style="text-align: center; color: #004080;">📝 Examination & Results</h4>', unsafe_allow_html=True)
        if st.button("🏆 Check Results"): st.session_state.portal = "Results"
        if st.button("📄 Download Admit Card"): st.session_state.portal = "Admit Card"
        if st.button("📞 Helpdesk / Support"): st.session_state.portal = "Support"
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 4. SUB-PORTALS
# ==========================================
else:
    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    if st.button("⬅️ Back to Home"):
        st.session_state.portal = "Home"
        st.rerun()
        
    st.title(f"{st.session_state.portal} Portal")
    
    if st.session_state.portal == "Admin":
        admin_id = st.text_input("Admin ID")
        admin_pass = st.text_input("Password", type="password")
        if st.button("Login"):
            # Master Password Setup for you!
            if admin_id == "KULU123" and admin_pass == "Admin@2026":
                st.success("✅ ସୁପର ଆଡମିନ୍ (Super Admin) ଲଗଇନ୍ ସଫଳ ହେଲା!")
                # ଆମେ ଆଗକୁ ଏଠାରେ Dashboard କାମ କରିବା
            else:
                st.error("❌ ଭୁଲ୍ ଆଇଡି କିମ୍ବା ପାସୱାର୍ଡ!")
            
    elif st.session_state.portal == "Results":
        roll_no = st.text_input("Enter Roll Number (e.g. 076CB0034)")
        dob = st.date_input("Date of Birth")
        if st.button("Check Result"):
            data = run_query("SELECT * FROM results WHERE roll_no=%s", (roll_no,))
            if data:
                st.write(data)
            else:
                st.warning("No records found for this Roll Number.")
            
    else:
        st.write(f"Welcome to the {st.session_state.portal} section. Backend integration ready.")
        
    st.markdown('</div>', unsafe_allow_html=True)
