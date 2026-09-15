import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import json
import os

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
            students = {
                "S001": {
                    "101": {
                        "name": "Amit Kumar Sutar",
                        "father_name": "Jaganath Sutar",
                        "mother_name": "Basanti Sutar",
                        "dob": "2008-05-12",
                        "class": "10",
                        "subjects": {"Odia": {"full": 100, "obt": 85}, "English": {"full": 100, "obt": 78}, "Math": {"full": 100, "obt": 90}},
                        "total_full": 300,
                        "total_obt": 253,
                        "percentage": 84.33,
                        "result": "PASS",
                        "grade": "A"
                    }
                }
            }
    else:
        students = {
            "S001": {
                "101": {
                    "name": "Amit Kumar Sutar",
                    "father_name": "Jaganath Sutar",
                    "mother_name": "Basanti Sutar",
                    "dob": "2008-05-12",
                    "class": "10",
                    "subjects": {"Odia": {"full": 100, "obt": 85}, "English": {"full": 100, "obt": 78}, "Math": {"full": 100, "obt": 90}},
                    "total_full": 300,
                    "total_obt": 253,
                    "percentage": 84.33,
                    "result": "PASS",
                    "grade": "A"
                }
            }
        }
    return schools, students

def save_data(schools, students):
    with open(SCHOOLS_FILE, "w", encoding="utf-8") as f:
        json.dump(schools, f, indent=4)
    with open(STUDENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(students, f, indent=4)

schools_db, students_db = load_data()

# Welcome Banner for KULU SUTAR
st.markdown("<h3 style='text-align: center; color: #0284C7;'>✨ WELCOME KULU SUTAR ✨</h3>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏫 ADVANCED SCHOOL MANAGEMENT SYSTEM</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

menu = st.sidebar.selectbox("🎯 Navigation Menu", ["Master Login", "School Login", "Student Login"])

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
    st.subheader("🏫 School Portal (No Forgot Password option here)")
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
            dob = st.date_input("DOB", key="add_dob")
            cls = st.text_input("Class", key="add_class")
            
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
                        st.success(f"Roll No {roll_no} ({st_name}) ସଫଳତାର ସହ `students.txt` ରେ ସେଭ୍ ହୋଇଗଲା!")
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
                up_cls = st.text_input("Edit Class", value=curr_st['class'], key="up_c")
                
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
                
                st.markdown(f"""
                <div style="border: 2px solid #1E3A8A; padding: 20px; border-radius: 10px; background-color: #f9f9f9;">
                    <h2 style="text-align: center; color: #1E3A8A;">{schools_db[cur_school]['name']}</h2>
                    <h4 style="text-align: center; color: #555;">Official Statement of Marks</h4>
                    <hr>
                    <p><b>Student Name:</b> {st_data['name']} &nbsp;&nbsp;&nbsp;&nbsp; <b>Roll No:</b> {rep_roll}</p>
                    <p><b>Father's Name:</b> {st_data.get('father_name', 'N/A')} &nbsp;&nbsp;&nbsp;&nbsp; <b>Mother's Name:</b> {st_data.get('mother_name', 'N/A')}</p>
                    <p><b>DOB:</b> {st_data['dob']} &nbsp;&nbsp;&nbsp;&nbsp; <b>Class:</b> {st_data['class']}</p>
                    <hr>
                    <h4>Subject-wise Performance:</h4>
                """, unsafe_allow_html=True)
                
                for sub, m_info in st_data.get('subjects', {}).items():
                    st.write(f"- **{sub}**: Full Mark: {m_info['full']} | Obtained Mark: {m_info['obt']}")
                
                st.markdown(f"""
                    <hr>
                    <p><b>Total Marks:</b> {st_data.get('total_obt', 0)} / {st_data.get('total_full', 0)}</p>
                    <p><b>Percentage:</b> {st_data.get('percentage', 0)}% &nbsp;&nbsp;&nbsp;&nbsp; <b>Grade:</b> {st_data.get('grade', 'N/A')}</p>
                    <p><b>Final Result:</b> <span style="color: green; font-weight: bold;">{st_data.get('result', 'N/A')}</span></p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("📥 Generate PDF Report"):
                    pdf_filename = f"Report_{rep_roll}.pdf"
                    c = canvas.Canvas(pdf_filename, pagesize=letter)
                    c.drawString(100, 750, f"School: {schools_db[cur_school]['name']}")
                    c.drawString(100, 730, f"Student Name: {st_data['name']} (Roll: {rep_roll})")
                    c.drawString(100, 710, f"Father: {st_data.get('father_name', '')} | Mother: {st_data.get('mother_name', '')}")
                    c.drawString(100, 680, f"Total Marks: {st_data.get('total_obt')} / {st_data.get('total_full')}")
                    c.drawString(100, 660, f"Percentage: {st_data.get('percentage')}% | Result: {st_data.get('result')}")
                    c.save()
                    
                    with open(pdf_filename, "rb") as f:
                        st.download_button("📥 Click Here to Download PDF Report", f, file_name=pdf_filename, mime="application/pdf")
                
                if st.button("🖨️ Print Report Card"):
                    st.markdown("<script>window.print();</script>", unsafe_allow_html=True)
                    st.success("Print command sent to browser!")
            else:
                st.warning("ରିପୋର୍ଟ ଜେନେରେଟ୍ କରିବା ପାଇଁ କୌଣସି ଷ୍ଟୁଡେଣ୍ଟ୍ ନାହାଁନ୍ତି।")

# ----------------- STUDENT LOGIN (Result & Report Card Viewer) -----------------
elif menu == "Student Login":
    st.subheader("🎓 Student Portal (Result & Report Card Viewer)")
    st_school_id = st.text_input("School ID", key="st_login_school")
    st_roll = st.text_input("Roll Number", key="st_login_roll")
    st_dob_input = st.text_input("Date of Birth (YYYY-MM-DD)", key="st_login_dob")
    
    if st.button("View Result"):
        try:
            student = students_db[st_school_id][st_roll]
            if student["dob"] == st_dob_input:
                st.success(f"Welcome KULU SUTAR! ସ୍ୱାଗତମ୍ {student['name']}! ଆପଣଙ୍କ ରେଜଲ୍ଟ୍ ତଳେ ଦିଆଗଲା:")
                
                st.markdown(f"""
                <div style="border: 2px solid #1E3A8A; padding: 20px; border-radius: 10px; background-color: #f9f9f9;">
                    <h3 style="text-align: center; color: #1E3A8A;">RESULT CARD</h3>
                    <p><b>Student Name:</b> {student['name']} &nbsp;&nbsp;&nbsp;&nbsp; <b>Roll No:</b> {st_roll}</p>
                    <p><b>Father's Name:</b> {student.get('father_name', 'N/A')} &nbsp;&nbsp;&nbsp;&nbsp; <b>Mother's Name:</b> {student.get('mother_name', 'N/A')}</p>
                    <p><b>DOB:</b> {student['dob']} &nbsp;&nbsp;&nbsp;&nbsp; <b>Class:</b> {student['class']}</p>
                    <hr>
                    <h4>Subject Marks:</h4>
                """, unsafe_allow_html=True)
                
                for sub, m_info in student.get('subjects', {}).items():
                    st.write(f"- **{sub}**: Full Mark: {m_info['full']} | Obtained Mark: {m_info['obt']}")
                
                st.markdown(f"""
                    <hr>
                    <p><b>Total Marks:</b> {student.get('total_obt', 0)} / {student.get('total_full', 0)}</p>
                    <p><b>Percentage:</b> {student.get('percentage', 0)}% &nbsp;&nbsp;&nbsp;&nbsp; <b>Grade:</b> {student.get('grade', 'N/A')}</p>
                    <p><b>Final Result:</b> <span style="color: green; font-weight: bold;">{student.get('result', 'N/A')}</span></p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("📥 Download Result PDF"):
                    filename = f"Result_{st_roll}.pdf"
                    c = canvas.Canvas(filename, pagesize=letter)
                    c.drawString(100, 750, f"Student Result: {student['name']}")
                    c.drawString(100, 730, f"Roll No: {st_roll} | Class: {student['class']}")
                    c.drawString(100, 700, f"Total Marks: {student.get('total_obt')} / {student.get('total_full')}")
                    c.drawString(100, 680, f"Percentage: {student.get('percentage')}% | Result: {student.get('result')}")
                    c.save()
                    
                    with open(filename, "rb") as f:
                        st.download_button("📥 Click Here to Download PDF", f, file_name=filename, mime="application/pdf")
            else:
                st.error("ଭୁଲ୍ Date of Birth!")
        except KeyError:
            st.error("ଭୁଲ୍ School ID କିମ୍ବା Roll Number!")
