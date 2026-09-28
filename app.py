import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor

# ୧. ପୃଷ୍ଠା ସେଟିଂସ୍
st.set_page_config(page_title="School Home Portal", page_icon="🏫", layout="wide")

# ୨. କ୍ଲାଉଡ୍ ଡାଟାବେସ୍ କନେକ୍ସନ୍
@st.cache_resource
def init_connection():
    try:
        return psycopg2.connect(st.secrets["DATABASE_URL"], sslmode='require')
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return None

# ୩. ଡାଟାବେସ୍ ଟେବୁଲ୍ ପ୍ରସ୍ତୁତି
def create_tables():
    conn = init_connection()
    if conn is not None:
        with conn.cursor() as cur:
            # ଆଡମିନ୍ ଟେବୁଲ୍
            cur.execute("""
                CREATE TABLE IF NOT EXISTS admin_users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(50) NOT NULL
                )
            """)
            # ସ୍କୁଲ୍ ରେଜିଷ୍ଟ୍ରେସନ୍ ଟେବୁଲ୍
            cur.execute("""
                CREATE TABLE IF NOT EXISTS schools (
                    id SERIAL PRIMARY KEY,
                    school_name VARCHAR(150) NOT NULL,
                    address TEXT,
                    school_id VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(50) NOT NULL
                )
            """)
            # ଷ୍ଟୁଡେଣ୍ଟ୍ ରେଜିଷ୍ଟ୍ରେସନ୍ ଟେବୁଲ୍
            cur.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id SERIAL PRIMARY KEY,
                    student_name VARCHAR(100) NOT NULL,
                    class_name VARCHAR(50) NOT NULL,
                    roll_number VARCHAR(50) NOT NULL,
                    dob DATE
                )
            """)
            # ମାଷ୍ଟର ଆଡମିନ୍ (KULU123) ସେଟଅପ୍
            cur.execute("SELECT * FROM admin_users WHERE username = 'KULU123'")
            if not cur.fetchone():
                cur.execute("INSERT INTO admin_users (username, password) VALUES ('KULU123', 'Admin@2026')")
            conn.commit()

# ୪. ମୂଳ ଆପ୍ ଡିଜାଇନ୍ (ଫଟୋ ଅନୁସାରେ)
def main():
    create_tables()

    # ସେସନ୍ ଷ୍ଟେଟ୍ ପାଇଁ
    if "page" not in st.session_state:
        st.session_state["page"] = "Home"

    # --- ଉପର ହେଡର୍ (School Home Portal Header) ---
    st.markdown("""
        <div style='background-color: #0d233a; padding: 20px; border-radius: 10px; color: white;'>
            <h1 style='margin: 0; font-size: 28px;'>🏫 SCHOOL HOME PORTAL</h1>
            <p style='margin: 5px 0 0 0; color: #a0c4ff; font-size: 14px;'>Better Education • Brighter Future</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    # ଯଦି ୟୁଜର୍ 'Home' ପେଜ୍‌ରେ ଅଛନ୍ତି
    if st.session_state["page"] == "Home":
        
        # ମୁଖ୍ୟ ଲେଆଉଟ୍: ଦୁଇଟି କอลମ୍ (ବାମ ପଟେ ସ୍ୱାଗତ ବାର୍ତ୍ତା/ବ୍ୟାନର୍, ଡାହାଣ ପଟେ ଲଗଇନ୍ କାର୍ଡ)
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
                <div style='background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); padding: 40px; border-radius: 15px; text-align: center; border: 2px dashed #0d233a;'>
                    <h2 style='color: #0d233a;'>🌟 Welcome to Smart School Portal</h2>
                    <p style='font-size: 16px; color: #333;'>Education is the key to a better tomorrow. Manage schools, student admissions, and records securely on the cloud!</p>
                    <hr style='border: 1px solid #ccc;'>
                    <p style='font-style: italic; color: #555;'>“Learn • Grow • Achieve • Together”</p>
                </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown("""
                <div style='background-color: #ffffff; padding: 25px; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border: 1px solid #e0e0e0;'>
                    <h3 style='text-align: center; color: #0d233a;'>🔐 Login Portal</h3>
                </div>
            """, unsafe_allow_html=True)
            
            login_type = st.radio("Select Login Type", ["Admin Login", "School Login"], horizontal=True)
            
            if login_type == "Admin Login":
                with st.form("admin_login_form"):
                    adm_user = st.text_input("Master Username", placeholder="KULU123")
                    adm_pass = st.text_input("Password", type="password", placeholder="Admin@2026")
                    adm_btn = st.form_submit_button("Admin Login ➔", use_container_width=True)
                    if adm_btn:
                        if adm_user == "KULU123" and adm_pass == "Admin@2026":
                            st.session_state["page"] = "Admin_Dashboard"
                            st.success("ଲଗଇନ୍ ସଫଳ ହେଲା!")
                            st.rerun()
                        else:
                            st.error("ଭୁଲ Master ID କିମ୍ବା Password!")
                            
            else:
                with st.form("school_login_form"):
                    sch_usr = st.text_input("School ID")
                    sch_pwd = st.text_input("Password", type="password")
                    sch_btn = st.form_submit_button("School Login ➔", use_container_width=True)
                    if sch_btn:
                        conn = init_connection()
                        if conn:
                            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                                cur.execute("SELECT * FROM schools WHERE school_id = %s AND password = %s", (sch_usr, sch_pwd))
                                if cur.fetchone():
                                    st.success("ସ୍କୁଲ୍ ଲଗଇନ୍ ସଫଳ ହେଲା!")
                                else:
                                    st.error("ଭୁଲ School ID କିମ୍ବା Password!")

        st.markdown("<br><hr><br>", unsafe_allow_html=True)
        
        # ତଳ ପଟେ ୩ଟି ବଡ଼ କାର୍ଡ (New School, New Student, Scholarship/Dashboard) - ଫଟୋ ଅନୁସାରେ
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            st.markdown("""
                <div style='background-color: #e3f2fd; padding: 25px; border-radius: 12px; text-align: center; border-left: 6px solid #1976d2;'>
                    <h3>🏫</h3>
                    <h4>New School Registration</h4>
                    <p style='font-size: 13px; color: #666;'>Add and register new schools to the cloud network easily.</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Open School Registration 📝", use_container_width=True):
                st.session_state["page"] = "New_School"
                st.rerun()
                
        with col_b:
            st.markdown("""
                <div style='background-color: #e8f5e9; padding: 25px; border-radius: 12px; text-align: center; border-left: 6px solid #388e3c;'>
                    <h3>🎓</h3>
                    <h4>New Student Registration</h4>
                    <p style='font-size: 13px; color: #666;'>Register student details, classes, and roll numbers securely.</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Open Student Registration 🎓", use_container_width=True):
                st.session_state["page"] = "New_Student"
                st.rerun()
                
        with col_c:
            st.markdown("""
                <div style='background-color: #fff3e0; padding: 25px; border-radius: 12px; text-align: center; border-left: 6px solid #f57c00;'>
                    <h3>📊</h3>
                    <h4>Master Dashboard</h4>
                    <p style='font-size: 13px; color: #666;'>View total registered schools and student counts instantly.</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Open Master Dashboard ⚙️", use_container_width=True):
                st.session_state["page"] = "Admin_Dashboard"
                st.rerun()

    # --- ୧. New School Registration ପେଜ୍ ---
    elif st.session_state["page"] == "New_School":
        if st.button("⬅️ Back to Home"):
            st.session_state["page"] = "Home"
            st.rerun()
            
        st.subheader("📝 New School Registration Portal")
        with st.form("reg_sch_form", clear_on_submit=True):
            s_name = st.text_input("School Name")
            s_addr = st.text_input("School Address")
            s_id = st.text_input("Create School ID (e.g. SCH001)")
            s_pwd = st.text_input("Create Password", type="password")
            submit_s = st.form_submit_button("Register School ✅")
            
            if submit_s:
                if s_name and s_id and s_pwd:
                    conn = init_connection()
                    if conn:
                        try:
                            with conn.cursor() as cur:
                                cur.execute("INSERT INTO schools (school_name, address, school_id, password) VALUES (%s, %s, %s, %s)", (s_name, s_addr, s_id, s_pwd))
                                conn.commit()
                            st.success(f"'{s_name}' ସଫଳତାର ସହ ରେଜିଷ୍ଟର୍ ହୋଇଗଲା!")
                        except Exception as e:
                            st.error(f"ଏରର୍: {e}")
                else:
                    st.warning("ସମସ୍ତ ଫିଲ୍ଡ ପୂରଣ କରନ୍ତୁ!")

    # --- ୨. New Student Registration ପେଜ୍ ---
    elif st.session_state["page"] == "New_Student":
        if st.button("⬅️ Back to Home"):
            st.session_state["page"] = "Home"
            st.rerun()
            
        st.subheader("🎓 New Student Admission Portal")
        with st.form("reg_std_form", clear_on_submit=True):
            st_name = st.text_input("Student Name")
            st_class = st.selectbox("Select Class", ["Class 1", "Class 2", "Class 3", "Class 4", "Class 5", "Class 6", "Class 7", "Class 8", "Class 9", "Class 10"])
            st_roll = st.text_input("Roll Number")
            st_dob = st.date_input("Date of Birth")
            submit_st = st.form_submit_button("Register Student ✅")
            
            if submit_st:
                if st_name and st_roll:
                    conn = init_connection()
                    if conn:
                        try:
                            with conn.cursor() as cur:
                                cur.execute("INSERT INTO students (student_name, class_name, roll_number, dob) VALUES (%s, %s, %s, %s)", (st_name, st_class, st_roll, st_dob))
                                conn.commit()
                            st.success(f"'{st_name}' ଙ୍କ ଆଡମିସନ୍ ସଫଳ ଭաբରେ ସେଭ୍ ହୋଇଗଲା!")
                        except Exception as e:
                            st.error(f"ଏରର୍: {e}")
                else:
                    st.warning("ନାମ ଏବଂ ରୋଲ୍ ନମ୍ବର ଦିଅନ୍ତୁ!")

    # --- ୩. Admin Dashboard ପେଜ୍ ---
    elif st.session_state["page"] == "Admin_Dashboard":
        if st.button("⬅️ Back to Home"):
            st.session_state["page"] = "Home"
            st.rerun()
            
        st.subheader("👑 Master Administrator Dashboard")
        
        conn = init_connection()
        tot_sch = 0
        tot_std = 0
        if conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM schools")
                r1 = cur.fetchone()
                if r1: tot_sch = r1[0]
                
                cur.execute("SELECT COUNT(*) FROM students")
                r2 = cur.fetchone()
                if r2: tot_std = r2[0]
                
        col1, col2, col3 = st.columns(3)
        col1.metric("🏫 Total Registered Schools", tot_sch)
        col2.metric("🎓 Total Students Enrolled", tot_std)
        col3.metric("👑 Admin Status", "Online")
        
        st.markdown("---")
        st.info("ଏଠାରୁ ଆପଣ ସମସ୍ତ ଡାଟା ଉପରେ ନଜର ରଖିପାରିବେ।")

if __name__ == "__main__":
    main()
