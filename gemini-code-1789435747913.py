import streamlit as st
import json
import os
import random
from fpdf import FPDF

# ଫାଇଲ୍ ଲୋକେସନ୍
DATA_FILE = "students.txt"
USER_FILE = "users.txt"

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

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'subjects' not in st.session_state:
    st.session_state.subjects = [{"name": "ODIA", "fm": 100, "om": 0}]
if 'otp' not in st.session_state:
    st.session_state.otp = None

st.set_page_config(page_title="School Management", layout="wide")
st.title("🏫 School Management System")

if not st.session_state.logged_in:
    st.subheader("User Login & Registration")
    uid = st.text_input("Email / Mobile Number:")
    pwd = st.text_input("Password:", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Login", use_container_width=True):
            users = load_data(USER_FILE)
            if uid in users and users[uid] == pwd:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid User ID or Password!")
    
    with col2:
        if st.button("📲 Get OTP for Registration", use_container_width=True):
            if uid:
                st.session_state.otp = str(random.randint(100000, 999999))
                st.info(f"Your OTP is: {st.session_state.otp} (Please note it down)")
            else:
                st.warning("Enter Email or Mobile Number first!")
    
    if st.session_state.otp:
        st.markdown("---")
        entered_otp = st.text_input("Enter 6-digit OTP:")
        new_pwd = st.text_input("Set New Password:", type="password")
        if st.button("Save & Register"):
            if entered_otp == st.session_state.otp:
                if new_pwd:
                    users = load_data(USER_FILE)
                    users[uid] = new_pwd
                    save_data(USER_FILE, users)
                    st.success("Registration Successful! Now you can login.")
                    st.session_state.otp = None
                else:
                    st.warning("Password cannot be empty!")
            else:
                st.error("Invalid OTP!")

else:
    col_w, col_l = st.columns([4, 1])
    with col_w:
        st.markdown("<h2 style='color: blue;'>WELCOME KULU SUTAR</h2>", unsafe_allow_html=True)
    with col_l:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()
            
    st.markdown("---")

    s_col1, s_col2, s_col3 = st.columns([2, 1, 1])
    with s_col1:
        search_roll = st.text_input("Search by Roll No:")
    with s_col2:
        btn_search = st.button("🔍 Search / Load", use_container_width=True)
    with s_col3:
        btn_delete = st.button("🗑️ Delete", use_container_width=True)

    students = load_data(DATA_FILE)
    loaded_data = {}
    if btn_search:
        if search_roll in students:
            loaded_data = students[search_roll]
            st.session_state.subjects = loaded_data.get("subjects", [{"name": "", "fm": 100, "om": 0}])
            st.success("Data Loaded!")
        else:
            st.error("Roll No not found!")

    if btn_delete:
        if search_roll in students:
            del students[search_roll]
            save_data(DATA_FILE, students)
            st.success("Deleted Successfully!")
        else:
            st.error("Roll No not found for deletion!")

    col1, col2 = st.columns(2)
    with col1:
        school = st.text_input("School Name:", value=loaded_data.get("school", ""))
        student_name = st.text_input("Student Name:", value=loaded_data.get("name", ""))
        father_name = st.text_input("Father Name:", value=loaded_data.get("father", ""))
        roll = st.text_input("Roll No:", value=loaded_data.get("roll", search_roll if btn_search else ""))
    with col2:
        stu_class = st.text_input("Class:", value=loaded_data.get("class", ""))
        dob = st.text_input("DOB (DD/MM/YYYY):", value=loaded_data.get("dob", ""))
        mother_name = st.text_input("Mother Name:", value=loaded_data.get("mother", ""))

    st.markdown("### 📚 Subjects & Marks")
    
    subs_to_remove = []
    for i, sub in enumerate(st.session_state.subjects):
        c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
        with c1:
            st.session_state.subjects[i]['name'] = st.text_input(f"Subject Name", value=sub['name'], key=f"sub_name_{i}")
        with c2:
            st.session_state.subjects[i]['fm'] = st.number_input(f"Full Mark", value=float(sub.get('fm', 100)), key=f"sub_fm_{i}")
        with c3:
            st.session_state.subjects[i]['om'] = st.number_input(f"Obtained Mark", value=float(sub.get('om', 0)), key=f"sub_om_{i}")
        with c4:
            st.write("")
            st.write("")
            if st.button("❌", key=f"del_{i}"):
                subs_to_remove.append(i)

    if subs_to_remove:
        for idx in sorted(subs_to_remove, reverse=True):
            st.session_state.subjects.pop(idx)
        st.rerun()

    if st.button("➕ Add More Subject"):
        st.session_state.subjects.append({"name": "", "fm": 100, "om": 0})
        st.rerun()

    total_fm = sum([float(s.get('fm', 0)) for s in st.session_state.subjects])
    total_om = sum([float(s.get('om', 0)) for s in st.session_state.subjects])
    pct = (total_om / total_fm * 100) if total_fm > 0 else 0
    grade = "F"
    if pct >= 90: grade = "A+"
    elif pct >= 80: grade = "A"
    elif pct >= 60: grade = "B"
    elif pct >= 30: grade = "C"

    st.markdown(f"**Total Marks:** `{total_om} / {total_fm}` &nbsp;&nbsp;|&nbsp;&nbsp; **Percentage:** `{pct:.2f}%` &nbsp;&nbsp;|&nbsp;&nbsp; **Grade:** `{grade}`")

    act_col1, act_col2 = st.columns(2)
    with act_col1:
        if st.button("💾 Save Student", use_container_width=True):
            if roll:
                students[roll] = {
                    "school": school, "class": stu_class, "name": student_name,
                    "father": father_name, "mother": mother_name, "dob": dob,
                    "roll": roll, "subjects": st.session_state.subjects,
                    "total": f"{total_om}/{total_fm}", "percentage": f"{pct:.2f}%", "grade": grade
                }
                save_data(DATA_FILE, students)
                st.success(f"Student Data Saved!")
            else:
                st.error("Roll No is required!")

    with act_col2:
        if st.button("📄 Generate PDF", use_container_width=True):
            if roll:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(200, 10, txt=school.upper() if school else "SCHOOL REPORT", ln=True, align='C')
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt="STUDENT PROGRESS REPORT", ln=True, align='C')
                pdf.line(10, 30, 200, 30)
                
                pdf.ln(10)
                pdf.cell(100, 8, txt=f"Name: {student_name}")
                pdf.cell(100, 8, txt=f"Roll No: {roll}", ln=True)
                pdf.cell(100, 8, txt=f"Class: {stu_class}")
                pdf.cell(100, 8, txt=f"DOB: {dob}", ln=True)
                pdf.cell(100, 8, txt=f"Father Name: {father_name}")
                pdf.cell(100, 8, txt=f"Mother Name: {mother_name}", ln=True)
                
                pdf.ln(10)
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(80, 10, "Subject", border=1)
                pdf.cell(40, 10, "Full Mark", border=1)
                pdf.cell(40, 10, "Obtained", border=1, ln=True)
                
                pdf.set_font("Arial", size=12)
                for sub in st.session_state.subjects:
                    pdf.cell(80, 10, sub.get("name", ""), border=1)
                    pdf.cell(40, 10, str(sub.get("fm", "")), border=1)
                    pdf.cell(40, 10, str(sub.get("om", "")), border=1, ln=True)
                    
                pdf.ln(10)
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(200, 10, txt=f"Total Marks: {total_om}/{total_fm}", ln=True)
                pdf.cell(200, 10, txt=f"Percentage: {pct:.2f}%", ln=True)
                pdf.cell(200, 10, txt=f"Grade: {grade}", ln=True)
                
                pdf_file = f"Report_{roll}.pdf"
                pdf.output(pdf_file)
                
                with open(pdf_file, "rb") as f:
                    st.download_button("⬇️ Download PDF", f, file_name=pdf_file, mime="application/pdf")
                st.success("PDF Generated! Click above to download.")
            else:
                st.error("Roll No is required for PDF!")