import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor

# 1. Page Configuration (Wide Layout & Custom Theme)
st.set_page_config(page_title="School Home Portal", page_icon="🏫", layout="wide")

# Custom CSS for 3D card effects and professional look matching the photo layout
st.markdown("""
    <style>
    .main {
        background-color: #f4f7f6;
    }
    .stButton>button {
        border-radius: 12px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .card-box {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.08);
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Cloud Database Connection
@st.cache_resource
def init_connection():
    try:
        return psycopg2.connect(st.secrets["DATABASE_URL"], sslmode='require')
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return None

# 3. Database Tables Setup
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

def check_admin_login(username, password):
    conn = init_connection()
    if conn is not None:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM admin_users WHERE username = %s AND password = %s", (username, password))
            return cur.fetchone() is not None
    return False

# 4. Main Portal Logic
def main():
    create_tables()

    if "page" not in st.session_state:
        st.session_state["page"] = "Home"
    if "admin_logged_in" not in st.session_state:
        st.session_state["admin_logged_in"] = False

    # --- HOME PAGE (PHOTO LAYOUT MATCHING) ---
    if st.session_state["page"] == "Home":
        # Top Header Banner
        col_h1, col_h2 = st.columns([3, 1])
        with col_h1:
            st.markdown("# 🏫 SCHOOL HOME PORTAL")
            st.caption("✨ Better Education • Brighter Future ✨")
        with col_h2:
            st.markdown("<br>🏠 **Home** &nbsp;|&nbsp; ❓ **Help** &nbsp;|&nbsp; 📞 **Contact**", unsafe_allow_html=True)
        
        st.markdown("---")

        # Main Banner & Login Area (Similar to Image layout)
        left_col, right_col = st.columns([2, 1])

        with left_col:
            st.markdown("""
                <div style='background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 35px; border-radius: 20px; color: white; box-shadow: 0 8px 25px rgba(0,0,0,0.15);'>
                    <h2>🌟 Welcome to Smart School Portal</h2>
                    <p style='font-size: 16px;'>Experience the next-gen 3D inspired cloud management system for advanced school administration, student registries, and secure database management.</p>
                    <hr style='border-color: rgba(255,255,255,0.2);'>
                    <p style='margin-bottom: 0; font-size: 14px;'>🔒 Cloud Connected • ⚡ Lightning Fast • 🛡️ 100% Secure</p>
                </div>
            """, unsafe_allow_html=True)

        with right_col:
            st.markdown("""
                <div style='background: white; padding: 25px; border-radius: 20px; box-shadow: 0 8px 25px rgba(0,0,0,0.08); border-top: 5px solid #00c853;'>
                    <h3>👤 Login Portal</h3>
                    <p style='color: gray; font-size: 14px;'>Select your access panel below:</p>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("🟢 Admin Login", use_container_width=True):
                st.session_state["page"] = "Admin_Login"
                st.rerun()
            
            if st.button("🔵 School Login", use_container_width=True):
                st.session_state["page"] = "School_Login"
                st.rerun()

        st.markdown("<br><h3 style='text-align: center;'>📌 Quick Services & Portals</h3><br>", unsafe_allow_html=True)
        
        # Bottom 3 Cards (New School, New Student, Scholarship) matching image bottom layout
        q1, q2, q3 = st.columns(3)
        with q1:
            st.markdown("<div class='card-box'><h4>🏫</h4><h4>New School Registration</h4><p>Add new schools to cloud database.</p></div>", unsafe_allow_html=True)
            if st.button("Register School ➡️", use_container_width=True):
                st.session_state["page"] = "New_School"
                st.rerun()
        with q2:
            st.markdown("<div class='card-box'><h4>🎓</h4><h4>New Student Registration</h4><p>Manage student admissions easily.</p></div>", unsafe_allow_html=True)
            if st.button("Register Student ➡️", use_container_width=True):
                st.session_state["page"] = "New_Student"
                st.rerun()
        with q3:
            st.markdown("<div class='card-box'><h4>📜</h4><h4>Scholarship Portal</h4><p>Check scholarship details & status.</p></div>", unsafe_allow_html=True)
            if st.button("Explore Portal ➡️", use_container_width=True):
                st.session_state["page"] = "Scholarship"
                st.rerun()

    # --- ADMIN LOGIN ---
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
                        st.success("Login Successful!")
                        st.rerun()
                    else:
                        st.error("Wrong Username or Password!")
        else:
            st.success("You are already logged in as Admin!")
            if st.button("Go to Admin Dashboard ➡️"):
                st.session_state["page"] = "Admin_Dashboard"
                st.rerun()
            if st.button("Logout"):
                st.session_state["admin_logged_in"] = False
                st.rerun()

    # --- ADMIN DASHBOARD ---
    elif st.session_state["page"] == "Admin_Dashboard":
        if st.button("⬅️ Back to Home"):
            st.session_state["page"] = "Home"
            st.rerun()
            
        st.title("👑 Master Admin Dashboard")
        st.success("Welcome, Master Administrator (KULU123)!")
        
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

    # --- SCHOOL LOGIN ---
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
                            st.success("School Login Successful!")
                        else:
                            st.error("Invalid School ID or Password!")

    # --- NEW SCHOOL REGISTRATION ---
    elif st.session_state["page"] == "New_School":
        if st.button("⬅️ Back to Home"):
            st.session_state["page"] = "Home"
            st.rerun()
            
        st.markdown("### 📝 New School Registration")
        with st.form("new_sch_form", clear_on_submit=True):
            s_name = st.text_input("School Name")
            s_addr = st.text_input("School Address")
            s_code = st.text_input("Create School ID (e.g. SCH001)")
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
                            st.success(f"'{s_name}' registered successfully and saved to cloud!")
                        except Exception as e:
                            st.error(f"Error: {e}")
                else:
                    st.warning("Please fill all required fields!")

    # --- NEW STUDENT REGISTRATION ---
    elif st.session_state["page"] == "New_Student":
        if st.button("⬅️ Back to Home"):
            st.session_state["page"] = "Home"
            st.rerun()
            
        st.markdown("### 🎓 New Student Registration")
        with st.form("new_std_form", clear_on_submit=True):
            st_name = st.text_input("Student Name")
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
                            st.success(f"'{st_name}' admission saved successfully to cloud!")
                        except Exception as e:
                            st.error(f"Error: {e}")
                else:
                    st.warning("Please enter student name and roll number!")

    # --- SCHOLARSHIP PORTAL ---
    elif st.session_state["page"] == "Scholarship":
        if st.button("⬅️ Back to Home"):
            st.session_state["page"] = "Home"
            st.rerun()
            
        st.markdown("### 📜 Scholarship Portal")
        st.info("Scholarship application and verification module coming soon.")

if __name__ == "__main__":
    main()
