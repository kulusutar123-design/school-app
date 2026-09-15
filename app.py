import streamlit as st
import streamlit.components.v1 as components
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import json
import os
import datetime
import random

st.set_page_config(page_title="Advanced School Management System", layout="wide")

SCHOOLS_FILE = "schools.json"
STUDENTS_FILE = "students.txt"
MASTER_FILE = "master.json"

# --- ଡାଟା ଲୋଡ୍ ଓ ସେଭ୍ ଫଙ୍କସନ୍ ---
def load_master_data():
    if os.path.exists(MASTER_FILE):
        with open(MASTER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # Default Master Credentials
        return {"username": "master", "password": "master123", "email": "admin@school.com", "phone": "9999999999"}

def save_master_data(data):
    with open(MASTER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def load_data():
    if os.path.exists(SCHOOLS_FILE):
        with open(SCHOOLS_FILE, "r", encoding="utf-8") as f:
            schools = json.load(f)
    else:
        schools = {"S001": {"name": "Govt High School Cuttack", "pass": "admin123"}}
        
    if os.path.exists(STUDENTS_FILE):
        try:
            with open(STUDENTS_FILE, "r", encoding="utf-8") as f:
                students = json.load(f)
        except:
            students = {}
    else:
        students = {}
    return schools, students

def save_data(schools, students):
    with open(SCHOOLS_FILE, "w", encoding="utf-8") as f:
        json.dump(schools, f, indent=4)
    with open(STUDENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(students, f, indent=4)

# --- ସୁନ୍ଦର ରେଜଲ୍ଟ କାର୍ଡ ଡିଜାଇନ୍ ---
def generate_result_card_html(school_name, st_data, roll_no):
    res_color = "green" if st_data.get('result') == "PASS" else "red"
    html_content = f"""
    <div style="border: 3px solid #1E3A8A; padding: 25px; border-radius: 12px; background-color: #ffffff; color: #000; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); font-family: sans-serif;">
        <h1 style="text-align: center; color: #1E3A8A; margin-bottom: 5px;">🏫 {school_name}</h1>
        <h3 style="text-align: center; color: #d32f2f; margin-top: 0px; text-decoration: underline;">OFFICIAL RESULT CARD</h3>
        <table style="width: 100%; border: none; margin-top: 20px; font-size: 16px;">
            <tr>
                <td style="padding: 5px;"><b>Student Name:</b> {st_data.get('name', '')}</td>
                <td style="padding: 5px; text-align: right;"><b>Roll No:</b> {roll_no}</td>
            </tr>
            <tr>
                <td style="padding: 5px;"><b>Father's Name:</b> {st_data.get('father_name', 'N/A')}</td>
                <td style="padding: 5px; text-align: right;"><b>Class:</b> {st_data.get('class', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 5px;"><b>Mother's Name:</b> {st_data.get('mother_name', 'N/A')}</td>
                <td style="padding: 5px; text-align: right;"><b>DOB:</b> {st_data.get('dob', '')}</td>
            </tr>
        </table>
        <h4 style="color: #1E3A8A; background-color: #f0f0f0; padding: 8px; margin-top: 20px;">Subject-wise Marks</h4>
        <table style="width: 100%; border-collapse: collapse; text-align: center;" border="1">
            <tr style="background-color: #1E3A8A; color: white;">
                <th style="padding: 10px;">Subject</th>
                <th style="padding: 10px;">Full Marks</th>
                <th style="padding: 10px;">Obtained Marks</th>
            </tr>
    """
    for sub, m_info in st_data.get('subjects', {}).items():
        html_content += f"""
            <tr>
                <td style="padding: 8px; text-align: left;"><b>{sub}</b></td>
                <td style="padding: 8px;">{m_info['full']}</td>
                <td style="padding: 8px;">{m_info['obt']}</td>
            </tr>
        """
    html_content += f"""
        </table>
        <table style="width: 100%; margin-top: 20px; font-size: 18px; border-top: 2px solid #1E3A8A; padding-top: 10px;">
            <tr>
                <td><b>Total Marks:</b> {st_data.get('total_obt', 0)} / {st_data.get('total_full', 0)}</td>
                <td style="text-align: right;"><b>Percentage:</b> {st_data.get('percentage', 0)}%</td>
            </tr>
            <tr>
                <td><b>Grade:</b> <span style="color: #1E3A8A; font-weight: bold;">{st_data.get('grade', 'N/A')}</span></td>
                <td style="text-align: right;"><b>Final Result:</b> <span style="color: {res_color}; font-weight: bold;">{st_data.get('result', 'N/A')}</span></td>
            </tr>
        </table>
    </div>
    """
    return html_content

# --- PDF ଜେନେରେଟର ---
def create_pdf(filename, school_name, st_data, roll_no):
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(300, 750, school_name)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(300, 730, "OFFICIAL RESULT CARD")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, 680, f"Student Name: {st_data.get('name', '')}")
    c.drawString(400, 680, f"Roll No: {roll_no}")
    c.drawString(50, 660, f"Father's Name: {st_data.get('father_name', 'N/A')}")
    c.drawString(400, 660, f"Class: {st_data.get('class', '')}")
    c.drawString(50, 640, f"Mother's Name: {st_data.get('mother_name', 'N/A')}")
    c.drawString(400, 640, f"DOB: {st_data.get('dob', '')}")
    
    c.line(50, 620, 550, 620)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 600, "Subject")
    c.drawString(300, 600, "Full Marks")
    c.drawString(450, 600, "Obtained Marks")
    c.line(50, 590, 550, 590)
    
    y = 570
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

st.markdown("<h3 style='text-align: center; color: #0284C7;'>✨ WELCOME KULU SUTAR ✨</h3>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏫 ADVANCED SCHOOL MANAGEMENT SYSTEM</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

menu = st.sidebar.selectbox("🎯 Navigation Menu", ["Master Login", "School Login", "Student Login"])
classes_list = [str(i) for i in range(1, 11)]

# ----------------- MASTER LOGIN -----------------
if menu == "Master Login":
    st.subheader("🔑 Master Administrator Portal")
    
    login_mode = st.radio("Choose Action", ["Login", "Forgot Password", "Register Master"])
    
    if login_mode == "Login":
        m_user = st.text_input("Master Username")
        m_pass = st.text_input("Master Password", type="password")
        
        if st.button("Login"):
            if m_user == master_db["username"] and m_pass == master_db["password"]:
                st.success("Welcome KULU SUTAR! ମାଷ୍ଟର୍ ଲଗ୍ଇନ୍ ସଫଳ ହେଲା!")
                st.session_state['master_logged'] = True
            else:
                st.error("ଭୁଲ୍ Master ID କିମ୍ବା Password!")
                
    elif login_mode == "Forgot Password":
        st.info("Recover your Master Account using Mobile or Email OTP")
        verify_contact = st.text_input(f"Enter Registered Mobile No or Email")
        
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

    elif login_mode == "Register Master":
        st.info("Register / Set Up Master ID, Password, Mobile No & Email")
        reg_m_user = st.text_input("Set Master Username")
        reg_m_pass = st.text_input("Set Master Password", type="password")
        reg_m_email = st.text_input("Set Email ID (For OTP Verification)")
        reg_m_phone = st.text_input("Set Mobile Number (For OTP Verification)")
        
        if st.button("Register Master Account"):
            if reg_m_user and reg_m_pass and reg_m_email and reg_m_phone:
                master_db["username"] = reg_m_user
                master_db["password"] = reg_m_pass
                master_db["email"] = reg_m_email
                master_db["phone"] = reg_m_phone
                save_master_data(master_db)
                st.success("Master Registration Successful! You can now login with these credentials.")
            else:
                st.error("Please fill all the details to register!")

    # MASTER DASHBOARD
    if st.session_state.get('master_logged', False):
        st.markdown("---")
        tab1, tab2, tab3, tab4 = st.tabs(["🏫 Register School", "🎓 All Students Data (View & Edit)", "🔄 Forgot School Password", "⚙️ Master Profile Edit"])
        
        with tab1:
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
                    
        with tab2:
            st.markdown("### 📋 Manage All Students (Master Access)")
            master_school_sel = st.selectbox("Select School", ["--Select--"] + list(schools_db.keys()))
            if master_school_sel != "--Select--":
                st.write(f"**School:** {schools_db[master_school_sel]['name']}")
                school_students = students_db.get(master_school_sel, {})
                
                if school_students:
                    m_edit_roll = st.selectbox("Select Student Roll No to Edit", list(school_students.keys()))
                    m_curr_st = school_students[m_edit_roll]
                    
                    st.markdown("#### Edit Student Details")
                    c1, c2 = st.columns(2)
                    with c1:
                        m_up_name = st.text_input("Student Name", value=m_curr_st['name'], key="m_up_n")
                        m_up_father = st.text_input("Father's Name", value=m_curr_st.get('father_name', ''), key="m_up_f")
                        cls_val = m_curr_st.get('class', '1')
                        cls_idx = classes_list.index(cls_val) if cls_val in classes_list else 0
                        m_up_cls = st.selectbox("Class", classes_list, index=cls_idx, key="m_up_c")
                    with c2:
                        m_up_dob = st.text_input("DOB (YYYY-MM-DD)", value=m_curr_st['dob'], key="m_up_d")
                        m_up_mother = st.text_input("Mother's Name", value=m_curr_st.get('mother_name', ''), key="m_up_m")
                        m_up_obt = st.number_input("Total Obtained Marks", value=float(m_curr_st.get('total_obt', 0)), key="m_up_o")
                        m_up_full = st.number_input("Total Full Marks", value=float(m_curr_st.get('total_full', 300)), key="m_up_full")
                    
                    if st.button("💾 Force Update Record (Master)"):
                        new_per = (m_up_obt / m_up_full * 100) if m_up_full > 0 else 0.0
                        new_res = "PASS" if new_per >= 30 else "FAIL"
                        new_grd = "A+" if new_per >= 90 else "A" if new_per >= 80 else "B" if new_per >= 60 else "C" if new_per >= 40 else "D" if new_per >= 30 else "F"
                        
                        school_students[m_edit_roll].update({
                            "name": m_up_name, "father_name": m_up_father, "mother_name": m_up_mother,
                            "dob": m_up_dob, "class": m_up_cls, "total_obt": m_up_obt,
                            "total_full": m_up_full, "percentage": round(new_per, 2),
                            "result": new_res, "grade": new_grd
                        })
                        save_data(schools_db, students_db)
                        st.success(f"Roll No {m_edit_roll} data updated successfully by Master!")
                else:
                    st.warning("No students in this school.")

        with tab3:
            st.markdown("### 🔄 Forgot / Reset School Password")
            selected_school = st.selectbox("Select School ID", list(schools_db.keys()))
            new_reset_pass = st.text_input("Enter New Password for this School", type="password")
            if st.button("Update School Password"):
                if new_reset_pass:
                    schools_db[selected_school]['pass'] = new_reset_pass
                    save_data(schools_db, students_db)
                    st.success("School password changed successfully!")

        with tab4:
            st.markdown("### ⚙️ Update Master Profile & Contact")
            up_m_user = st.text_input("Change Master Username", value=master_db.get("username", ""))
            up_m_pass = st.text_input("Change Master Password", value=master_db.get("password", ""), type="password")
            up_m_email = st.text_input("Recovery Email", value=master_db.get("email", ""))
            up_m_phone = st.text_input("Recovery Phone Number", value=master_db.get("phone", ""))
            
            if st.button("Save Profile Changes"):
                master_db.update({"username": up_m_user, "password": up_m_pass, "email": up_m_email, "phone": up_m_phone})
                save_master_data(master_db)
                st.success("Master profile updated successfully!")

# ----------------- SCHOOL LOGIN -----------------
elif menu == "School Login":
    st.subheader("🏫 School Portal")
    s_id = st.text_input("School ID")
    s_pass = st.text_input("School Password", type="password")
    
    if st.button("Login as School"):
        if s_id in schools_db and schools_db[s_id]["pass"] == s_pass:
            st.success(f"Welcome KULU SUTAR! ସ୍ୱାଗତମ୍ {schools_db[s_id]['name']}!")
            st.session_state['school_logged_id'] = s_id
        else:
            st.error("ଭୁଲ୍ School ID କିମ୍ବା Password!")

    if 'school_logged_id' in st.session_state:
        cur_school = st.session_state['school_logged_id']
        st.markdown("---")
        
        tab_add, tab_edit, tab_list, tab_report = st.tabs(["Add/Save Student", "Edit/Update by Roll No", "Student List & Search", "Generate & Print Report"])
        
        with tab_add:
            st.markdown("### 📝 Student Registration & Subject Marks Entry")
            roll_no = st.text_input("Roll No", key="add_roll")
            st_name = st.text_input("Student Name", key="add_name")
            father_name = st.text_input("Father's Name", key="add_father")
            mother_name = st.text_input("Mother's Name", key="add_mother")
            
            min_date = datetime.date(2000, 1, 1)
            max_date = datetime.date(2065, 12, 31)
            dob = st.date_input("DOB (2000-2065)", min_value=min_date, max_value=max_date, key="add_dob")
            
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
                            "name": st_name, "father_name": father_name, "mother_name": mother_name,
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
                up_father = st.text_input("Edit Father's Name", value=curr_st.get('father_name', ''))
                up_mother = st.text_input("Edit Mother's Name", value=curr_st.get('mother_name', ''))
                up_dob = st.text_input("Edit DOB (YYYY-MM-DD)", value=curr_st['dob'])
                
                cls_val = curr_st.get('class', '1')
                cls_idx = classes_list.index(cls_val) if cls_val in classes_list else 0
                up_cls = st.selectbox("Edit Class", classes_list, index=cls_idx)
                
                up_total_obt = st.number_input("Update Total Obtained Marks", value=float(curr_st.get('total_obt', 0)))
                up_total_full = st.number_input("Update Total Full Marks", value=float(curr_st.get('total_full', 300)))
                
                if st.button("💾 Save Updated Record"):
                    new_per = (up_total_obt / up_total_full * 100) if up_total_full > 0 else 0.0
                    new_res = "PASS" if new_per >= 30 else "FAIL"
                    new_grd = "A+" if new_per >= 90 else "A" if new_per >= 80 else "B" if new_per >= 60 else "C" if new_per >= 40 else "D" if new_per >= 30 else "F"
                    
                    school_students[edit_roll].update({
                        "name": up_name, "father_name": up_father, "mother_name": up_mother,
                        "dob": up_dob, "class": up_cls, "total_obt": up_total_obt,
                        "total_full": up_total_full, "percentage": round(new_per, 2),
                        "result": new_res, "grade": new_grd
                    })
                    save_data(schools_db, students_db)
                    st.success("ରେକର୍ଡ ଅପଡେଟ୍ ହୋଇଗଲା!")
            else:
                st.warning("କୌଣସି ଷ୍ଟୁଡେଣ୍ଟ୍ ନାହାଁନ୍ତି।")

        with tab_list:
            st.markdown("### 📋 Student List, Search & Delete")
            school_students = students_db.get(cur_school, {})
            if school_students:
                search_query = st.text_input("🔍 Search by Name or Roll No")
                for r_no, s_info in school_students.items():
                    if search_query.lower() in r_no.lower() or search_query.lower() in s_info['name'].lower() or search_query == "":
                        cols = st.columns([3, 3, 2, 2])
                        cols[0].write(f"**Roll:** {r_no}")
                        cols[1].write(f"**Name:** {s_info['name']}")
                        if cols[3].button(f"🗑️ Delete {r_no}", key=f"del_{r_no}"):
                            del school_students[r_no]
                            save_data(schools_db, students_db)
                            st.rerun()

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

# ----------------- STUDENT LOGIN -----------------
elif menu == "Student Login":
    st.subheader("🎓 Student Portal (Result Viewer)")
    st_school_id = st.text_input("School ID", key="st_login_school")
    st_class = st.selectbox("Select Class (1 to 10)", classes_list, key="st_login_class") 
    st_roll = st.text_input("Roll Number", key="st_login_roll")
    st_dob_input = st.text_input("Date of Birth (YYYY-MM-DD)", key="st_login_dob")
    
    if st.button("View Result"):
        try:
            student = students_db[st_school_id][st_roll]
            if student["dob"] == st_dob_input and student.get("class") == st_class:
                st.success(f"Welcome KULU SUTAR! ଆପଣଙ୍କ ରେଜଲ୍ଟ୍ ତଳେ ଦିଆଗଲା:")
                school_name = schools_db[st_school_id]['name']
                
                st.markdown(generate_result_card_html(school_name, student, st_roll), unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    pdf_file = f"Result_{st_roll}.pdf"
                    create_pdf(pdf_file, school_name, student, st_roll)
                    with open(pdf_file, "rb") as f:
                        st.download_button("📥 Download PDF", f, file_name=pdf_file, mime="application/pdf", key="dl_stu")
                
                with col2:
                    if st.button("🖨️ Print Result Card", key="print_stu"):
                        components.html("<script>window.parent.print();</script>", height=0)
            
            elif student["dob"] != st_dob_input:
                st.error("ଭୁଲ୍ Date of Birth!")
            else:
                st.error("ଭୁଲ୍ Class! ଦୟାକରି ସଠିକ୍ କ୍ଲାସ୍ ବାଛନ୍ତୁ।")
        except KeyError:
            st.error("ଭୁଲ୍ School ID କିମ୍ବା Roll Number!")
