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

    # Exact Photo Style CSS Styling (Green Admin Button, Blue School Button & 3D Cards)
    st.markdown("""
        <style>
        /* Admin Login Button - Green Style */
        .admin-btn button {
            width: 100%;
            height: 65px;
            border-radius: 14px !important;
            font-weight: bold;
            font-size: 18px !important;
            background: linear-gradient(135deg, #22c55e, #16a34a) !important;
            color: white !important;
            box-shadow: 0 8px 20px rgba(34, 197, 94, 0.3) !important;
            border: none !important;
            transition: all 0.3s ease;
        }
        .admin-btn button:hover {
            transform: translateY(-2px);
            background: linear-gradient(135deg, #16a34a, #15803d) !important;
            box-shadow: 0 12px 25px rgba(34, 197, 94, 0.4) !important;
        }

        /* School Login Button - Blue Style */
        .school-btn button {
            width: 100%;
            height: 65px;
            border-radius: 14px !important;
            font-weight: bold;
            font-size: 18px !important;
            background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
            color: white !important;
            box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3) !important;
            border: none !important;
            transition: all 0.3s ease;
        }
        .school-btn button:hover {
            transform: translateY(-2px);
            background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
            box-shadow: 0 12px 25px rgba(59, 130, 246, 0.4) !important;
        }

        /* Quick Action 3D Cards */
        .action-card button {
            width: 100%;
            height: 140px;
            border-radius: 20px !important;
            font-weight: bold;
            font-size: 17px !important;
            background: linear-gradient(135deg, #ffffff, #f8fafc) !important;
            color: #1e3a8a !important;
            box-shadow: 0 10px 25px rgba(0,0,0,0.08) !important;
            border: 2px solid #cbd5e1 !important;
            transition: all 0.3s ease;
        }
        .action-card button:hover {
            transform: translateY(-4px);
            border-color: #2563eb !important;
            box-shadow: 0 15px 30px rgba(0,0,0,0.15) !important;
            background: linear-gradient(135deg, #f0fdf4, #ffffff) !important;
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
            
            st.markdown("### 📌 Quick Portal Actions")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown('<div class="action-card">', unsafe_allow_html=True)
                if st.button("🏫\n\nNew School Registration"):
                    st.session_state["nav"] = "New School Registration"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="action-card">', unsafe_allow_html=True)
                if st.button("🎓\n\nNew Student Registration"):
                    st.session_state["nav"] = "New Student Registration"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with c3:
                st.markdown('<div class="action-card">', unsafe_allow_html=True)
                if st.button("💰\n\nScholarship Portal"):
                    st.session_state["nav"] = "Scholarship Portal"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        with col_right:
            st.markdown("""
                <div style='background: linear-gradient(135deg, #ffffff, #f8fafc); padding: 25px; border-radius: 20px; box-shadow: 0 12px 30px rgba(0,0,0,0.08); text-align: center; margin-bottom: 20px;'>
                    <h3 style='color: #1e3a8a; margin-top:0;'>🔐 Login</h3>
                    <hr style='margin: 8px 0 15px 0;'>
                </div>
            """, unsafe_allow_html=True)
            
            # Admin Login Button (Green)
            st.markdown('<div class="admin-btn">', unsafe_allow_html=True)
            if st.button("👤  Admin Login ➔"):
                st.session_state["nav"] = "Admin Login"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.write("")
            
            # School Login Button (Blue)
            st.markdown('<div class="school-btn">', unsafe_allow_html=True)
            if st.button("🏫  School Login ➔"):
                st.session_state["nav"] = "School Login"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
                
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
