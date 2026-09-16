import streamlit as st
import json
import os
import random
import datetime
from fpdf import FPDF

# File Locations
DATA_FILE = "students_db.txt"
USER_FILE = "users_db.txt"

# Utility Functions
def load_data(file_name):
    if os.path.exists(file_name):
        try:
            with open(file_name, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(file_name, data):
    with open(file_name, "w") as f:
        json.dump(data, f, indent=4)

def generate_report_pdf(student_data):
    pdf = FPDF()
    pdf.add_page()
    
    # Border
    pdf.rect(5, 5, 200, 287)
    
    # Header
    pdf.set_font("Arial", 'B', 18)
    pdf.cell(200, 15, txt=student_data.get('school', 'MY SCHOOL').upper(), ln=True, align='C')
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="ANNUAL PROGRESS REPORT CARD", ln=True, align='C')
    pdf.line(10, 35, 200, 35)
    
    # Student Info
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 11)
    
    pdf.cell(100, 8, txt=f"Student Name: {student_data.get('name', '')}")
    pdf.cell(100, 8, txt=f"Roll No: {student_data.get('roll', '')}", ln=True)
    
    pdf.cell(100, 8, txt=f"Class: {student_data.get('class', '')}")
    pdf.cell(100, 8, txt=f"DOB: {student_data.get('dob', '')}", ln=True)
    
    pdf.cell(100, 8, txt=f"Gender: {student_data.get('gender', '')}")
    pdf.cell(100, 8, txt=f"PEN NO: {student_data.get('pen_no', '')}", ln=True)
    
    pdf.cell(100, 8, txt=f"Father's Name: {student_data.get('father', '')}")
    pdf.cell(100, 8, txt=f"APAAR NO: {student_data.get('apaar_no', '')}", ln=True)
    
    pdf.cell(100, 8, txt=f"Mother's Name: {student_data.get('mother', '')}", ln=True)
    
    # Marks Table Header
    pdf.ln(8)
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(80, 10, "Subject", border=1, fill=True)
    pdf.cell(55, 10, "Full Mark", border=1, fill=True)
    pdf.cell(55, 10, "Obtained Mark", border=1, fill=True, ln=True)
    
    # Marks Data
    pdf.set_font("Arial", '', 11)
    for sub in student_data.get('subjects', []):
        pdf.cell(80, 10, sub['name'], border=1)
        pdf.cell(55, 10, str(sub['fm']), border=1)
        pdf.cell(55, 10, str(sub['om']), border=1, ln=True)
        
    # Result Summary
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"Final Result: {student_data.get('total', '')} | Percentage: {student_data.get('percentage', '')} | Grade: {student_data.get('grade', '')}", ln=True)
    
    # Signatures
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(100, 10, "Class Teacher Signature", align='L')
    pdf.cell(100, 10, "Headmaster Signature", align='R', ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# --- Streamlit UI Setup ---
st.set_page_config(page_title="Advanced School Management", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { border-radius: 5px; height: 3em; font-weight: bold; }
    .result-card { background-color: white; padding: 25px; border-radius: 15px; border-left: 5px solid #1f77b4; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏫 Advanced School Management System")

# Navigation Tabs
tab1, tab2 = st.tabs(["👨‍🎓 STUDENT PORTAL", "🏢 SCHOOL ADMIN LOGIN"])

# --- TAB 1: STUDENT PORTAL ---
with tab1:
    st.header("Check Your Result & Download PDF")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        s_roll = st.text_input("Enter Your Roll Number:", key="student_roll")
    with col_s2:
        s_dob = st.date_input("Select Your DOB:", min_value=datetime.date(2000, 1, 1), max_value=datetime.date(2065, 12, 31), key="student_dob")
    
    if st.button("🔍 View & Download Result"):
        students = load_data(DATA_FILE)
        str_dob = s_dob.strftime("%d/%m/%Y")
        
        found = False
        for r, data in students.items():
            if str(r) == str(s_roll) and data.get('dob', '') == str_dob:
                found = True
                st.success(f"Result Found for {data['name']}!")
                
                # Professional Result Display with new fields
                st.markdown(f"""
                <div class="result-card">
                    <h3 style="text-align: center; color: #1f77b4;">REPORT CARD - {data.get('school', '')}</h3>
                    <hr>
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <p><b>Name:</b> {data.get('name', '')}</p>
                            <p><b>Class:</b> {data.get('class', '')}</p>
                            <p><b>Gender:</b> {data.get('gender', 'N/A')}</p>
                        </div>
                        <div>
                            <p><b>Roll No:</b> {data.get('roll', '')}</p>
                            <p><b>PEN NO:</b> {data.get('pen_no', 'N/A')}</p>
                            <p><b>APAAR NO:</b> {data.get('apaar_no', 'N/A')}</p>
                        </div>
                    </div>
                    <hr>
                    <p style="text-align: center; font-size: 18px;"><b>Result:</b> <span style="color: green;">{data.get('grade', '')}</span> ({data.get('percentage', '')})</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Marks table display
                st.table(data.get('subjects', []))
                
                # PDF Download Button for Student
                pdf_bytes = generate_report_pdf(data)
                st.download_button(
                    label="📥 Download Official Marksheet (PDF)",
                    data=pdf_bytes,
                    file_name=f"Result_{s_roll}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                break
        
        if not found:
            st.error("Roll Number or Date of Birth does not match!")

# --- TAB 2: SCHOOL ADMIN ---
with tab2:
    if 'admin_logged_in' not in st.session_state:
        st.session_state.admin_logged_in = False

    if not st.session_state.admin_logged_in:
        st.subheader("Admin Access")
        admin_id = st.text_input("Admin ID / Mobile:")
        admin_pwd = st.text_input("Admin Password:", type="password")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔑 Login to Dashboard"):
                users = load_data(USER_FILE)
                if admin_id in users and users[admin_id] == admin_pwd:
                    st.session_state.admin_logged_in = True
                    st.rerun()
                else:
                    st.error("Invalid Credentials!")
        with c2:
            if st.button("📩 Create Admin Account"):
                st.info("Registration is open. Use the OTP feature below.")
                new_otp = str(random.randint(111111, 999999))
                st.session_state.admin_otp = new_otp
                st.warning(f"Registration OTP: {new_otp}")
        
        if 'admin_otp' in st.session_state:
            otp_val = st.text_input("Enter OTP:")
            new_reg_pwd = st.text_input("Create Password:", type="password")
            if st.button("Confirm Registration"):
                if otp_val == st.session_state.admin_otp:
                    users = load_data(USER_FILE)
                    users[admin_id] = new_reg_pwd
                    save_data(USER_FILE, users)
                    st.success("Admin Registered! Please login.")
                    del st.session_state.admin_otp
    
    else:
        st.sidebar.success(f"Admin Dashboard Active")
        if st.sidebar.button("🚪 Logout"):
            st.session_state.admin_logged_in = False
            st.rerun()
            
        st.subheader("Manage Student Records")
        
        # Search/Delete Logic
        search_col, action_col = st.columns([3, 1])
        with search_col:
            admin_search_roll = st.text_input("Search Roll Number to Edit/Delete:")
        
        students = load_data(DATA_FILE)
        loaded_info = {}
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🔍 Load Data"):
                if admin_search_roll in students:
                    loaded_info = students[admin_search_roll]
                    st.session_state.admin_subjects = loaded_info.get('subjects', [{"name": "ODIA", "fm": 100, "om": 0}])
                    st.success("Data Loaded Successfully!")
                else: 
                    st.error("Roll Number Not Found!")
        with col_btn2:
            if st.button("🗑️ Delete Student"):
                if admin_search_roll in students:
                    del students[admin_search_roll]
                    save_data(DATA_FILE, students)
                    st.success("Deleted Successfully!")
                    st.rerun()

        st.markdown("---")
        # Entry Form
        f1, f2 = st.columns(2)
        with f1:
            sch_name = st.text_input("School Name:", value=loaded_info.get('school', 'MY SCHOOL'))
            stu_name = st.text_input("Student Name:", value=loaded_info.get('name', ''))
            f_name = st.text_input("Father's Name:", value=loaded_info.get('father', ''))
            
            # New Field: PEN NO
            pen_no = st.text_input("PEN NO:", value=loaded_info.get('pen_no', ''))
            roll_no = st.text_input("Roll Number:", value=loaded_info.get('roll', admin_search_roll))
            
        with f2:
            cls_name = st.text_input("Class:", value=loaded_info.get('class', ''))
            # SETTING DOB RANGE 2000 to 2065
            
            # Safely parse DOB if it exists, otherwise use today's date
            default_dob = datetime.date.today()
            if loaded_info.get('dob'):
                try:
                    default_dob = datetime.datetime.strptime(loaded_info['dob'], "%d/%m/%Y").date()
                except:
                    pass
                    
            dob_val = st.date_input("Date of Birth:", value=default_dob,
                                    min_value=datetime.date(2000, 1, 1), 
                                    max_value=datetime.date(2065, 12, 31))
            
            m_name = st.text_input("Mother's Name:", value=loaded_info.get('mother', ''))
            
            # New Field: Gender
            gender_options = ["Select", "Male", "Female", "Other"]
            current_gender = loaded_info.get('gender', 'Select')
            g_index = gender_options.index(current_gender) if current_gender in gender_options else 0
            gender_val = st.selectbox("Gender:", options=gender_options, index=g_index)
            
            # New Field: APAAR NO
            apaar_no = st.text_input("APAAR NO:", value=loaded_info.get('apaar_no', ''))

        # Subjects
        st.write("### 📖 Subjects & Marks")
        if 'admin_subjects' not in st.session_state:
            st.session_state.admin_subjects = [{"name": "ODIA", "fm": 100, "om": 0}]

        for i, s in enumerate(st.session_state.admin_subjects):
            sc1, sc2, sc3, sc4 = st.columns([3, 2, 2, 1])
            st.session_state.admin_subjects[i]['name'] = sc1.text_input(f"Subject {i+1}", value=s['name'], key=f"admin_sub_{i}")
            st.session_state.admin_subjects[i]['fm'] = sc2.number_input(f"Full Mark", value=int(s['fm']), key=f"admin_fm_{i}")
            st.session_state.admin_subjects[i]['om'] = sc3.number_input(f"Obtained", value=int(s['om']), key=f"admin_om_{i}")
            if sc4.button("❌", key=f"admin_del_{i}"):
                st.session_state.admin_subjects.pop(i)
                st.rerun()

        if st.button("➕ Add Subject"):
            st.session_state.admin_subjects.append({"name": "", "fm": 100, "om": 0})
            st.rerun()

        # Calculation
        t_fm = sum([x['fm'] for x in st.session_state.admin_subjects])
        t_om = sum([x['om'] for x in st.session_state.admin_subjects])
        per = (t_om/t_fm*100) if t_fm > 0 else 0
        grd = "F"
        if per >= 90: grd = "A+"
        elif per >= 80: grd = "A"
        elif per >= 60: grd = "B"
        elif per >= 30: grd = "C"

        st.info(f"Total: {t_om}/{t_fm} | Percentage: {per:.2f}% | Grade: {grd}")

        if st.button("💾 SAVE STUDENT DATA", use_container_width=True):
            if roll_no:
                students[roll_no] = {
                    "school": sch_name, "name": stu_name, "father": f_name,
                    "mother": m_name, "roll": roll_no, "class": cls_name,
                    "dob": dob_val.strftime("%d/%m/%Y"),
                    "gender": gender_val if gender_val != "Select" else "",
                    "pen_no": pen_no, "apaar_no": apaar_no,
                    "subjects": st.session_state.admin_subjects,
                    "total": f"{t_om}/{t_fm}", "percentage": f"{per:.2f}%", "grade": grd
                }
                save_data(DATA_FILE, students)
                st.success("Student Data Saved Successfully!")
            else:
                st.error("Roll Number Required!")
