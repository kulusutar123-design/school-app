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
            # ମାଷ୍ଟର ଆଡମିନ୍ (KULU123)
            cur.execute("SELECT * FROM admin_users WHERE username = 'KULU123'")
            if not cur.fetchone():
                cur.execute("INSERT INTO admin_users (username, password) VALUES ('KULU123', 'Admin@2026')")
            conn.commit()

def main():
    create_tables()

    # ସେସନ୍ ଷ୍ଟେଟ୍ ଇନିସিয়াଲାଇଜ୍
    if "nav" not in st.session_state:
        st.session_state["nav"] = "Home"
    if "admin_logged" not in st.session_state:
        st.session_state["admin_logged"] = False
    if "school_logged" not in st.session_state:
        st.session_state["school_logged"] = False

    # ----------------- ଉପର ହେଡର୍ (Header) -----------------
    st.markdown("""
        <div style='background-color: #0d3b66; padding: 15px; border-radius: 10px; color: white; display: flex; justify-content: space-between; align-items: center;'>
            <h2>🏫 SCHOOL HOME PORTAL</h2>
            <p style='margin: 0; font-style: italic;'>Better Education, Brighter Future</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("")

    # ଯଦି ୟୁଜର୍ 'Home' ପେଜ୍‌ରେ ଅଛନ୍ତି
    if st.session_state["nav"] == "Home":
        # ମୁଖ୍ୟ ଲେଆଉଟ୍: ଦୁଇ ଭାଗ (ବାମ ପଟେ ସ୍ୱାଗତ/ବ୍ୟାନର, ଡାହାଣ ପଟେ Login Card)
        col_left, col_right = st.columns([2, 1])

        with col_left:
            st.markdown("""
                <div style='background: linear-gradient(135deg, #f0f4f8, #d9e2ec); padding: 30px; border-radius: 15px; border-left: 6px solid #0d3b66;'>
                    <h3>🌟 Welcome to Digital School Management</h3>
                    <p>Manage your schools, student admissions, attendance, and records securely on the cloud platform.</p>
                    <p><b>✨ Features:</b> Secure Cloud Database, Instant Registration, 3D Interactive Portal.</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            st.markdown("### 📌 Quick Portal Actions")
            
            # ଫଟୋ ଭଳି ତଳେ ୩ଟି ସୁନ୍ଦର 3D ଷ୍ଟାଇଲ୍ କାର୍ଡ ବଟନ୍
            b1, b2, b3 = st.columns(3)
            with b1:
                if st.button("🏫 New School Registration", use_container_width=True):
                    st.session_state["nav"] = "New School Registration"
                    st.rerun()
            with b2:
                if st.button("🎓 New Student Registration", use_container_width=True):
                    st.session_state["nav"] = "New Student Registration"
                    st.rerun()
            with b3:
                if st.button("💰 Scholarship Portal", use_container_width=True):
                    st.session_state["nav"] = "Scholarship Portal"
                    st.rerun()

        with col_right:
            # ଫଟୋ ପରି ଡାହାଣ ପଟେ ସୁନ୍ଦର Login Box
            st.markdown("""
                <div style='background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border: 1px solid #e2e8f0;'>
                    <h3 style='text-align: center; color: #0d3b66;'>🔐 Login Portal</h3>
                    <hr style='margin: 5px 0 15px 0;'>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("👤 Admin Login", use_container_width=True, type="primary"):
                st.session_state["nav"] = "Admin Login"
                st.rerun()
                
            if st.button("🏫 School Login", use_container_width=True):
                st.session_state["nav"] = "School Login"
                st.rerun()
                
            st.markdown("<p style='text-align: center; font-size: 12px; color: gray; margin-top: 15px;'>\"Education is the key to a better tomorrow\"</p>", unsafe_allow_html=True)

    # ----------------- 1. ADMIN LOGIN PAGE -----------------
    elif st.session_state["nav"] == "Admin Login":
        if st.button("⬅️ Back to Home"):
            st.session_state["nav"] = "Home"
            st.rerun()
            
        st.subheader("👑 Master Administrator Login")
        if not st.session_state["admin_logged"]:
            with st.form("admin_login_form"):
                u_name = st.text_input("Master Username", placeholder="Enter KULU123")
                u_pass = st.text_input("Master Password", type="password", placeholder="Enter Admin@2026")
                submitted = st.form_submit_button("Login 🚀")
                if submitted:
                    conn = init_connection()
                    if conn:
                        with conn.cursor(cursor_factory=RealDictCursor) as cur:
                            cur.execute("SELECT * FROM admin_users WHERE username = %s AND password = %s", (u_name, u_pass))
                            if cur.fetchone():
                                st.session_state["admin_logged"] = True
                                st.success("ଲଗଇନ୍ ସଫଳ ହେଲା! ଡ୍ୟାସ୍‌ବୋର୍ଡକୁ ସ୍ୱାଗତ...")
                                st.rerun()
                            else:
                                st.error("ଭୁଲ Master ID କିମ୍ବା Password!")
        else:
            st.success("You are already logged in as Master Admin (KULU123)!")
            col1, col2, col3 = st.columns(3)
            col1.metric("Status", "Active")
            
            if st.button("Logout Admin"):
                st.session_state["admin_logged"] = False
                st.rerun()

    # ----------------- 2. SCHOOL LOGIN PAGE -----------------
    elif st.session_state["nav"] == "School Login":
        if st.button("⬅️ Back to Home"):
            st.session_state["nav"] = "Home"
            st.rerun()
            
        st.subheader("🏫 School Portal Login")
        with st.form("school_login_page_form"):
            s_id = st.text_input("School ID")
            s_pass = st.text_input("Password", type="password")
            s_btn = st.form_submit_button("Login to School ➡️")
            if s_btn:
                conn = init_connection()
                if conn:
                    with conn.cursor(cursor_factory=RealDictCursor) as cur:
                        cur.execute("SELECT * FROM schools WHERE school_id = %s AND password = %s", (s_id, s_pass))
                        if cur.fetchone():
                            st.success("ସ୍କୁଲ୍ ଲଗଇନ୍ ସଫଳ ହେଲା!")
                        else:
                            st.error("ଭୁଲ School ID କିମ୍ବା Password!")

    # ----------------- 3. NEW SCHOOL REGISTRATION -----------------
    elif st.session_state["nav"] == "New School Registration":
        if st.button("⬅️ Back to Home"):
            st.session_state["nav"] = "Home"
            st.rerun()
            
        st.subheader("📝 New School Registration Portal")
        with st.form("school_reg_page", clear_on_submit=True):
            sch_name = st.text_input("School Name (ସ୍କୁଲ୍ ର ନାମ)")
            sch_addr = st.text_input("School Address (ଠିକଣା)")
            sch_id = st.text_input("Create School ID (ଯେପରି: SCH001)")
            sch_pass = st.text_input("Create Password (ପାସୱାର୍ଡ)", type="password")
            
            reg_btn = st.form_submit_button("Register School ✅")
            if reg_btn:
                if sch_name and sch_id and sch_pass:
                    conn = init_connection()
                    if conn:
                        try:
                            with conn.cursor() as cur:
                                cur.execute(
                                    "INSERT INTO schools (school_name, address, school_id, password) VALUES (%s, %s, %s, %s)",
                                    (sch_name, sch_addr, sch_id, sch_pass)
                                )
                                conn.commit()
                            st.success(f"'{sch_name}' ସଫଳତାର ସହ ରେଜିଷ୍ଟର୍ ହୋଇଗଲା!")
                        except Exception as e:
                            st.error(f"ଏରର୍: ଏହି ID ଆଗରୁ ଅଛି କିମ୍ବା ସମସ୍ୟା ଘଟିଲା ({e})")
                else:
                    st.warning("ସମସ୍ତ ଫିଲ୍ଡ ପୂରଣ କରନ୍ତୁ!")

    # ----------------- 4. NEW STUDENT REGISTRATION -----------------
    elif st.session_state["nav"] == "New Student Registration":
        if st.button("⬅️ Back to Home"):
            st.session_state["nav"] = "Home"
            st.rerun()
            
        st.subheader("🎓 New Student Registration Portal")
        with st.form("student_reg_page", clear_on_submit=True):
            std_name = st.text_input("Student Name (ଛାତ୍ର/ଛାତ୍ରୀଙ୍କ ନାମ)")
            std_class = st.selectbox("Select Class (ଶ୍ରେଣୀ)", ["Class 1", "Class 2", "Class 3", "Class 4", "Class 5", "Class 6", "Class 7", "Class 8", "Class 9", "Class 10"])
            roll_no = st.text_input("Roll Number (ରୋଲ୍ ନମ୍ବର)")
            dob = st.date_input("Date of Birth (ଜନ୍ମ ତାରିଖ)")
            
            std_btn = st.form_submit_button("Register Student ✅")
            if std_btn:
                if std_name and roll_no:
                    conn = init_connection()
                    if conn:
                        try:
                            with conn.cursor() as cur:
                                cur.execute(
                                    "INSERT INTO students (student_name, class_name, roll_number, dob) VALUES (%s, %s, %s, %s)",
                                    (std_name, std_class, roll_no, dob)
                                )
                                conn.commit()
                            st.success(f"'{std_name}' ଙ୍କ ଆଡମିସନ୍ ସଫଳ ଭਾବରେ ସେଭ୍ ହୋଇଗଲା!")
                        except Exception as e:
                            st.error(f"ଏରର୍: {e}")
                else:
                    st.warning("ନାମ ଏବଂ ରୋଲ୍ ନମ୍ବର ଦିଅନ୍ତୁ!")

    # ----------------- 5. SCHOLARSHIP PORTAL -----------------
    elif st.session_state["nav"] == "Scholarship Portal":
        if st.button("⬅️ Back to Home"):
            st.session_state["nav"] = "Home"
            st.rerun()
            
        st.subheader("💰 Scholarship Portal & Details")
        st.info("ଏଠାରୁ ଛାତ୍ରଛାତ୍ରୀମାନେ ସ୍କଲାରସିପ୍ (Scholarship) ପାଇଁ ଆବେଦନ କରିପାରିବେ।")
        st.text_input("Student Roll Number")
        st.text_input("Aadhaar / ID Number")
        st.button("Check Scholarship Eligibility 🔍")

    # ଫୁଟର୍ (Footer)
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: gray;'>School Management System | Education • Discipline • Success</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
