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
            cur.execute("""
                CREATE TABLE IF NOT EXISTS admin_users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(50) NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS schools (
                    id SERIAL PRIMARY KEY,
                    school_name VARCHAR(150) NOT NULL,
                    address TEXT,
                    school_id VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(50) NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id SERIAL PRIMARY KEY,
                    student_name VARCHAR(100) NOT NULL,
                    class_name VARCHAR(50) NOT NULL,
                    roll_number VARCHAR(50) NOT NULL,
                    dob DATE
                )
            """)
            cur.execute("SELECT * FROM admin_users WHERE username = 'KULU123'")
            if not cur.fetchone():
                cur.execute("INSERT INTO admin_users (username, password) VALUES ('KULU123', 'Admin@2026')")
            conn.commit()

# ୪. ମୂଳ ଆପ୍ ଡିଜାଇନ୍ (ଫଟୋ ଅନୁସାରେ ଡିଜାଇନ୍)
def main():
    create_tables()

    if "page" not in st.session_state:
        st.session_state["page"] = "Home"

    # --- ଉପର ହେଡର୍ (School Home Portal) ---
    st.markdown("""
        <div style='background-color: #0b2545; padding: 22px; border-radius: 12px; color: white; display: flex; justify-content: space-between; align-items: center;'>
            <div>
                <h1 style='margin: 0; font-size: 26px;'>🏫 SCHOOL HOME PORTAL</h1>
                <p style='margin: 4px 0 0 0; color: #8da9c4; font-size: 13px;'>Better Education • Brighter Future</p>
            </div>
            <div>
                <span style='margin-right: 15px; font-size: 14px; cursor: pointer;'>🏠 Home</span>
                <span style='margin-right: 15px; font-size: 14px; cursor: pointer;'>❓ Help</span>
                <span style='font-size: 14px; cursor: pointer;'>👤 Contact</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    # ଯଦି ୟୁଜର୍ 'Home' ପେଜ୍‌ରେ ଅଛନ୍ତି
    if st.session_state["page"] == "Home":
        
        # ଦୁଇଟି କଲମ୍: ବାମ ପଟେ ସ୍ୱାଗତ ବ୍ୟାନର୍, ଡାହାଣ ପଟେ ଲଗଇନ୍ କାର୍ଡ (ଫଟୋ ଭଳି)
        col1, col2 = st.columns([1.8, 1])
        
        with col1:
            st.markdown("""
                <div style='background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%); padding: 45px; border-radius: 16px; border: 2px dashed #0284c7; text-align: center;'>
                    <h2 style='color: #0369a1; margin-top: 0;'>🌟 Learn • Grow • Achieve • Together</h2>
                    <p style='font-size: 15px; color: #334155; line-height: 1.6;'>
                        Welcome to the advanced portal. Manage schools, student admissions, and cloud records seamlessly with high security and instant cloud storage[cite: 10].
                    </p>
                    <hr style='border: 0.5px solid #7dd3fc; margin: 20px 0;'>
                    <p style='font-style: italic; color: #0284c7; font-weight: 600;'>“Education is the key to a better tomorrow”[cite: 10]</p>
                </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown("""
                <div style='background-color: #ffffff; padding: 24px; border-radius: 16px; box-shadow: 0 6px 16px rgba(0,0,0,0.08); border: 1px solid #e2e8f0;'>
                    <h3 style='text-align: center; color: #0f172a; margin-top: 0;'>🔐 Login</h3>
                </div>
            """, unsafe_allow_html=True)
            
            login_type = st.radio("Select Login", ["Admin Login", "School Login"], horizontal=True)
            
            if login_type == "Admin Login":
                with st.form("admin_login_box"):
                    u_name = st.text_input("Master Username", placeholder="KULU123")
                    u_pass = st.text_input("Password", type="password", placeholder="Admin@2026")
                    if st.form_submit_button("Admin Login ➔", use_container_width=True):
                        if u_name == "KULU123" and u_pass == "Admin@2026":
                            st.session_state["page"] = "Admin_Dashboard"
                            st.success("ଲଗଇନ୍ ସଫଳ ହେଲା!")
                            st.rerun()
                        else:
                            st.error("ଭୁଲ Master ID କିମ୍ବା Password!")
            else:
                with st.form("school_login_box"):
                    s_code = st.text_input("School ID")
                    s_key = st.text_input("Password", type="password")
                    if st.form_submit_button("School Login ➔", use_container_width=True):
                        conn = init_connection()
                        if conn:
                            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                                cur.execute("SELECT * FROM schools WHERE school_id = %s AND password = %s", (s_code, s_key))
                                if cur.fetchone():
                                    st.success("ସ୍କୁଲ୍ ଲଗଇନ୍ ସଫଳ ହେଲା!")
                                else:
                                    st.error("ଭୁଲ School ID କିମ୍ବା Password!")

        st.markdown("<br><hr style='border: 0.5px solid #eee;'><br>", unsafe_allow_html=True)
        
        # ତଳ ପଟେ ୩ଟି ବଡ଼ ସୁନ୍ଦର କାର୍ଡ (ଫଟୋ ଅନୁସାରେ)
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.markdown("""
                <div style='background-color: #f0fdf4; padding: 25px; border-radius: 14px; text-align: center; border: 1px solid #bbf7d0; box-shadow: 0 2px 8px rgba(0,0,0,0.04);'>
                    <h2 style='margin: 0; color: #16a34a;'>🏫</h2>
                    <h4 style='color: #166534; margin: 10px 0;'>New School Registration</h4>
                    <p style='font-size: 13px; color: #475569;'>Register and add new schools directly to the cloud system[cite: 10].</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Open School Registration 📝", use_container_width=True):
                st.session_state["page"] = "New_School"
                st.rerun()
                
        with c2:
            st.markdown("""
                <div style='background-color: #eff6ff; padding: 25px; border-radius: 14px; text-align: center; border: 1px solid #bfdbfe; box-shadow: 0 2px 8px rgba(0,0,0,0.04);'>
                    <h2 style='margin: 0; color: #2563eb;'>🎓</h2>
                    <h4 style='color: #1e40af; margin: 10px 0;'>New Student Registration</h4>
                    <p style='font-size: 13px; color: #475569;'>Add student records, classes, and roll numbers securely[cite: 10].</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Open Student Registration 🎓", use_container_width=True):
                st.session_state["page"] = "New_Student"
                st.rerun()
                
        with c3:
            st.markdown("""
                <div style='background-color: #fff7ed; padding: 25px; border-radius: 14px; text-align: center; border: 1px solid #fed7aa; box-shadow: 0 2px 8px rgba(0,0,0,0.04);'>
                    <h2 style='margin: 0; color: #ea580c;'>📊</h2>
                    <h4 style='color: #9a3412; margin: 10px 0;'>Master Dashboard</h4>
                    <p style='font-size: 13px; color: #475569;'>Check live cloud counts of schools and total students[cite: 10].</p>
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
        with st.form("sch_form_main", clear_on_submit=True):
            s_name = st.text_input("School Name")
            s_addr = st.text_input("School Address")
            s_id = st.text_input("Create School ID (e.g. SCH001)")
            s_pwd = st.text_input("Create Password", type="password")
            if st.form_submit_button("Register School ✅"):
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
        with st.form("std_form_main", clear_on_submit=True):
            st_name = st.text_input("Student Name")
            st_class = st.selectbox("Select Class", ["Class 1", "Class 2", "Class 3", "Class 4", "Class 5", "Class 6", "Class 7", "Class 8", "Class 9", "Class 10"])
            st_roll = st.text_input("Roll Number")
            st_dob = st.date_input("Date of Birth")
            if st.form_submit_button("Register Student ✅"):
                if st_name and st_roll:
                    conn = init_connection()
                    if conn:
                        try:
                            with conn.cursor() as cur:
                                cur.execute("INSERT INTO students (student_name, class_name, roll_number, dob) VALUES (%s, %s, %s, %s)", (st_name, st_class, st_roll, st_dob))
                                conn.commit()
                            st.success(f"'{st_name}' ଙ୍କ ଆଡମିସନ୍ ସଫଳ ଭାବରେ ସେଭ୍ ହୋଇଗଲା!")
                        except Exception as e:
                            st.error(f"ଏରର୍: {e}")
                else:
                    st.warning("ନାମ ଏବଂ ରୋଲ୍ ନମ୍ବର ଦିଅନ୍ତୁ!")

    # --- ୩. Master Dashboard ପେଜ୍ ---
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
        st.info("ଏଠାରେ ଆପଣଙ୍କ ସମସ୍ତ ସ୍କୁଲ୍ ଏବଂ ଛାତ୍ରଛାତ୍ରୀଙ୍କର ଲାଇଭ୍ ଡାଟା ଗଣନା ଦେଖାଯାଉଛି।")

if __name__ == "__main__":
    main()
