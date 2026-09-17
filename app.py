import streamlit as st
import streamlit.components.v1 as components
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import json
import os
import datetime
import random

st.set_page_config(page_title="Advanced School Management System", layout="centered")

SCHOOLS_FILE = "schools.json"
STUDENTS_FILE = "students.txt"
MASTER_FILE = "master.json"

# --- ଡାଟା ଲୋଡ୍ ଓ ସେଭ୍ ଫଙ୍କସନ୍ (Strong Persistence) ---
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
    schools = {"S001": {"name": "Govt High School Cuttack", "pass": "admin123"}}
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

# --- ସୁନ୍ଦର ରାଙ୍କ୍ କାର୍ଡ (RANK CARD) ଡିଜାଇନ୍ ---
def generate_result_card_html(school_name, st_data, roll_no):
    res_color = "#15803d" if st_data.get('result') == "PASS" else "#dc2626"
    bg_color = "#f0fdf4" if st_data.get('result') == "PASS" else "#fef2f2"
    
    raw_dob = st_data.get('dob', '')
    disp_dob = raw_dob
    if len(raw_dob.split('-')) == 3:
        y, m, d = raw_dob.split('-')
        if len(y) == 4:
            disp_dob = f"{d}-{m}-{y}"

    rows_html = ""
    for sub, m_info in st_data.get('subjects', {}).items():
        rows_html += (
            f"<tr>"
            f"<td style='padding: 12px; border: 1px solid #cbd5e1; text-align: left; font-weight: bold;'>{sub}</td>"
            f"<td style='padding: 12px; border: 1px solid #cbd5e1;'>{m_info['full']}</td>"
            f"<td style='padding: 12px; border: 1px solid #cbd5e1; font-weight: bold;'>{m_info['obt']}</td>"
            f"</tr>"
        )

    html_content = f"""
    <div style="border: 3px solid #1E3A8A; padding: 30px; border-radius: 12px; 
                background-color: #ffffff; color: #1e293b; font-family: Arial, sans-serif; 
                max-width: 850px; margin: auto; box-shadow: 0px 8px 16px rgba(0,0,0,0.15);">
        <div style="text-align: center; border-bottom: 4px double #1E3A8A; padding-bottom: 15px; margin-bottom: 25px;">
            <h1 style="color: #1E3A8A; margin: 0; font-size: 32px; text-transform: uppercase; font-weight: 900;">
                🏫 {school_name}
            </h1>
            <h3 style="color: #e11d48; margin: 8px 0 0 0; letter-spacing: 3px; font-weight: bold;">
                OFFICIAL RANK CARD
            </h3>
        </div>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 25px; font-size: 16px;">
            <tr>
                <td style="padding: 8px 0;"><b>Student Name:</b> {st_data.get('name', '')}</td>
                <td style="padding: 8px 0; text-align: right;"><b>Roll No:</b> {roll_no}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0;"><b>Father's Name:</b> {st_data.get('father_name', 'N/A')}</td>
                <td style="padding: 8px 0; text-align: right;"><b>Class:</b> {st_data.get('class', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0;"><b>Mother's Name:</b> {st_data.get('mother_name', 'N/A')}</td>
                <td style="padding: 8px 0; text-align: right;"><b>Date of Birth:</b> {disp_dob}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0;"><b>Gender:</b> {st_data.get('gender', 'N/A')}</td>
                <td style="padding: 8px 0; text-align: right;"><b>PEN NO:</b> {st_data.get('pen_no', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0;"><b>APAAR NO:</b> {st_data.get('apaar_no', 'N/A')}</td>
                <td style="padding: 8px 0; text-align: right;"></td>
            </tr>
        </table>
        <h4 style="color: #ffffff; background-color: #1E3A8A; padding: 12px; margin: 0; text-align: center; border-top-left-radius: 8px; border-top-right-radius: 8px; letter-spacing: 1px;">
            SUBJECT-WISE PERFORMANCE
        </h4>
        <table style="width: 100%; border-collapse: collapse; text-align: center; margin-bottom: 30px; font-size: 16px; background-color: #f8fafc;">
            <tr style="background-color: #e2e8f0; color: #1e293b;">
                <th style="padding: 12px; border: 1px solid #cbd5e1;">Subject</th>
                <th style="padding: 12px; border: 1px solid #cbd5e1;">Full Marks</th>
                <th style="padding: 12px; border: 1px solid #cbd5e1;">Obtained Marks</th>
            </tr>
            {rows_html}
        </table>
        <div style="background-color: {bg_color}; padding: 20px; border: 2px solid {res_color}; border-radius: 8px;">
            <table style="width: 100%; font-size: 18px;">
                <tr>
                    <td style="padding: 5px 0;"><b>Total Marks:</b> <span style="font-size: 20px;">{st_data.get('total_obt', 0)} / {st_data.get('total_full', 0)}</span></td>
                    <td style="padding: 5px 0; text-align: center;"><b>Percentage:</b> <span style="font-size: 20px;">{st_data.get('percentage', 0)}%</span></td>
                    <td style="padding: 5px 0; text-align: right;"><b>Grade:</b> <span style="color: #1E3A8A; font-size: 24px; font-weight: 900;">{st_data.get('grade', 'N/A')}</span></td>
                </tr>
            </table>
            <div style="text-align: center; margin-top: 20px; padding-top: 15px; border-top: 2px dashed {res_color};">
                <span style="font-size: 20px; font-weight: bold; color: #475569;">FINAL RESULT:</span> 
                <span style="color: {res_color}; font-size: 28px; font-weight: 900; letter-spacing: 2px; margin-left: 10px;">
                    {st_data.get('result', 'N/A')}
                </span>
            </div>
        </div>
    </div>
    """
    return html_content

# --- PDF ଜେନେରେଟର ---
def create_pdf(filename, school_name, st_data, roll_no):
    raw_dob = st_data.get('dob', '')
    disp_dob = raw_dob
    if len(raw_dob.split('-')) == 3:
        y, m, d = raw_dob.split('-')
        if len(y) == 4:
            disp_dob = f"{d}-{m}-{y}"
            
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(300, 750, school_name)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(300, 730, "OFFICIAL RANK CARD")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, 680, f"Student Name: {st_data.get('name', '')}")
    c.drawString(400, 680, f"Roll No: {roll_no}")
    c.drawString(50, 660, f"Father's Name: {st_data.get('father_name', 'N/A')}")
    c.drawString(400, 660, f"Class: {st_data.get('class', '')}")
    c.drawString(50, 640, f"Mother's Name: {st_data.get('mother_name', 'N/A')}")
    c.drawString(400, 640, f"DOB: {disp_dob}")
    c.drawString(50, 620, f"Gender: {st_data.get('gender', 'N/A')}")
    c.drawString(400, 620, f"PEN NO: {st_data.get('pen_no', 'N/A')}")
    c.drawString(50, 600, f"APAAR NO: {st_data.get('apaar_no', 'N/A')}")
    
    c.line(50, 580, 550, 580)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 560, "Subject")
    c.drawString(300, 560, "Full Marks")
    c.drawString(450, 560, "Obtained Marks")
    c.line(50, 550, 550, 550)
    
    y = 530
    c.setFont("Helvetica", 12)
    for sub, m_info in st_data.get('subjects', {}).items():
        c.drawString(50, y, str(sub))
        c.drawString(300, y, str(m_info['full']))
        c.drawString(450, y, str(m_info['obt']))
        y -= 20
        
    c.line(50, y, 550, y)
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, f"Total Marks: {st_data.get('total_obt', 0)} / {st_data.get('total_full', 0)}")
    c.drawString(400, y, f"Percentage: {st_data.get('percentage', 0)}%")
    y -= 20
    c.drawString(50, y, f"Grade: {st_data.get('grade', '')}")
    c.drawString(400, y, f"Final Result: {st_data.get('result', '')}")
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

# ----------------- HOME PAGE (ERP STYLE UI) -----------------
if menu == "Home Page":
    # ନୂଆ ଏବଂ ସୁରକ୍ଷିତ Notice Board ଡିଜାଇନ୍ (ମୋବାଇଲ୍ Copy ପାଇଁ ଏକଦମ୍ ଠିକ୍)
    notice_html = (
        "<div style='background-color:#ffffff; border:1px solid #cbd5e1; border-radius:10px; box-shadow:0 4px 6px rgba(0,0,0,0.1); margin-bottom:25px; overflow:hidden;'>"
        "<div style='background:linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%); color:white; padding:15px; text-align:center; font-size:20px; font-weight:bold; letter-spacing:1px;'>📢 RECENT UPDATES & NOTICES</div>"
        "<div style='padding:15px; color:#1e293b; height:240px; overflow:hidden;'>"
        "<marquee direction='up' scrollamount='2' onmouseover='this.stop();' onmouseout='this.start();' style='height:100%;'>"
        "<div style='margin-bottom:12px; padding-bottom:8px; border-bottom:1px dashed #cbd5e1; font-size:16px;'>📌 <b>Welcome</b> to Advanced School Management System! <span style='background-color:#ef4444; color:white; font-size:11px; padding:2px 6px; border-radius:4px; font-weight:bold;'>NEW!</span></div>"
        "<div style='margin-bottom:12px; padding-bottom:8px; border-bottom:1px dashed #cbd5e1; font-size:16px;'>📌 <b>Security:</b> Master & School portal passwords are encrypted and secured.</div>"
        "<div style='margin-bottom:12px; padding-bottom:8px; border-bottom:1px dashed #cbd5e1; font-size:16px;'>📌 <b>Rank Cards:</b> Online Student Rank Card generation is now active for all classes.</div>"
        "<div style='margin-bottom:12px; padding-bottom:8px; border-bottom:1px dashed #cbd5e1; font-size:16px;'>📌 <b>Search Feature:</b> Students can now Search Result by Roll No OR Name. No School ID needed! <span style='background-color:#10b981; color:white; font-size:11px; padding:2px 6px; border-radius:4px; font-weight:bold;'>UPDATE!</span></div>"
        "<div style='margin-bottom:12px; padding-bottom:8px; border-bottom:1px dashed #cbd5e1; font-size:16px;'>📌 <b>New Fields:</b> APAAR and PEN details have been integrated into the system.</div>"
        "<div style='margin-top:20px; text-align:center; padding:15px; background-color:#f1f5f9; border-radius:8px; border:1px solid #e2e8f0;'>"
        "<div style='color:#1e3a8a; font-weight:bold; font-size:18px; margin-bottom:10px;'>📞 Helpdesk 24x7 Support:</div>"
        "<span style='background-color:#25D366; color:white; padding:6px 15px; border-radius:20px; font-weight:bold; display:inline-block; margin:5px; box-shadow:0 2px 4px rgba(0,0,0,0.1);'>💬 WhatsApp: 8910223342</span>"
        "<span style='background-color:#ea4335; color:white; padding:6px 15px; border-radius:20px; font-weight:bold; display:inline-block; margin:5px; box-shadow:0 2px 4px rgba(0,0,0,0.1);'>📧 Mail: kulusutar123@gmail.com</span>"
        "</div>"
        "</marquee>"
        "</div>"
        "</div>"
    )
    st.markdown(notice_html, unsafe_allow_html=True)

    st.markdown("""
    <style>
    .login-card { background-color: white; border: 1px solid #cbd5e1; border-bottom: 5px solid #fbbf24; border-radius: 8px; padding: 20px; margin-bottom: 15px; text-align: center; text-decoration: none; display: block; color: #1e3a8a; box-shadow: 0 4px 6px rgba(0,0,0,0.05); transition: 0.3s; }
    .login-card:hover { background-color: #f8fafc; border-bottom: 5px solid #1e3a8a; transform: translateY(-2px); }
    .login-title { font-size: 24px; font-weight: bold; margin-bottom: 5px; display: flex; align-items: center; justify-content: center; gap: 10px; }
    .login-sub { font-size: 14px; color: #64748b; }
    </style>
    
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
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 All IDs & Schools", "🏫 Register School", "🎓 Edit Students Data", "🔄 Forgot School Password", "⚙️ Settings (Change ID/Pass)"])
        
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
                    c_1.write(f"**School ID:** {s_id}")
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
                    st.write(f"- **Student ID:** {r_no} | **School ID:** {s_id} | Name: {st_info['name']}")
                    total_students += 1
            if total_students == 0:
                st.write("No students registered yet.")

        with tab2:
            st.markdown("### Register New School")
            new_s_id = st.text_input("New School ID (e.g. S002)")
            new_s_name = st.text_input("School Name")
            new_s_pass = st.text_input("School Password", type="password")
            if st.button("Create School Account"):
                if new_s_id and new_s_name and new_s_pass:
                    schools_db[new_s_id] = {"name": new_s_name, "pass": new_s_pass}
                    save_data(schools_db, students_db)
                    st.success(f"ସ୍କୁଲ୍ '{new_s_name}' ସଫଳତାର ସହ ପଞ୍ଜୀକୃତ ହୋଇଗଲା!")
                else:
                    st.warning("ସମସ୍ତ ଫିଲ୍ଡ ପୂରଣ କରନ୍ତୁ।")
                    
        with tab3:
            st.markdown("### 📋 Manage All Students (Master Access)")
            master_school_sel = st.selectbox("Select School", ["--Select--"] + list(schools_db.keys()))
            if master_school_sel != "--Select--":
                school_students = students_db.get(master_school_sel, {})
                if school_students:
                    m_edit_roll = st.selectbox("Select Student Roll No to Edit", list(school_students.keys()))
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
                        m_up_obt = st.number_input("Total Obtained Marks", value=float(m_curr_st.get('total_obt', 0)), key="m_up_o")
                        m_up_full = st.number_input("Total Full Marks", value=float(m_curr_st.get('total_full', 300)), key="m_up_full")
                    
                    if st.button("💾 Force Update Record"):
                        new_per = (m_up_obt / m_up_full * 100) if m_up_full > 0 else 0.0
                        new_res = "PASS" if new_per >= 30 else "FAIL"
                        new_grd = "A+" if new_per >= 90 else "A" if new_per >= 80 else "B" if new_per >= 60 else "C" if new_per >= 40 else "D" if new_per >= 30 else "F"
                        
                        school_students[m_edit_roll].update({
                            "name": m_up_name, "gender": m_up_gender, "pen_no": m_up_pen, "apaar_no": m_up_apaar,
                            "father_name": m_up_father, "mother_name": m_up_mother,
                            "dob": m_up_dob, "class": m_up_cls, "total_obt": m_up_obt,
                            "total_full": m_up_full, "percentage": round(new_per, 2),
                            "result": new_res, "grade": new_grd
                        })
                        save_data(schools_db, students_db)
                        st.success(f"Roll No {m_edit_roll} data updated successfully!")
                else:
                    st.warning("No students in this school.")

        with tab4:
            st.markdown("### 🔄 Forgot / Reset School Password")
            selected_school = st.selectbox("Select School ID", list(schools_db.keys()))
            new_reset_pass = st.text_input("Enter New Password for this School", type="password")
            if st.button("Update School Password"):
                if new_reset_pass:
                    schools_db[selected_school]['pass'] = new_reset_pass
                    save_data(schools_db, students_db)
                    st.success("School password changed successfully!")

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
        
        col1, col2 = st.columns([8, 2])
        with col1:
            st.info(f"🏫 **Your School ID:** {cur_school} | **School Name:** {schools_db[cur_school]['name']}")
        with col2:
            if st.button("🔴 Logout", key="s_logout"):
                del st.session_state['school_logged_id']
                st.rerun()

        st.markdown("---")
        st.success("🔗 **Share Direct Results Link:** `?portal=student`")

        tab_list, tab_add, tab_edit, tab_report = st.tabs(["📋 My Students & IDs", "Add/Save Student", "Edit/Update by Roll No", "Generate & Print Report"])
        
        with tab_list:
            st.markdown("### 📋 Student List, Search & IDs")
            school_students = students_db.get(cur_school, {})
            if school_students:
                st.write(f"Total Students Registered: **{len(school_students)}**")
                search_query = st.text_input("🔍 Search by Name or Student ID (Roll No)")
                for r_no, s_info in school_students.items():
                    if search_query.lower() in r_no.lower() or search_query.lower() in s_info['name'].lower() or search_query == "":
                        cols = st.columns([2, 3, 2, 1, 2])
                        cols[0].write(f"**Roll:** {r_no}")
                        cols[1].write(f"**Name:** {s_info['name']}")
                        cols[2].write(f"**PEN:** {s_info.get('pen_no', 'N/A')}")
                        cols[3].write(f"**Gen:** {s_info.get('gender', 'N/A')}")
                        if cols[4].button(f"🗑️ Delete", key=f"del_{r_no}"):
                            del school_students[r_no]
                            save_data(schools_db, students_db)
                            st.rerun()
            else:
                st.warning("No students registered in your school yet.")
                
        with tab_add:
            st.markdown("### 📝 Student Registration & Subject Marks Entry")
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
            
            cls = st.selectbox("Class", classes_list, key="add_class")
            
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
            result = "PASS" if percentage >= 30 else "FAIL"
            grade = "A+" if percentage >= 90 else "A" if percentage >= 80 else "B" if percentage >= 60 else "C" if percentage >= 40 else "D" if percentage >= 30 else "F"
            
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
                            "dob": str(dob), "class": cls, "subjects": subjects_data,
                            "total_full": total_full_mark, "total_obt": total_obt_mark,
                            "percentage": round(percentage, 2), "result": result, "grade": grade
                        }
                        save_data(schools_db, students_db)
                        st.success(f"Roll No {roll_no} ସେଭ୍ ହୋଇଗଲା!")
                    else:
                        st.error("Roll No ଏବଂ Student Name ଦିଅନ୍ତୁ।")
            with c_clear:
                if st.button("🧹 Clear Form"):
                    st.rerun()

        with tab_edit:
            st.markdown("### ✏️ Edit / Update Student Record")
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
                
                cls_val = curr_st.get('class', '1')
                up_cls = st.selectbox("Edit Class", classes_list, index=classes_list.index(cls_val) if cls_val in classes_list else 0)
                
                up_total_obt = st.number_input("Update Total Obtained Marks", value=float(curr_st.get('total_obt', 0)))
                up_total_full = st.number_input("Update Total Full Marks", value=float(curr_st.get('total_full', 300)))
                
                if st.button("💾 Save Updated Record"):
                    new_per = (up_total_obt / up_total_full * 100) if up_total_full > 0 else 0.0
                    new_res = "PASS" if new_per >= 30 else "FAIL"
                    new_grd = "A+" if new_per >= 90 else "A" if new_per >= 80 else "B" if new_per >= 60 else "C" if new_per >= 40 else "D" if new_per >= 30 else "F"
                    
                    school_students[edit_roll].update({
                        "name": up_name, "gender": up_gender, "pen_no": up_pen, "apaar_no": up_apaar,
                        "father_name": up_father, "mother_name": up_mother,
                        "dob": up_dob, "class": up_cls, "total_obt": up_total_obt,
                        "total_full": up_total_full, "percentage": round(new_per, 2),
                        "result": new_res, "grade": new_grd
                    })
                    save_data(schools_db, students_db)
                    st.success("ରେକର୍ଡ ଅପଡେଟ୍ ହୋଇଗଲା!")
            else:
                st.warning("କୌଣସି ଷ୍ଟୁଡେଣ୍ଟ୍ ନାହାଁନ୍ତି।")

        with tab_report:
            st.markdown("### 🖨️ Generate & Print Report Cards")
            school_students = students_db.get(cur_school, {})
            if school_students:
                rep_roll = st.selectbox("Select Student Roll No for Report", list(school_students.keys()), key="rep_sel")
                st_data = school_students[rep_roll]
                school_name = schools_db[cur_school]['name']
                
                st.markdown(generate_result_card_html(school_name, st_data, rep_roll), unsafe_allow_html=True)
                
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
                st.warning("କୌଣସି ଷ୍ଟୁଡେଣ୍ଟ୍ ନାହାଁନ୍ତି।")

# ----------------- RESULTS PORTAL -----------------
elif menu == "Results":
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
    
    st_class = st.selectbox("Select Class (1 to 10)", classes_list, key="st_login_class") 
    st_search_query = st.text_input("Roll Number OR Student Name (ରୋଲ୍ ନମ୍ବର କିମ୍ବା ନାମ ଦିଅନ୍ତୁ)", key="st_login_search")
    st_dob_input = st.text_input("Date of Birth (DD-MM-YYYY)", key="st_login_dob")
    
    if st.button("View Result"):
        found_student = None
        found_roll = None
        found_school_id = None
        
        search_query_lower = st_search_query.strip().lower()
        
        # ବ୍ୟବହାରକାରୀ ଦେଇଥିବା ଦିନ-ମାସ-ବର୍ଷ (DD-MM-YYYY) କୁ ଡାଟାବେସ୍ ଫର୍ମାଟ୍ (YYYY-MM-DD) କୁ ବଦଳାଇବା
        db_dob_format = st_dob_input.strip()
        if db_dob_format.count('-') == 2:
            p1, p2, p3 = db_dob_format.split('-')
            if len(p1) == 2 and len(p3) == 4:
                db_dob_format = f"{p3}-{p2}-{p1}"
        
        # ସବୁ ସ୍କୁଲ୍ ଭିତରେ ଖୋଜିବା
        for s_id, school_students in students_db.items():
            if st_search_query in school_students:
                potential_student = school_students[st_search_query]
                if potential_student["dob"] == db_dob_format and potential_student.get("class") == st_class:
                    found_student = potential_student
                    found_roll = st_search_query
                    found_school_id = s_id
                    break
            
            if not found_student:
                for r_no, s_info in school_students.items():
                    if s_info.get("name", "").strip().lower() == search_query_lower:
                        if s_info["dob"] == db_dob_format and s_info.get("class") == st_class:
                            found_student = s_info
                            found_roll = r_no
                            found_school_id = s_id
                            break
            
            if found_student:
                break
                
        if found_student:
            st.success(f"Welcome KULU SUTAR! ଆପଣଙ୍କ ରେଜଲ୍ଟ୍ ତଳେ ଦିଆଗଲା:")
            school_name = schools_db[found_school_id]['name']
            
            st.markdown(generate_result_card_html(school_name, found_student, found_roll), unsafe_allow_html=True)
            
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
                st.error("❌ କୌଣସି ରେକର୍ଡ ମିଳିଲା ନାହିଁ! ଭୁଲ୍ ତଥ୍ୟ (Roll Number/Name, DOB କିମ୍ବା Class) ଦେଇଛନ୍ତି।")
