import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import json
import os
import datetime

st.set_page_config(page_title="Advanced School Management System", layout="wide")

SCHOOLS_FILE = "schools.json"
STUDENTS_FILE = "students.txt"

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

def generate_result_card_html(school_name, st_data, roll_no):
    # ସୁନ୍ଦର ରେଜଲ୍ଟ କାର୍ଡ ଡିଜାଇନ୍ (Table & Styling)
    html = f"""
    <div style="border: 4px solid #1E3A8A; padding: 25px; border-radius: 15px; background-color: #ffffff; box-shadow: 0px 4px 8px rgba(0,0,0,0.1); font-family: sans-serif; color: #333;">
        <div style="text-align: center; border-bottom: 2px solid #1E3A8A; padding-bottom: 10px; margin-bottom: 20px;">
            <h1 style="color: #1E3A8A; margin: 0; font-size: 28px;">🏫 {school_name}</h1>
            <h3 style="color: #0284C7; margin: 5px 0 0 0;">OFFICIAL RESULT CARD</h3>
        </div>
        
        <table style="width: 100%; border: none; margin-bottom: 20px;">
            <tr>
                <td style="padding: 5px; font-size: 16px;"><b>Student Name:</b> {st_data['name']}</td>
                <td style="padding: 5px; font-size: 16px; text-align: right;"><b>Roll No:</b> {roll_no}</td>
            </tr>
            <tr>
                <td style="padding: 5px; font-size: 16px;"><b>Father's Name:</b> {st_data.get('father_name', 'N/A')}</td>
                <td style="padding: 5px; font-size: 16px; text-align: right;"><b>Class:</b> {st_data.get('class', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 5px; font-size: 16px;"><b>Mother's Name:</b> {st_data.get('mother_name', 'N/A')}</td>
                <td style="padding: 5px; font-size: 16px; text-align: right;"><b>DOB:</b> {st_data['dob']}</td>
            </tr>
        </table>

        <h4 style="color: #1E3A8A; border-bottom: 1px solid #ccc; padding-bottom: 5px;">Subject-wise Marks</h4>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;" border="1">
            <tr style="background-color: #1E3A8A; color: white;">
                <th style="padding: 10px; text-align: left;">Subject</th>
                <th style="padding: 10px; text-align: center;">Full Marks</th>
                <th style="padding: 10px; text-align: center;">Obtained Marks</th>
            </tr>
    """
    
    for sub, m_info in st_data.get('subjects', {}).items():
        html += f"""
            <tr>
                <td style="padding: 8px;"><b>{sub}</b></td>
                <td style="padding: 8px; text-align: center;">{m_info['full']}</td>
                <td style="padding: 8px; text-align: center;">{m_info['obt']}</td>
            </tr>
        """
        
    res_color = "green" if st_data.get('result') == "PASS" else "red"
    
    html += f"""
        </table>
        
        <table style="width: 100%; border-top: 2px solid #1E3A8A; padding-top: 15px; font-size: 18px;">
            <tr>
                <td><b>Total Marks:</b> {st_data.get('total_obt', 0)} / {st_data.get('total_full', 0)}</td>
                <td style="text-align: right;"><b>Percentage:</b> {st_data.get('percentage', 0)}%</td>
            </tr>
            <tr>
                <td><b>Grade:</b> <span style="color: #0284C7; font-weight: bold;">{st_data.get('grade', 'N/A')}</span></td>
                <td style="text-align: right;"><b>Final Result:</b> <span style="color: {res_color}; font-weight: bold;">{st_data.get('result', 'N/A')}</span></td>
            </tr>
        </table>
        <p style="text-align: center; margin-top: 30px; font-size: 12px; color: #777;">*This is a computer-generated document. Verified by School Management System.</p>
    </div>
    """
    return html

schools_db, students_db = load_data()

# Welcome Banner for KULU SUTAR
st.markdown("<h3 style='text-align: center; color: #0284C7;'>✨ WELCOME KULU SUTAR ✨</h3>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏫 ADVANCED SCHOOL MANAGEMENT SYSTEM</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

menu = st.sidebar.selectbox("🎯 Navigation Menu", ["Master Login", "School Login", "Student Login"])

classes_list = [str(i) for i in range(1, 11)]

# ----------------- MASTER LOGIN -----------------
if menu == "Master Login":
    st.subheader("🔑 Master Administrator Login")
    m_user = st.text_input("Master Username")
    m_pass = st.text_input("Master Password", type="password")
    
    if st.button("Login as Master"):
        if m_user == "master" and m_pass == "master123":
            st.success("Welcome KULU SUTAR! ମାଷ୍ଟର୍ ଲଗ୍ଇନ୍ ସଫଳ ହେଲା!")
            st.session_state['master_logged'] = True
        else:
            st.error("ଭୁଲ୍ Master ID କିମ୍ବା Password!")

    if st.session_state.get('master_logged', False):
        st.markdown("---")
        tab1, tab2, tab3 = st.tabs(["Register School", "Manage / Forgot School Password", "Student Records & Reports"])
        
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
                    st.warning("ସମସ୍ତ ଫିଲ୍ଡ ପୂରଣ କରନ୍ତୁ।")
                    
        with tab2:
            st.markdown("### 🔄 Forgot / Reset School Password")
            selected_school = st.selectbox("Select School ID", list(schools_db.keys()))
            st.write(f"Current School Name: **{schools_db[selected_school]['name']}**")
            new_reset_pass = st.text_input("Enter New Password for this School", type="password", key="m_reset_p")
            if st.button("Update / Reset Password"):
                if new_reset_pass:
                    schools_db[selected_school]['pass'] = new_reset_pass
                    save_data(schools_db, students_db)
                    st.success("School password ଫର୍ଗେଟ୍/ଚେଞ୍ଜ୍ ସଫଳତାର ସହ ହୋଇଗଲା!")
                else:
                    st.warning("ନୂତନ ପାସୱାର୍ଡ ଦିଅନ୍ତୁ।")

        with tab3:
            st.markdown("### 📊 All Schools & Students Overview")
            st.write(students_db)

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
        st.info(f"Connected School: **{schools_db[cur_school]['name']}** (ID: {cur_school})")
        
        tab_add, tab_edit, tab_list, tab_report = st.tabs(["Add/Save Student", "Edit/Update by Roll No", "Student List & Search", "Generate & Print Report"])
        
        with tab_add:
            st.markdown("### 📝 Student Registration & Subject Marks Entry")
            roll_no = st.text_input("Roll No", key="add_roll")
            st_name = st.text_input("Student Name", key="add_name")
            father_name = st.text_input("Father's Name", key="add_father")
            mother_name = st.text_input("Mother's Name", key="add_mother")
            
            # DOB ରେଞ୍ଜ୍: 2000 ରୁ 2065
            min_date = datetime.date(2000, 1, 1)
            max_date = datetime.date(2065, 12, 31)
            dob = st.date_input("DOB (2000-2065)", min_value=min_date, max_value=max_date, key="add_dob")
            
            cls = st.selectbox("Class", classes_list, key="add_class")
            
            st.markdown("#### 📚 Nijara Ichha Mutabaka Subject Add / Remove & Marks")
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
                    f_mark = st.number_input(f"Full Mark", value=100.0, key=f"f_mark_{i}")
                with c3:
                    o_mark = st.number_input(f"Obtained Mark", value=0.0, key=f"o_mark_{i}")
                
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
                            "name": st_name,
                            "father_name": father_name,
                            "mother_name": mother_name,
                            "dob": str(dob),
                            "class": cls,
                            "subjects": subjects_data,
                            "total_full": total_full_mark,
                            "total_obt": total_obt_mark,
                            "percentage": round(percentage, 2),
                            "result": result,
                            "grade": grade
                        }
                        save_data(schools_db, students_db)
                        st.success(f"Roll No {roll_no} ({st_name}) ସଫଳତାର ସହ ସେଭ୍ ହୋଇଗଲା!")
                    else:
                        st.error("Roll No ଏବଂ Student Name ଦିଅନ୍ତୁ।")
            with c_clear:
                if st.button("🧹 Clear Form"):
                    st.rerun()

        with tab_edit:
            st.markdown("### ✏️ Edit / Update Student Record")
            school_students = students_db.get(cur_school, {})
            if school_students:
                edit_roll = st.selectbox("Select Roll No to Load & Edit", list(school_students.keys()), key="edit_roll_sel")
                curr_st = school_students[edit_roll]
                
                up_name = st.text_input("Edit Student Name", value=curr_st['name'], key="up_n")
                up_father = st.text_input("Edit Father's Name", value=curr_st.get('father_name', ''), key="up_f")
                up_mother = st.text_input("Edit Mother's Name", value=curr_st.get('mother_name', ''), key="up_m")
                up_dob = st.text_input("Edit DOB (YYYY-MM-DD)", value=curr_st['dob'], key="up_d")
                
                cls_val = curr_st.get('class', '1')
                cls_index = classes_list.index(cls_val) if cls_val in classes_list else 0
                up_cls = st.selectbox("Edit Class", classes_list, index=cls_index, key="up_c")
                
                up_total_obt = st.number_input("Update Total Obtained Marks", value=float(curr_st.get('total_obt', 0)), key="up_obt")
                up_total_full = st.number_input("Update Total Full Marks", value=float(curr_st.get('total_full', 300)), key="up_full")
                
                if st.button("💾 Save Updated Record"):
                    new_per = (up_total_obt / up_total_full * 100) if up_total_full > 0 else 0.0
                    new_res = "PASS" if new_per >= 30 else "FAIL"
                    new_grd = "A+" if new_per >= 90 else "A" if new_per >= 80 else "B" if new_per >= 60 else "C" if new_per >= 40 else "D" if new_per >= 30 else "F"
                    
                    school_students[edit_roll].update({
                        "name": up_name,
                        "father_name": up_father,
                        "mother_name": up_mother,
                        "dob": up_dob,
                        "class": up_cls,
                        "total_obt": up_total_obt,
                        "total_full": up_total_full,
                        "percentage": round(new_per, 2),
                        "result": new_res,
                        "grade": new_grd
                    })
                    save_data(schools_db, students_db)
                    st.success(f"Roll No {edit_roll} ସଫଳତାର ସହ ଅପଡେଟ୍ ହୋଇଗଲା!")
            else:
                st.warning("କୌଣସି ଷ୍ଟୁଡେଣ୍ଟ୍ ରେକର୍ଡ ନାହିଁ।")

        with tab_list:
            st.markdown("### 📋 Student List, Search & Delete")
            school_students = students_db.get(cur_school, {})
            if school_students:
                search_query = st.text_input("🔍 Search by Name or Roll No")
                
                st.write("---")
                for r_no, s_info in school_students.items():
                    if search_query.lower() in r_no.lower() or search_query.lower() in s_info['name'].lower() or search_query == "":
                        cols = st.columns([3, 3, 2, 2])
                        cols[0].write(f"**Roll:** {r_no}")
                        cols[1].write(f"**Name:** {s_info['name']}")
                        cols[2].write(f"**Result:** {s_info.get('result', 'N/A')}")
                        if cols[3].button(f"🗑️ Delete {r_no}", key=f"del_{r_no}"):
                            del school_students[r_no]
                            save_data(schools_db, students_db)
                            st.success(f"Roll No {r_no} ଡିଲିଟ୍ ହୋଇଗଲା!")
                            st.rerun()
            else:
                st.warning("କୌଣସି ଷ୍ଟୁଡେଣ୍ଟ୍ ନାହାଁନ୍ତି।")

        with tab_report:
            st.markdown("### 🖨️ Generate & Print Report Cards")
            school_students = students_db.get(cur_school, {})
            if school_students:
                rep_roll = st.selectbox("Select Student Roll No for Report", list(school_students.keys()), key="rep_sel")
                st_data = school_students[rep_roll]
                
                school_name = schools_db[cur_school]['name']
                # Call styled HTML function
                st.markdown(generate_result_card_html(school_name, st_data, rep_roll), unsafe_allow_html=True)
                
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    if st.button("📥 Generate PDF Report", key="pdf_school"):
                        pdf_filename = f"Report_{rep_roll}.pdf"
                        c = canvas.Canvas(pdf_filename, pagesize=letter)
                        c.drawString(100, 750, f"School: {school_name}")
                        c.drawString(100, 730, f"Student Name: {st_data['name']} (Roll: {rep_roll})")
                        c.drawString(100, 710, f"Father: {st_data.get('father_name', '')} | Mother: {st_data.get('mother_name', '')}")
                        c.drawString(100, 680, f"Total Marks: {st_data.get('total_obt')} / {st_data.get('total_full')}")
                        c.drawString(100, 660, f"Percentage: {st_data.get('percentage')}% | Result: {st_data.get('result')}")
                        c.save()
                        with open(pdf_filename, "rb") as f:
                            st.download_button("📥 Click Here to Download PDF", f, file_name=pdf_filename, mime="application/pdf")
                with c_btn2:
                    if st.button("🖨️ Print Report Card", key="print_school"):
                        st.markdown("<script>window.print();</script>", unsafe_allow_html=True)
            else:
                st.warning("ରିପୋର୍ଟ ଜେନେରେଟ୍ କରିବା ପାଇଁ କୌଣସି ଷ୍ଟୁଡେଣ୍ଟ୍ ନାହାଁନ୍ତି।")

# ----------------- STUDENT LOGIN -----------------
elif menu == "Student Login":
    st.subheader("🎓 Student Portal (Result & Report Card Viewer)")
    st_school_id = st.text_input("School ID", key="st_login_school")
    st_class = st.selectbox("Select Class (1 to 10)", classes_list, key="st_login_class") 
    st_roll = st.text_input("Roll Number", key="st_login_roll")
    st_dob_input = st.text_input("Date of Birth (YYYY-MM-DD)", key="st_login_dob")
    
    if st.button("View Result"):
        try:
            student = students_db[st_school_id][st_roll]
            
            if student["dob"] == st_dob_input and student.get("class") == st_class:
                st.success(f"Welcome KULU SUTAR! ସ୍ୱାଗତମ୍ {student['name']}! ଆପଣଙ୍କ ରେଜଲ୍ଟ୍ ତଳେ ଦିଆଗଲା:")
                
                school_name = schools_db[st_school_id]['name']
                # Show Styled Report Card
                st.markdown(generate_result_card_html(school_name, student, st_roll), unsafe_allow_html=True)
                
                # Student Print & PDF Buttons
                col1, col2 = st.columns(2)
                with col1:
                    # Fix PDF Generation for Student
                    pdf_filename = f"Result_{st_roll}.pdf"
                    c = canvas.Canvas(pdf_filename, pagesize=letter)
                    c.drawString(100, 750, f"School: {school_name}")
                    c.drawString(100, 730, f"Student Result: {student['name']} (Roll: {st_roll})")
                    c.drawString(100, 710, f"Father: {student.get('father_name', '')} | Mother: {student.get('mother_name', '')}")
                    c.drawString(100, 680, f"Total Marks: {student.get('total_obt')} / {student.get('total_full')}")
                    c.drawString(100, 660, f"Percentage: {student.get('percentage')}% | Result: {student.get('result')}")
                    c.save()
                    
                    with open(pdf_filename, "rb") as f:
                        st.download_button("📥 Download PDF", f, file_name=pdf_filename, mime="application/pdf", key="st_pdf_btn")
                
                with col2:
                    # Added Print Button for Student
                    if st.button("🖨️ Print Result Card", key="st_print_btn"):
                        st.markdown("<script>window.print();</script>", unsafe_allow_html=True)
            
            elif student["dob"] != st_dob_input:
                st.error("ଭୁଲ୍ Date of Birth! ଫର୍ମାଟ୍ ଧ୍ୟାନ ରଖନ୍ତୁ: YYYY-MM-DD (ଉଦାହରଣ: 2008-05-12)")
            else:
                st.error("ଭୁଲ୍ Class! ଦୟାକରି ସଠିକ୍ କ୍ଲାସ୍ ବାଛନ୍ତୁ।")
        except KeyError:
            st.error("ଭୁଲ୍ School ID କିମ୍ବା Roll Number!")
