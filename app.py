import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor

# 1. Page Configuration
st.set_page_config(page_title="School Home Portal", page_icon="🏫", layout="wide")

# 2. Cloud Database Connection
@st.cache_resource
def init_connection():
    try:
        return psycopg2.connect(st.secrets["DATABASE_URL"], sslmode='require')
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return None

# 3. Database Tables
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

def main():
    create_tables()

    if "nav" not in st.session_state:
        st.session_state["nav"] = "Home"
    if "admin_logged" not in st.session_state:
        st.session_state["admin_logged"] = False

    # Big 3D Cards CSS Styling (Buttons styled as big 3D interactive cards)
    st.markdown("""
        <style>
        .stButton>button {
            width: 100%;
            height: 130px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 18px !important;
            padding: 20px !important;
            box-shadow: 0 12px 30px rgba(0,0,0,0.12), 0 6px 10px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
            border: 2px solid #cbd5e1;
            background: linear-gradient(135deg, #ffffff, #f8fafc);
            color: #1e3a8a !important;
            text-align: center;
        }
        .stButton>button:hover {
            transform: translateY(-5px);
            box-shadow: 0 18px 35px rgba(0,0,0,0.2), 0 8px 12px rgba(0,0,0,0.12);
            border-color: #2563eb;
            background: linear-gradient(135deg, #f0fdf4, #ffffff);
        }
        </style>
    """, unsafe_allow_html=True)

    # Header Bar
    st.markdown("""
        <div style='background: linear-gradient(90deg, #0d3b66, #1d4ed8); padding: 25px; border-radius: 16px; color: white; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 8px 20px rgba(0,0,0,0.2);'>
            <h2 style='margin:0;'>🏫 SCHOOL HOME PORTAL</h2>
            <p style='margin: 0; font-style: italic; font-size: 18px;'>Better Education, Brighter Future</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("")

    # HOME PAGE
    if st.session_state["nav"] == "Home":
        col_left, col_right = st.columns([1.6, 1])

        with col_left:
            st.markdown("""
                <div style='background: linear-gradient(135deg, #ffffff, #f8fafc); padding: 30px; border-radius: 20px; box-shadow: 0 12px 30px rgba(0,0,0,0.08); border-left: 8px solid #2563eb; margin-bottom: 25px;'>
                    <h3 style='color: #1e3a8a; margin-top:0;'>🌟 Welcome to Digital School Management</h3>
                    <p style='font-size: 16px; color: #475569;'>Manage your schools, student admissions, attendance, and records securely on the cloud platform with high performance.</p>
                    <p style='font-size: 15px;'><b>✨ Features:</b> Secure Cloud Database, Instant Registration, 3D Interactive Portal.</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 📌 Quick Portal Actions (Clickable 3D Cards)")
            
            # 3no 3D Card buttons seedha upar hain, niche wale extra buttons hata diye gaye hain
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("🏫\n\nNew School Registration"):
                    st.session_state["nav"] = "New School Registration"
                    st.rerun()
            with c2:
                if st.button("🎓\n\nNew Student Registration"):
                    st.session_state["nav"] = "New Student Registration"
                    st.rerun()
            with c3:
                if st.button("💰\n\nScholarship Portal"):
                    st.session_state["nav"] = "Scholarship Portal"
                    st.rerun()

        with col_right:
            st.markdown("""
                <div style='background: linear-gradient(135deg, #ffffff, #f8fafc); padding: 30px; border-radius: 20px; box-shadow: 0 12px 30px rgba(0,0,0,0.08); text-align: center; margin-bottom: 25px;'>
                    <h3 style='color: #1e3a8a; margin-top:0;'>🔐 Login Portal</h3>
                    <hr style='margin: 10px 0 20px 0;'>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("👤 Admin Login"):
                st.session_state["nav"] = "Admin Login"
                st.rerun()
                
            st.write("")
            if st.button("🏫 School Login"):
                st.session_state["nav"] = "School Login"
                st.rerun()
                
            st.markdown("<p style='text-align: center; font-size: 14px; color: gray; margin-top: 30px;'>\"Education is the key to a better tomorrow\"</p>", unsafe_allow_html=True)

    # ADMIN LOGIN PAGE
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
                                st.success("Login safala hela! Dashboard kholuchi...")
                                st.rerun()
                            else:
                                st.error("Bhula Master ID kimbha Password!")
        else:
            st.success("You are already logged in as Master Admin (KULU123)!")
            if st.button("Logout Admin"):
                st.session_state["admin_logged"] = False
                st.rerun()

    # SCHOOL LOGIN PAGE
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
                            st.success("School Login safala hela!")
                        else:
                            st.error("Bhula School ID kimbha Password!")

    # NEW SCHOOL REGISTRATION
    elif st.session_state["nav"] == "New School Registration":
        if st.button("⬅️ Back to Home"):
            st.session_state["nav"] = "Home"
            st.rerun()
            
        st.subheader("📝 New School Registration Portal")
        with st.form("school_reg_page", clear_on_submit=True):
            sch_name = st.text_input("School Name")
            sch_addr = st.text_input("School Address")
            sch_id = st.text_input("Create School ID (jeperia: SCH001)")
            sch_pass = st.text_input("Create Password", type="password")
            
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
                            st.success(f"'{sch_name}' safalatara sahita register hoi gala!")
                        except Exception as e:
                            st.error(f"Error: {e}")
                else:
                    st.warning("Samasta field purana karantu!")

    # NEW STUDENT REGISTRATION
    elif st.session_state["nav"] == "New Student Registration":
        if st.button("⬅️ Back to Home"):
            st.session_state["nav"] = "Home"
            st.rerun()
            
        st.subheader("🎓 New Student Registration Portal")
        with st.form("student_reg_page", clear_on_submit=True):
            std_name = st.text_input("Student Name")
            std_class = st.selectbox("Select Class", ["Class 1", "Class 2", "Class 3", "Class 4", "Class 5", "Class 6", "Class 7", "Class 8", "Class 9", "Class 10"])
            roll_no = st.text_input("Roll Number")
            dob = st.date_input("Date of Birth")
            
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
                            st.success(f"'{std_name}' admision safala bhabare save hoi gala!")
                        except Exception as e:
                            st.error(f"Error: {e}")
                else:
                    st.warning("Nama ebong roll number diantu!")

    # SCHOLARSHIP PORTAL
    elif st.session_state["nav"] == "Scholarship Portal":
        if st.button("⬅️ Back to Home"):
            st.session_state["nav"] = "Home"
            st.rerun()
            
        st.subheader("💰 Scholarship Portal & Details")
        st.info("Eatharu chatrachatrimane scholarship pain abedan kariparibe.")
        st.text_input("Student Roll Number")
        st.text_input("Aadhaar / ID Number")
        st.button("Check Scholarship Eligibility 🔍")

    st.markdown("---")
    st.markdown("<p style='text-align: center; color: gray;'>School Management System | Education • Discipline • Success</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
