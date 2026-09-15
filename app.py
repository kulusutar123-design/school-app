import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import json
import os

st.set_page_config(page_title="School Management System", layout="wide")

# Persistent Storage using JSON files
SCHOOLS_FILE = "schools.json"
STUDENTS_FILE = "students.json"

def load_data():
    if os.path.exists(SCHOOLS_FILE):
        with open(SCHOOLS_FILE, "r") as f:
            schools = json.load(f)
    else:
        schools = {"S001": {"name": "Govt High School Cuttack", "pass": "admin123"}}
        
    if os.path.exists(STUDENTS_FILE):
        with open(STUDENTS_FILE, "r") as f:
            students = json.load(f)
    else:
        students = {
            "S001": {
                "101": {"name": "Amit Kumar Sutar", "dob": "2008-05-12", "class": "10", "marks": "88%"}
            }
        }
    return schools, students

def save_data(schools, students):
    with open(SCHOOLS_FILE, "w") as f:
        json.dump(schools, f, indent=4)
    with open(STUDENTS_FILE, "w") as f:
        json.dump(students, f, indent=4)

schools_db, students_db = load_data()

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏫 ONLINE SCHOOL MANAGEMENT SYSTEM</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

menu = st.sidebar.selectbox("🎯 Navigation Menu", ["Master Login", "School Login", "Student Login"])

# ----------------- MASTER LOGIN -----------------
if menu == "Master Login":
    st.subheader("🔑 Master Administrator Login")
    m_user = st.text_input("Master Username")
    m_pass = st.text_input("Master Password", type="password")
    
    if st.button("Login as Master"):
        if m_user == "master" and m_pass == "master123":
            st.success("માଷ୍ଟର୍ ଲଗ୍ଇନ୍ ସଫଳ ହେଲା! (Master Login Successful)")
            st.session_state['master_logged'] = True
        else:
            st.error("ଭୁଲ୍ Master ID କିମ୍ବା Password!")

    if st.session_state.get('master_logged', False):
        st.markdown("---")
        st.info("📌 **Master Control Panel:** Here Master can register schools, reset/forget school passwords, and also register students directly if needed.")
        
        tab1, tab2, tab3 = st.tabs(["Register School", "Manage / Forgot School Password", "Register Student (Master)"])
        
        with tab1:
            st.markdown("### 🏫 Register New School")
            new_s_id = st.text_input("New School ID (e.g. S002)")
            new_s_name = st.text_input("School Name")
            new_s_pass = st.text_input("School Password", type="password")
            if st.button("Create School Account"):
                if new_s_id and new_s_name and new_s_pass:
                    schools_db[new_s_id] = {"name": new_s_name, "pass": new_s_pass}
                    save_data(schools_db, students_db)
                    st.success(f"ସ୍କୁଲ୍ '{new_s_name}' ସଫଳତାର ସହ ପଞ୍ଜୀକୃତ ହୋଇଗଲା!")
                else:
                    st.warning("ସମସ୍ତ ଫିଲ୍ଡ ପୂରଣ କਰନ୍ତୁ।")
                    
        with tab2:
            st.markdown("### 🔄 Forgot / Reset School Password")
            selected_school = st.selectbox("Select School ID", list(schools_db.keys()))
            st.write(f"Current School Name: **{schools_db[selected_school]['name']}**")
            new_reset_pass = st.text_input("Enter New Password for this School", type="password")
            if st.button("Update / Reset Password"):
                if new_reset_pass:
                    schools_db[selected_school]['pass'] = new_reset_pass
                    save_data(schools_db, students_db)
                    st.success(f"School ID {selected_school} ရဲ့ password ଫର୍ଗେଟ୍/ଚେଞ୍ଜ୍ ସଫଳତାର ସହ ହୋଇଗଲା!")
                else:
                    st.warning("ନୂତନ ପାସୱାର୍ଡ ଦିଅନ୍ତୁ।")

        with tab3:
            st.markdown("### 🎓 Register Student (Master Panel)")
            target_school = st.selectbox("Select School for Student Registration", list(schools_db.keys()), key="m_target_school")
            m_roll = st.text_input("Student Roll Number")
            m_st_name = st.text_input("Student Full Name")
            m_dob = st.date_input("Date of Birth")
            m_cls = st.text_input("Class")
            m_marks = st.text_input("Marks / Result")
            if st.button("Add Student via Master"):
                if m_roll and m_st_name:
                    if target_school not in students_db:
                        students_db[target_school] = {}
                    students_db[target_school][m_roll] = {
                        "name": m_st_name,
                        "dob": str(m_dob),
                        "class": m_cls,
                        "marks": m_marks
                    }
                    save_data(schools_db, students_db)
                    st.success("ଷ୍ଟୁଡେଣ୍ଟ୍ ସଫଳତାର ସହ ପଞ୍ଜୀକୃତ ହେଲା!")
                else:
                    st.warning("ରୋଲ୍ ନମ୍ବର୍ ଏବଂ ନାମ ଦିଅନ୍ତୁ।")

        st.markdown("---")
        st.subheader("📋 Registered Schools List")
        st.write(schools_db)

# ----------------- SCHOOL LOGIN -----------------
elif menu == "School Login":
    st.subheader("🏫 School Portal (No Forgot Password option here)")
    s_id = st.text_input("School ID")
    s_pass = st.text_input("School Password", type="password")
    
    if st.button("Login as School"):
        if s_id in schools_db and schools_db[s_id]["pass"] == s_pass:
            st.success(f"ସ୍ୱାଗତମ୍ {schools_db[s_id]['name']}! ଲଗ୍ଇନ୍ ସଫଳ ହେଲା।")
            st.session_state['school_logged_id'] = s_id
        else:
            st.error("ଭୁଲ୍ School ID କିମ୍ବା Password! (Note: School login has no direct forgot password option. Contact Master)")

    if 'school_logged_id' in st.session_state:
        cur_school = st.session_state['school_logged_id']
        st.markdown("---")
        st.info(f"Connected School: **{schools_db[cur_school]['name']}** (ID: {cur_school})")
        
        tab_reg, tab_edit = st.tabs(["Register New Student", "Edit / Update Student Records"])
        
        with tab_reg:
            st.markdown("### 📝 Register Student")
            r_no = st.text_input("Student Roll No")
            st_name = st.text_input("Student Name")
            st_dob = st.date_input("Student Date of Birth")
            st_class = st.text_input("Class")
            st_marks = st.text_input("Marks / Result")
            
            if st.button("Save Student Registration"):
                if r_no and st_name:
                    if cur_school not in students_db:
                        students_db[cur_school] = {}
                    students_db[cur_school][r_no] = {
                        "name": st_name,
                        "dob": str(st_dob),
                        "class": st_class,
                        "marks": st_marks
                    }
                    save_data(schools_db, students_db)
                    st.success(f"Roll No {r_no} ({st_name}) ସଫଳତାର ସହ ରେଜିଷ୍ଟର୍ ଏବଂ ସେଭ୍ ହୋଇଗଲା!")
                else:
                    st.error("ରୋଲ୍ ନମ୍ବର୍ ଏବଂ ନାମ ଆବଶ୍ୟକ।")
                    
        with tab_edit:
            st.markdown("### ✏️ Edit or Update Student Records")
            school_students = students_db.get(cur_school, {})
            if school_students:
                edit_roll = st.selectbox("Select Roll Number to Edit", list(school_students.keys()))
                curr_info = school_students[edit_roll]
                
                up_name = st.text_input("Edit Name", value=curr_info['name'])
                up_dob = st.text_input("Edit DOB (YYYY-MM-DD)", value=curr_info['dob'])
                up_class = st.text_input("Edit Class", value=curr_info['class'])
                up_marks = st.text_input("Edit Marks", value=curr_info['marks'])
                
                if st.button("Update Student Record"):
                    school_students[edit_roll] = {
                        "name": up_name,
                        "dob": up_dob,
                        "class": up_class,
                        "marks": up_marks
                    }
                    save_data(schools_db, students_db)
                    st.success(f"Roll No {edit_roll} ରେକର୍ଡ ସଫଳତାର ସହ ଅପଡେଟ୍ ହୋଇଗଲା!")
            else:
                st.warning("ଏହି ସ୍କୁଲରେ କୌଣସି ଷ୍ଟୁଡେଣ୍ଟ୍ ପଞ୍ଜୀକୃତ ହୋଇନାହାଁନ୍ତି।")

        st.markdown("---")
        st.subheader("👥 Students List in Your School")
        st.write(students_db.get(cur_school, {}))

# ----------------- STUDENT LOGIN -----------------
elif menu == "Student Login":
    st.subheader("🎓 Student Portal (Login via Roll No & Date of Birth)")
    st_school_id = st.text_input("School ID")
    st_roll = st.text_input("Student Roll Number")
    st_dob_input = st.text_input("Date of Birth (YYYY-MM-DD)")
    
    if st.button("Login as Student"):
        try:
            student = students_db[st_school_id][st_roll]
            if student["dob"] == st_dob_input:
                st.success(f"ସ୍ୱାଗତମ୍ {student['name']}! ଲଗ୍ଇନ୍ ସଫଳ ହେଲା।")
                st.markdown(f"""
                ### 📋 Student Information Card
                - **School ID:** {st_school_id}
                - **Student Name:** {student['name']}
                - **Roll Number:** {st_roll}
                - **Date of Birth:** {student['dob']}
                - **Class:** {student['class']}
                - **Marks / Result:** {student['marks']}
                """)
                
                # PDF Generator & Saver
                if st.button("Generate & Download Student PDF Report"):
                    filename = f"Student_{st_roll}.pdf"
                    c = canvas.Canvas(filename, pagesize=letter)
                    c.drawString(100, 750, "========================================")
                    c.drawString(100, 730, "      ONLINE SCHOOL MANAGEMENT SYSTEM   ")
                    c.drawString(100, 710, "========================================")
                    c.drawString(100, 670, f"School ID: {st_school_id}")
                    c.drawString(100, 640, f"Student Name: {student['name']}")
                    c.drawString(100, 610, f"Roll Number: {st_roll}")
                    c.drawString(100, 580, f"Date of Birth: {student['dob']}")
                    c.drawString(100, 550, f"Class: {student['class']}")
                    c.drawString(100, 520, f"Marks/Result: {student['marks']}")
                    c.drawString(100, 480, "----------------------------------------")
                    c.drawString(100, 450, "Status: Verified & Generated Online")
                    c.save()
                    
                    with open(filename, "rb") as f:
                        st.download_button("📥 Click Here to Download PDF File", f, file_name=filename, mime="application/pdf")
            else:
                st.error("ଭୁଲ୍ Date of Birth! (ଯାଞ୍ଚ୍ କରନ୍ତୁ)")
        except KeyError:
            st.error("ଭୁଲ୍ School ID କିମ୍ବା Roll Number!")
