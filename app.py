import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor

# ୧. ପୃଷ୍ଠା ସେଟିଂସ୍ (Wide Layout)
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

# ୪. ଲଗଇନ୍ ଯାଞ୍ଚ ପ୍ରଣାଳୀ
def check_admin_login(username, password):
    conn = init_connection()
    if conn is not None:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM admin_users WHERE username = %s AND password = %s", (username, password))
            return cur.fetchone() is not None
    return False

# ୫. ମୂଳ ଆପ୍ (Home Portal & Navigation)
def main():
    create_tables()

    # ସେସନ୍ ଷ୍ଟେଟ୍ ଇନିସିଆଲାଇଜ୍
    if "page" not in st.session_state:
        st.session_state["page"] = "Home"
    if "admin_logged_in" not in st.session_state:
        st.session_state["admin_logged_in"] = False
    if "school_logged_in" not in st.session_state:
        st.session_state["school_logged_in"] = False

    # --- ୧. SCHOOL HOME PORTAL (ମେନ୍ ପେଜ୍) ---
    if st.session_state["page"] == "Home":
        # ଉପର ହେଡର୍
        col_h1, col_h2 = st.columns([4, 1])
        with col_h1:
            st.markdown("## 🏫 SCHOOL HOME PORTAL")
            st.caption("Better Education • Brighter Future")
        with col_h2:
            st.markdown("<br>🏠 **Home** | ❓ **Help** | 📞 **Contact**", unsafe_allow_html=True)
        
        st.markdown("---")

        # ମୁଖ୍ୟ ଲେଆଉଟ୍: ବାମ ପଟେ ବ୍ୟାନର/ଟେକ୍ସଟ୍, ଡାହାଣ ପଟେ Login Box (ଫଟୋ ଅନୁସାରେ)
        left_col, right_col = st.columns([2, 1])

        with left_col:
            st.info("👋 ସ୍ୱାଗତମ୍! ଏହା ହେଉଛି ଆପଣଙ୍କର ଅନ୍‌ଲାଇନ୍ ସ୍କୁଲ୍ ମ୍ୟାନେଜ୍‌ମେଣ୍ଟ୍ ପୋର୍ଟାଲ୍।")
            st.markdown("""
                ### 🌟 Our Key Features:
                * **Easy School Management:** ସମସ୍ତ ସ୍କୁଲ୍ ତଥ୍ୟ ଏବଂ ଛାତ୍ରଛାତ୍ରୀଙ୍କ ରେକର୍ଡ ସୁରକ୍ଷିତ ଭାବରେ ସଂରକ୍ଷଣ କରନ୍ତୁ।
                * **Cloud Database:** ଆପଣଙ୍କ ଡାଟା କ୍ଲାଉଡ୍‌ରେ ୨୪ ଘଣ୍ଟା ସୁରକ୍ଷିତ ରହିବ, କେବେ ବି ଉଡ଼ିବ ନାହିଁ।
            """)

        with right_col:
            st.markdown("### 🔐 Login Portal")
            # ଫଟୋରେ ଥିବା ବଟନ୍ ଭଳି ଦୁଇଟି ବଟନ୍
            if st.button("🟢 Admin Login", use_container_width=True):
                st.session_state["page"] = "Admin_Login"
                st.rerun()
            
            if st.button("🔵 School Login", use_container_width=True):
                st.session_state["page"] = "School_Login"
                st.rerun()

        st.markdown("---")
        st.markdown("### 📌 Quick Services")
        
        # ତଳେ ଥିବା ୩ଟି କାର୍ଡ/ବଟନ୍ (New School, New Student, Scholarship)
        q1, q2, q3 = st.columns(3)
        with q1:
            if st.button("🏫 New School Registration", use_container_width=True):
                st.session_state["page"] = "New_School"
                st.rerun()
        with q2:
            if st.button("🎓 New Student Registration", use_container_width=True):
                st.session_state["page"] = "New_Student"
                st.rerun()
        with q3:
            if st.button("📜 Scholarship Portal", use_container_width=True):
                st.session_state["page"] = "Scholarship"
                st.rerun()

    # --- ୨. ADMIN LOGIN PAGE ---
    elif st.session_state["page"] == "Admin_Login":
        if st.button("⬅️ Back to Home"):
            st.session_state["page"] = "Home"
            st.rerun()
            
        st.markdown("### 👑 Master Administrator Login")
        if not st.session_state["admin_logged_in"]:
            with st.form("admin_login_form"):
                u_name = st.text_input("Master Username", placeholder="Enter KULU123")
                u_pass = st.text_input("Master Password", type="password", placeholder="Enter Admin@2026")
                submitted = st.form_submit_button("Login 🚀")
                if submitted:
                    if check_admin_login(u_name, u_pass):
                        st.session_state["admin_logged_in"] = True
                        st.success("ଲଗଇନ୍ ସଫଳ ହେଲା!")
                        st.rerun()
                    else:
                        st.error("ଭୁଲ Master ID କିମ୍ବା Password!")
        else:
            st.success("ଆପଣ ପୂର୍ବରୁ ଆଡମିନ୍ ଭାବରେ ଲଗଇନ୍ ଅଛନ୍ତି!")
            if st.button("Go to Admin Dashboard ➡️"):
                st.session_state["page"] = "Admin_Dashboard"
                st.rerun()
            if st.button("Logout"):
                st.session_state["admin_logged_in"] = False
                st.rerun()

    # --- ୩. ADMIN DASHBOARD (ଆଡମିନ୍ ଲଗଇନ୍ ହେଲା ପରେ ଖୋଲିବ) ---
    elif st.session_state["page"] == "Admin_Dashboard":
        if st.button("⬅️ Back to Home"):
            st.session_state["page"] = "Home"
            st.rerun()
            
        st.title("👑 Master Admin Dashboard")
        st.success("ସ୍ୱାଗତମ୍, Master Administrator (KULU123)!")
        
        # ଡାଟାବେସ୍‌ରୁ ତଥ୍ୟ ଆଣିବା
        conn = init_connection()
        t_schools, t_students = 0, 0
        if conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM schools")
                res = cur.fetchone()
                if res: t_schools = res[0]
                cur.execute("SELECT COUNT(*) FROM students")
                res2 = cur.fetchone()
                if res2: t_students = res2[0]

        col1, col2 = st.columns(2)
        col1.metric("🏫 Total Registered Schools", t_schools)
        col2.metric("🎓 Total Students Enrolled", t_students)
        
        if st.button("Logout Admin"):
            st.session_state["admin_logged_in"] = False
            st.session_state["page"] = "Home"
            st.rerun()

    # --- ୪. SCHOOL LOGIN PAGE ---
    elif st.session_state["page"] == "School_Login":
        if st.button("⬅️ Back to Home"):
            st.session_state["page"] = "Home"
            st.rerun()
            
        st.markdown("### 🏫 School Portal Login")
        with st.form("school_login"):
            s_id = st.text_input("School ID")
            s_pass = st.text_input("Password", type="password")
            s_sub = st.form_submit_button("Login ➡️")
            if s_sub:
                conn = init_connection()
                if conn:
                    with conn.cursor(cursor_factory=RealDictCursor) as cur:
                        cur.execute("SELECT * FROM schools WHERE school_id = %s AND password = %s", (s_id, s_pass))
                        if cur.fetchone():
                            st.success("ସ୍କୁଲ୍ ଲଗଇନ୍ ସଫଳ ହେଲା!")
                        else:
                            st.error("ଭୁଲ School ID କିମ୍ବା Password!")

    # --- ୫. NEW SCHOOL REGISTRATION ---
    elif st.session_state["page"] == "New_School":
        if st.button("⬅️ Back to Home"):
            st.session_state["page"] = "Home"
            st.rerun()
            
        st.markdown("### 📝 New School Registration")
        with st.form("new_sch_form", clear_on_submit=True):
            s_name = st.text_input("School Name (ସ୍କୁଲ୍ ର ନାମ)")
            s_addr = st.text_input("School Address (ଠିକଣା)")
            s_code = st.text_input("Create School ID (ଯେପରି: SCH001)")
            s_pwd = st.text_input("Create Password", type="password")
            s_btn = st.form_submit_button("Register School ✅")
            
            if s_btn:
                if s_name and s_code and s_pwd:
                    conn = init_connection()
                    if conn:
                        try:
                            with conn.cursor() as cur:
                                cur.execute("INSERT INTO schools (school_name, address, school_id, password) VALUES (%s, %s, %s, %s)", (s_name, s_addr, s_code, s_pwd))
                                conn.commit()
                            st.success(f"'{s_name}' ସଫଳତାର ସହ ରେଜିଷ୍ଟର୍ ହୋଇଗଲା!")
                        except Exception as e:
                            st.error(f"ଏରର୍: {e}")
                else:
                    st.warning("ସମସ୍ତ ଜରୁରୀ କ୍ଷେତ୍ର ପୂରଣ କରନ୍ତୁ!")

    # --- ୬. NEW STUDENT REGISTRATION ---
    elif st.session_state["page"] == "New_Student":
        if st.button("⬅️ Back to Home"):
            st.session_state["page"] = "Home"
            st.rerun()
            
        st.markdown("### 🎓 New Student Registration")
        with st.form("new_std_form", clear_on_submit=True):
            st_name = st.text_input("Student Name (ଛାତ୍ର/ଛାତ୍ରୀଙ୍କ ନାମ)")
            st_class = st.selectbox("Select Class", ["Class 1", "Class 2", "Class 3", "Class 4", "Class 5", "Class 6", "Class 7", "Class 8", "Class 9", "Class 10"])
            st_roll = st.text_input("Roll Number")
            st_dob = st.date_input("Date of Birth")
            st_btn = st.form_submit_button("Register Student ✅")
            
            if st_btn:
                if st_name and st_roll:
                    conn = init_connection()
                    if conn:
                        try:
                            with conn.cursor() as cur:
                                cur.execute("INSERT INTO students (student_name, class_name, roll_number, dob) VALUES (%s, %s, %s, %s)", (st_name, st_class, st_roll, st_dob))
                                conn.commit()
                            st.success(f"'{st_name}' ଙ୍କ ଆଡମିସନ୍ ସଫଳତାର ସହ ସେଭ୍ ହୋଇଗଲା!")
                        except Exception as e:
                            st.error(f"ଏରର୍: {e}")
                else:
                    st.warning("ନାମ ଏବଂ ରୋଲ୍ ନମ୍ବର ଦିଅନ୍ତୁ!")

    # --- ୭. SCHOLARSHIP PORTAL ---
    elif st.session_state["page"] == "Scholarship":
        if st.button("⬅️ Back to Home"):
            st.session_state["page"] = "Home"
            st.rerun()
            
        st.markdown("### 📜 Scholarship Portal")
        st.info("ଏଠାରେ ଛାତ୍ରଛାତ୍ରୀମାନଙ୍କର ବୃତ୍ତି (Scholarship) ଆବେଦନ ଏବଂ ଷ୍ଟାଟସ୍ ଯାଞ୍ଚ କରାଯିବ। (শীଘ୍ର ଆସୁଛି)")

if __name__ == "__main__":
    main()
