import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor

# ୧. ପୃଷ୍ଠା ସେଟିଂସ୍ (Wide layout for professional dashboard)
st.set_page_config(page_title="Advanced School Management System", page_icon="🏫", layout="wide")

# ୨. କ୍ଲାଉଡ୍ ଡାଟାବେସ୍ କନେକ୍ସନ୍ (Supabase Transaction Pooler)
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
def check_login(username, password):
    conn = init_connection()
    if conn is not None:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM admin_users WHERE username = %s AND password = %s", (username, password))
            user = cur.fetchone()
            return user is not None
    return False

# ୫. ମୂଳ ଆପ୍ ଡିଜାଇନ୍ ଏବଂ ଡ୍ୟାସ୍‌ବୋର୍ଡ
def main():
    create_tables()

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    # --- ଲଗଇନ୍ ପେଜ୍ ---
    if not st.session_state["logged_in"]:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<br><h2 style='text-align: center;'>🏫 Advanced School Management</h2>", unsafe_allow_html=True)
            st.markdown("<h4 style='text-align: center; color: gray;'>Master Administrator Portal</h4><br>", unsafe_allow_html=True)
            
            action = st.radio("Choose Action", ["Login", "Forgot Password"], horizontal=True)
            
            if action == "Login":
                username = st.text_input("Master Username", placeholder="Enter KULU123")
                password = st.text_input("Master Password", type="password", placeholder="Enter Admin@2026")
                
                if st.button("Login to Dashboard 🚀", use_container_width=True):
                    if check_login(username, password):
                        st.session_state["logged_in"] = True
                        st.rerun()
                    else:
                        st.error("ଭୁଲ Master ID କିମ୍ବା Password!")
            
            elif action == "Forgot Password":
                st.warning("ପାସୱାର୍ଡ ରିସେଟ୍ କରିବା ପାଇଁ ମୁଖ୍ୟ ଡେଭେଲପର୍ (Jyoti Prakash Sutar) ଙ୍କ ସହ ସମ୍ପର୍କ କରନ୍ତୁ।")
            
    # --- ମାଷ୍ଟର ଡ୍ୟାସ୍‌ବୋର୍ଡ (Master Dashboard) ---
    else:
        # ଉପର ହେଡର୍
        st.title("🏫 Advanced School Management System")
        st.markdown("---")
        
        # ବାମ ପଟେ ମେନୁ (Sidebar)
        st.sidebar.markdown("### 📌 Navigation Panel")
        menu = st.sidebar.radio(
            "ମେନୁ ବାଛନ୍ତୁ", 
            ["Master ID Dashboard", "School Login", "New School Registration", "New Student Registration"]
        )
        
        st.sidebar.markdown("---")
        st.sidebar.success("Logged in as: **KULU123**")
        if st.sidebar.button("Logout 🔴", use_container_width=True):
            st.session_state["logged_in"] = False
            st.rerun()
        
        # ୧. Master ID Dashboard
        if menu == "Master ID Dashboard":
            st.subheader("👑 Master ID Dashboard & Overview")
            st.write("ଏଠାରେ ଆପଣ ସମସ୍ତ ସ୍କୁଲ୍ ଏବଂ ଛାତ୍ରଛାତ୍ରୀଙ୍କର ମୋଟ ହିସାବ ଦେଖିପାରିବେ।")
            
            # କ୍ଲାଉଡ୍‌ରୁ ପ୍ରକୃତ ତଥ୍ୟ ଆଣିବା
            conn = init_connection()
            total_schools = 0
            total_students = 0
            if conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) FROM schools")
                    res_s = cur.fetchone()
                    if res_s: total_schools = res_s[0]
                    
                    cur.execute("SELECT COUNT(*) FROM students")
                    res_st = cur.fetchone()
                    if res_st: total_students = res_st[0]

            # ସୁନ୍ଦର ମେଟ୍ରିକ୍ କାର୍ଡସ୍
            col1, col2, col3 = st.columns(3)
            col1.metric(label="🏫 Total Registered Schools", value=total_schools)
            col2.metric(label="🎓 Total Students Enrolled", value=total_students)
            col3.metric(label="👑 Master Admin Status", value="Active")
            
            st.markdown("---")
            st.info("💡 ବାମ ପଟେ ଥିବା ମେନୁରୁ ଯେକୌଣସି ଅପ୍ସନ୍ ବାଛି ଆପଣ ନୂଆ ସ୍କୁଲ୍ କିମ୍ବା ଛାତ୍ରଛାତ୍ରୀଙ୍କୁ ରେଜିଷ୍ଟର୍ କରିପାରିବେ।")

        # ୨. School Login
        elif menu == "School Login":
            st.subheader("🏫 School Login Portal")
            st.write("ନିଜର ସ୍ୱତନ୍ତ୍ର ସ୍କୁଲ୍ ID ଏବଂ Password ଦେଇ ଲଗଇନ୍ କରନ୍ତୁ।")
            
            col1, col2 = st.columns(2)
            with col1:
                with st.form("school_login_form"):
                    s_id = st.text_input("School ID")
                    s_pass = st.text_input("Password", type="password")
                    submitted = st.form_submit_button("School Login ➡️")
                    if submitted:
                        # ଯାଞ୍ଚ ଲଜିକ୍
                        conn = init_connection()
                        if conn:
                            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                                cur.execute("SELECT * FROM schools WHERE school_id = %s AND password = %s", (s_id, s_pass))
                                if cur.fetchone():
                                    st.success("ସ୍କୁଲ୍ ଲଗଇନ୍ ସଫଳ ହେଲା!")
                                else:
                                    st.error("ଭୁଲ School ID କିମ୍ବା Password!")
            
        # ୩. New School Registration
        elif menu == "New School Registration":
            st.subheader("📝 New School Registration")
            st.write("ଏଠାରେ ଏକ ନୂଆ ସ୍କୁଲ୍ ସିଷ୍ଟମ୍‌ରେ ଯୋଡ଼ି ହେବ ଏବଂ ତାହା ସିଧାସଳଖ କ୍ଲାଉଡ୍ ଡାଟାବେସ୍‌ରେ ସେଭ୍ ହେବ।")
            
            with st.form("school_reg_form", clear_on_submit=True):
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
                                st.success(f"'{sch_name}' ସଫଳତାର ସହ ରେଜିଷ୍ଟର୍ ହୋଇଗଲା! ଡାଟା କ୍ଲାଉଡ୍‌ରେ ସେଭ୍ ହୋଇଗଲା.")
                            except Exception as e:
                                st.error(f"ଏରର୍: ଏହି School ID ଆଗରୁ ଅଛି କିମ୍ବା କିଛି ସମସ୍ୟା ଘଟିଲା ({e})")
                    else:
                        st.warning("ଦୟାକରି ସମସ୍ତ ଜରୁରୀ କ୍ଷେତ୍ର (Fields) ପୂରଣ କରନ୍ତୁ!")
                
        # ୪. New Student Registration
        elif menu == "New Student Registration":
            st.subheader("🎓 New Student Registration")
            st.write("ନୂଆ ଛାତ୍ରଛାତ୍ରୀଙ୍କ ଆଡମିସନ୍ ଏଣ୍ଟ୍ରି ଏବଂ କ୍ଲାଉଡ୍ ସେଭ୍ ଡାଟାବେସ୍।")
            
            with st.form("student_reg_form", clear_on_submit=True):
                std_name = st.text_input("Student Name (ଛାତ୍ର/ଛାତ୍ରୀଙ୍କ ନାମ)")
                std_class = st.selectbox("Select Class (ଶ୍ରେଣୀ ବାଛନ୍ତୁ)", ["Class 1", "Class 2", "Class 3", "Class 4", "Class 5", "Class 6", "Class 7", "Class 8", "Class 9", "Class 10"])
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
                                st.success(f"'{std_name}' ଙ୍କ ଆଡମିସନ୍ ସଫଳ ଭାବରେ ସେଭ୍ ହୋଇଗଲା!")
                            except Exception as e:
                                st.error(f"ଏରର୍: {e}")
                    else:
                        st.warning("ଦୟାକରି ଛାତ୍ରଛାତ୍ରୀଙ୍କ ନାମ ଏବଂ ରୋଲ୍ ନମ୍ବର ଦିଅନ୍ତୁ!")

if __name__ == "__main__":
    main()
