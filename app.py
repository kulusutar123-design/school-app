import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor

# ୧. ପୃଷ୍ଠା ସେଟିଂସ୍ (ନାମ ବଦଳାଗଲା)
st.set_page_config(page_title="Advanced School Management System", page_icon="🏫", layout="wide")

# ୨. ସୁରକ୍ଷିତ କ୍ଲାଉଡ୍ ଡାଟାବେସ୍ କନେକ୍ସନ୍ (Supabase)
@st.cache_resource
def init_connection():
    try:
        return psycopg2.connect(st.secrets["DATABASE_URL"], sslmode='require')
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return None

# ୩. ଡାଟାବେସ୍ ଟେବୁଲ୍ ପ୍ରସ୍ତୁତି (ପ୍ରଥମ ଥର ପାଇଁ)
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

# ୫. ମୂଳ ଆପ୍ ଡିଜାଇନ୍ ଏବଂ ଲଗଇନ୍ ପୋର୍ଟାଲ୍
def main():
    # ଡାଟାବେସ୍ ଚାଲୁକରନ୍ତୁ
    create_tables()

    # ସେସନ୍ ଷ୍ଟେଟ୍ ଚେକ୍
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    # ଲଗଇନ୍ ପେଜ୍ ଡିଜାଇନ୍
    if not st.session_state["logged_in"]:
        st.button("🏠 Home")
        st.markdown("### 🔑 Master Administrator Portal")
        
        action = st.radio("Choose Action", ["Login", "Forgot Password"])
        
        if action == "Login":
            username = st.text_input("Master Username", placeholder="Enter KULU123")
            password = st.text_input("Master Password", type="password", placeholder="Enter Admin@2026")
            
            if st.button("Login"):
                if check_login(username, password):
                    st.session_state["logged_in"] = True
                    st.success("ଲଗଇନ୍ ସଫଳ ହେଲା! ଡ୍ୟାସ୍‌ବୋର୍ଡ ଖୋଲୁଛି...")
                    st.rerun()
                else:
                    st.error("ଭୁଲ Master ID କିମ୍ବା Password!")
        
        elif action == "Forgot Password":
            st.warning("ସୁରକ୍ଷା କାରଣରୁ ପାସୱାର୍ଡ ରିସେଟ୍ କରିବା ପାଇଁ ମୁଖ୍ୟ ଡେଭେଲପର୍ (Jyoti Prakash Sutar) ଙ୍କ ସହ ସମ୍ପର୍କ କରନ୍ତୁ।")
            
    # ଡ୍ୟାସ୍‌ବୋର୍ଡ ପେଜ୍ (ଲଗଇନ୍ ସଫଳ ହେବା ପରେ)
    else:
        st.title("🏫 Advanced School Management System")
        st.success("ସ୍ୱାଗତମ୍, Master Administrator (KULU123)!")
        
        # Dashboard Menu Options
        menu = st.sidebar.selectbox("ମେନୁ ବାଛନ୍ତୁ", ["Student Details", "Attendance Entry", "Result Management", "Fees Collection"])
        
        st.write(f"ବର୍ତ୍ତମାନ ଆପଣ **{menu}** ବିଭାଗରେ ଅଛନ୍ତି। ଏଠାରେ ସେଭ୍ ହେଉଥିବା ସମସ୍ତ ଡାଟା ସିଧାସଳଖ ଆପଣଙ୍କ ଲାଇଫ୍‌ଟାଇମ୍ ସୁରକ୍ଷିତ Supabase ଡାଟାବେସ୍‌କୁ ଯାଉଛି।")
        
        # ଲଗଆଉଟ୍ ବଟନ୍
        st.sidebar.markdown("---")
        if st.sidebar.button("Logout"):
            st.session_state["logged_in"] = False
            st.rerun()

if __name__ == "__main__":
    main()
