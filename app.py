import os
import base64
# ଏହା ଦରକାରୀ ପ୍ୟାକେଜ୍‌କୁ ଆପେ ଆପେ ଇନଷ୍ଟଲ୍ କରିବ (503 ଏରର୍ ଆସିବନି)
os.system("pip install python-multipart")

from fastapi import FastAPI, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

# ଡାଟାବେସ୍ (ଉଦାହରଣ ପାଇଁ ଡାଟା)
admin_data = {
    "username": "admin",
    "password": "123",
    "email": "admin@school.com",
    "mobile": "9876543210",
    "upi_id": "school@upi",
    "reg_fee": "1000",
    "gst_percent": "18",
    "gst_no": "21AAAAA1234A1Z1"
}

home_settings = {
    "notice": "Welcome to our School Portal! New Registration is Open for 2026.",
    "bg_image": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?q=80&w=1920&auto=format&fit=crop"
}

schools = [
    {"code": "1001", "name": "Cuttack High School", "hm_name": "Ramesh Das", "hm_mobile": "9876543211", "address": "Link Road, Cuttack", "state": "Odisha", "pay_status": "Pending", "status": "Inactive"},
    {"code": "1002", "name": "Delhi Public School", "hm_name": "Amit Sharma", "hm_mobile": "9876543212", "address": "RK Puram", "state": "Delhi", "pay_status": "Approved", "status": "Active"},
    {"code": "1003", "name": "Mumbai City School", "hm_name": "Vikram Singh", "hm_mobile": "9876543213", "address": "Andheri West", "state": "Maharashtra", "pay_status": "Rejected", "status": "Inactive"}
]

states_list = ["Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Delhi", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"]

# ୧. ହୋମ୍ ପେଜ୍ (ରନିଂ ନୋଟିସ୍ ଏବଂ ଅପଲୋଡେଡ୍ ଫଟୋ ସହିତ)
@app.get("/", response_class=HTMLResponse)
async def home():
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>School Portal</title>
        <style>
            body {{ margin: 0; font-family: 'Segoe UI', Tahoma, sans-serif; background: url('{home_settings["bg_image"]}') no-repeat center center fixed; background-size: cover; min-height: 100vh; display: flex; flex-direction: column; color: #fff; }}
            .overlay {{ background: rgba(0, 20, 50, 0.65); min-height: 100vh; display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box; }}
            .navbar {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255, 255, 255, 0.2); padding: 15px 40px; }}
            .marquee-box {{ background: #d32f2f; color: white; padding: 10px; font-size: 1.2rem; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; }}
            .main-content {{ text-align: center; margin: auto 0; padding: 0 40px; }}
            .portal-title {{ font-size: 3rem; font-weight: bold; margin-bottom: 5px; text-shadow: 0 2px 10px rgba(0,0,0,0.5); }}
            .grid-container {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 30px; max-width: 1200px; margin: 40px auto 0; }}
            .card-wrapper {{ display: flex; flex-direction: column; align-items: center; width: 170px; text-decoration: none; }}
            .circle-btn {{ width: 110px; height: 110px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 2.5rem; box-shadow: 0 8px 25px rgba(0,0,0,0.4); transition: 0.3s; border: 4px solid rgba(255,255,255,0.8); margin-bottom: 12px; background: linear-gradient(135deg, #00c6ff, #0072ff); }}
            .card-wrapper:hover .circle-btn {{ transform: translateY(-8px); }}
            .card-label {{ background: white; color: #0d47a1; font-weight: bold; font-size: 0.9rem; padding: 8px 12px; border-radius: 20px; width: 100%; box-sizing: border-box; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="overlay">
            <div class="marquee-box">
                <marquee>{home_settings["notice"]}</marquee>
            </div>
            <div class="navbar">
                <div class="logo-text"><h1 style="margin:0;">🏫 School Portal</h1><p style="margin:0;">Learn | Grow | Succeed</p></div>
            </div>
            <div class="main-content">
                <div class="portal-title">Welcome to Our School</div>
                <div class="grid-container">
                    <a href="/admin-login" class="card-wrapper"><div class="circle-btn">⚙️</div><div class="card-label">ADMIN LOGIN</div></a>
                    <a href="#" class="card-wrapper"><div class="circle-btn" style="background: linear-gradient(135deg, #11998e, #38ef7d);">🏫</div><div class="card-label">SCHOOL LOGIN</div></a>
                    <a href="#" class="card-wrapper"><div class="circle-btn" style="background: linear-gradient(135deg, #f7971e, #ffd200);">📝</div><div class="card-label">SCHOOL REGISTRATION</div></a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

# ୨. ଲଗଇନ୍ ଏବଂ ସାଇଡବାର୍
@app.get("/admin-login", response_class=HTMLResponse)
async def login_page(error: str = None):
    err_msg = f"<p style='color:red; text-align:center;'>{error}</p>" if error else ""
    return f"""
    <html><body style="font-family: Arial; background: #f0f2f5; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0;">
        <div style="background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); width: 300px;">
            <h2 style="text-align: center; color: #0d6efd;">Admin Login</h2>
            {err_msg}
            <form action="/login" method="post">
                <input type="text" name="username" placeholder="Username" style="width:100%; padding:10px; margin:10px 0; border:1px solid #ccc; border-radius:5px;" required>
                <input type="password" name="password" placeholder="Password" style="width:100%; padding:10px; margin:10px 0; border:1px solid #ccc; border-radius:5px;" required>
                <button type="submit" style="width:100%; padding:10px; background:#0d6efd; color:white; border:none; border-radius:5px; cursor:pointer;">Login</button>
            </form>
            <a href="/" style="display:block; text-align:center; margin-top:15px; text-decoration:none; color: green; font-weight:bold;">🏠 Back to Home Portal</a>
        </div>
    </body></html>
    """

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    if username == admin_data["username"] and password == admin_data["password"]:
        return RedirectResponse(url="/dashboard", status_code=303)
    return RedirectResponse(url="/admin-login?error=Invalid Login", status_code=303)

def render_sidebar(active):
    return f"""
    <div style="width: 260px; background: #2c3e50; height: 100vh; position: fixed; border-right: 1px solid #ccc; padding-top: 20px;">
        <div style="text-align: center; margin-bottom: 20px;">
            <h3 style="color: #f1c40f; font-weight: bold; text-transform: uppercase;">KULU SUTAR</h3>
            <p style="color: white; font-size:12px;">Admin Panel</p>
        </div>
        <a href="/dashboard" style="display: block; padding: 12px 20px; text-decoration: none; color: white; background: {'#34495e' if active=='dash' else 'transparent'}; border-left: {'4px solid #f1c40f' if active=='dash' else '4px solid transparent'};">📊 Dashboard</a>
        <a href="/home-ground-setup" style="display: block; padding: 12px 20px; text-decoration: none; color: white; background: {'#34495e' if active=='home' else 'transparent'}; border-left: {'4px solid #f1c40f' if active=='home' else '4px solid transparent'};">🖼️ Home Ground Setup</a>
        <a href="/school-management" style="display: block; padding: 12px 20px; text-decoration: none; color: white; background: {'#34495e' if active=='school' else 'transparent'}; border-left: {'4px solid #f1c40f' if active=='school' else '4px solid transparent'};">🏫 School Management</a>
        <a href="/payment" style="display: block; padding: 12px 20px; text-decoration: none; color: white; background: {'#34495e' if active=='pay' else 'transparent'}; border-left: {'4px solid #f1c40f' if active=='pay' else '4px solid transparent'};">💳 Payment Settings</a>
        <a href="/profile" style="display: block; padding: 12px 20px; text-decoration: none; color: white; background: {'#34495e' if active=='prof' else 'transparent'}; border-left: {'4px solid #f1c40f' if active=='prof' else '4px solid transparent'};">👤 Manage Profile</a>
        <br>
        <a href="/" style="display: block; padding: 10px 20px; text-decoration: none; color: white; background: #e74c3c; text-align: center; margin: 0 20px; border-radius: 5px;">🚪 Logout</a>
    </div>
    """

# ୩. ଡ୍ୟାସବୋର୍ଡ
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    return f"""
    <html><head><style>body{{margin:0; font-family:Arial; background:#f4f6f9;}} .content{{margin-left: 260px; padding: 30px;}}</style></head>
    <body>
        {render_sidebar('dash')}
        <div class="content">
            <h2>Welcome Admin!</h2>
            <p>Select an option from the sidebar to manage your portal.</p>
        </div>
    </body></html>
    """

# ୪. School Management (ଷ୍ଟେଟ୍ ଫିଲ୍ଟର୍ ଏବଂ ଆପ୍ରୁଭ୍/ରିଜେକ୍ଟ ସହିତ)
@app.get("/school-management", response_class=HTMLResponse)
async def school_management():
    state_opts = "<option value='all'>All India (Show All)</option>" + "".join([f"<option value='{s}'>{s}</option>" for s in states_list])
    
    rows = ""
    for s in schools:
        btn_html = ""
        if s["pay_status"] != "Approved":
            btn_html += f"<a href='/verify-payment/{s['code']}/Approve' style='background:green; color:white; padding:5px 10px; text-decoration:none; border-radius:3px; font-size:12px;'>Approve</a> "
        if s["pay_status"] != "Rejected":
            btn_html += f"<a href='/verify-payment/{s['code']}/Reject' style='background:red; color:white; padding:5px 10px; text-decoration:none; border-radius:3px; font-size:12px;'>Reject</a>"
            
        status_color = "green" if s["status"] == "Active" else "red"
        
        rows += f"""
        <tr class="school-row" data-state="{s['state']}" style="background:white; border-bottom:1px solid #ddd;">
            <td style="padding:10px;">{s['name']}</td>
            <td style="padding:10px;">{s['code']}</td>
            <td style="padding:10px;">{s['hm_name']} <br><small>📞 {s['hm_mobile']}</small></td>
            <td style="padding:10px;">{s['address']}, {s['state']}</td>
            <td style="padding:10px; font-weight:bold;">{s['pay_status']}</td>
            <td style="padding:10px; color:{status_color}; font-weight:bold;">{s['status']}</td>
            <td style="padding:10px;">{btn_html}</td>
        </tr>
        """

    return f"""
    <html><head><style>body{{margin:0; font-family:Arial; background:#f4f6f9;}} .content{{margin-left: 260px; padding: 20px;}}</style>
    <script>
        function filterState() {{
            let selected = document.getElementById("stateSelect").value.toLowerCase();
            let rows = document.querySelectorAll(".school-row");
            rows.forEach(row => {{
                if(selected === "all" || row.getAttribute("data-state").toLowerCase() === selected) {{
                    row.style.display = "";
                }} else {{
                    row.style.display = "none";
                }}
            }});
        }}
    </script>
    </head>
    <body>
        {render_sidebar('school')}
        <div class="content">
            <h2>School Management</h2>
            <div style="margin-bottom: 20px;">
                <label style="font-weight:bold;">Select State: </label>
                <select id="stateSelect" onchange="filterState()" style="padding:8px; width:250px; font-size:16px;">
                    {state_opts}
                </select>
            </div>
            
            <table style="width: 100%; border-collapse: collapse; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                <tr style="background: #0d47a1; color: white; text-align:left;">
                    <th style="padding:10px;">School Name</th>
                    <th style="padding:10px;">Code</th>
                    <th style="padding:10px;">Headmaster Info</th>
                    <th style="padding:10px;">Address & State</th>
                    <th style="padding:10px;">Payment Status</th>
                    <th style="padding:10px;">Portal Status</th>
                    <th style="padding:10px;">Action (Verify)</th>
                </tr>
                {rows}
            </table>
        </div>
    </body></html>
    """

@app.get("/verify-payment/{code}/{action}")
async def verify_payment(code: str, action: str):
    for s in schools:
        if s["code"] == code:
            if action == "Approve":
                s["pay_status"] = "Approved"
                s["status"] = "Active" # ପେମେଣ୍ଟ ଦେଲା ପରେ Active
            else:
                s["pay_status"] = "Rejected"
                s["status"] = "Inactive" # ପେମେଣ୍ଟ ରିଜେକ୍ଟ ହେଲେ Inactive
    return RedirectResponse(url="/school-management", status_code=303)

# ୫. Home Ground Setup (Photo Upload & Notice)
@app.get("/home-ground-setup", response_class=HTMLResponse)
async def home_ground_setup():
    return f"""
    <html><head><style>body{{margin:0; font-family:Arial; background:#f4f6f9;}} .content{{margin-left: 260px; padding: 30px;}} .box{{background:white; padding:20px; border-radius:8px; width:500px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);}}</style></head>
    <body>
        {render_sidebar('home')}
        <div class="content">
            <h2>Home Ground Portal Setup</h2>
            <div class="box">
                <form action="/update-home-ground" method="post" enctype="multipart/form-data">
                    <label style="font-weight:bold; display:block; margin-bottom:5px;">Running Notice Display (Marquee):</label>
                    <input type="text" name="notice" value="{home_settings['notice']}" style="width:100%; padding:10px; margin-bottom:20px; box-sizing:border-box;" required>
                    
                    <label style="font-weight:bold; display:block; margin-bottom:5px;">Upload Home Ground Photo:</label>
                    <input type="file" name="bg_file" accept="image/*" style="margin-bottom:20px;">
                    <p style="font-size:12px; color:gray;">(Leave file empty to keep the current background)</p>
                    
                    <button type="submit" style="background:#27ae60; color:white; padding:10px 20px; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">Update Home Page</button>
                </form>
            </div>
        </div>
    </body></html>
    """

@app.post("/update-home-ground")
async def update_home_ground(notice: str = Form(...), bg_file: UploadFile = File(None)):
    home_settings["notice"] = notice
    if bg_file.filename:
        # Base64 ରେ ସେଭ୍ କରିବା ଦ୍ୱାରା ଫାଇଲ୍ ହଜିବ ନାହିଁ 
        contents = await bg_file.read()
        encoded = base64.b64encode(contents).decode("utf-8")
        home_settings["bg_image"] = f"data:{bg_file.content_type};base64,{encoded}"
    return RedirectResponse(url="/home-ground-setup", status_code=303)

# ୬. Payment Settings (Fees, GST, UPI)
@app.get("/payment", response_class=HTMLResponse)
async def payment():
    qr = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=upi://pay?pa={admin_data['upi_id']}"
    return f"""
    <html><head><style>body{{margin:0; font-family:Arial; background:#f4f6f9;}} .content{{margin-left: 260px; padding: 20px;}} .box{{background:white; padding:20px; border-radius:10px; width: 450px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);}} input{{width:100%; padding:10px; margin-bottom:15px; box-sizing:border-box; border:1px solid #ccc; border-radius:4px;}}</style></head>
    <body>
        {render_sidebar('pay')}
        <div class="content">
            <h2>Payment & Fee Settings</h2>
            <div class="box">
                <form action="/update-payment" method="post">
                    <label>Admin UPI ID:</label>
                    <input type="text" name="upi" value="{admin_data['upi_id']}" required>
                    
                    <label>School Registration Fee (₹):</label>
                    <input type="number" name="reg_fee" value="{admin_data['reg_fee']}" required>
                    
                    <label>GST Percentage (%):</label>
                    <input type="number" name="gst_percent" value="{admin_data['gst_percent']}" required>
                    
                    <label>Admin GST Number:</label>
                    <input type="text" name="gst_no" value="{admin_data['gst_no']}" required>
                    
                    <button type="submit" style="padding:10px; background:blue; color:white; width:100%; border:none; border-radius:4px; font-weight:bold; cursor:pointer;">Save Settings & Update QR</button>
                </form>
                <div style="margin-top:20px; text-align:center;">
                    <h4>Auto Generated UPI Barcode:</h4>
                    <img src="{qr}" style="border: 2px solid #ddd; padding:5px; border-radius:5px;">
                </div>
            </div>
        </div>
    </body></html>
    """

@app.post("/update-payment")
async def update_payment(upi: str=Form(...), reg_fee: str=Form(...), gst_percent: str=Form(...), gst_no: str=Form(...)):
    admin_data["upi_id"] = upi
    admin_data["reg_fee"] = reg_fee
    admin_data["gst_percent"] = gst_percent
    admin_data["gst_no"] = gst_no
    return RedirectResponse(url="/payment", status_code=303)

# ୭. Profile
@app.get("/profile", response_class=HTMLResponse)
async def profile():
    return f"""
    <html><head><style>body{{margin:0; font-family:Arial; background:#f4f6f9;}} .content{{margin-left: 260px; padding: 20px;}} input{{width:100%; padding:10px; margin-bottom:10px; box-sizing:border-box;}}</style></head>
    <body>
        {render_sidebar('prof')}
        <div class="content">
            <h2>Manage Profile</h2>
            <div style="background:white; padding:20px; border-radius:10px; width: 400px;">
                <form action="/update-profile" method="post">
                    <label>User Name</label>
                    <input type="text" name="username" value="{admin_data['username']}">
                    <label>New Password</label>
                    <input type="password" name="password" placeholder="Enter new password">
                    <button type="submit" style="padding:10px; background:green; color:white; width:100%; border:none; cursor:pointer;">Update Profile</button>
                </form>
            </div>
        </div>
    </body></html>
    """

@app.post("/update-profile")
async def update_profile(username: str=Form(...), password: str=Form(...)):
    admin_data["username"] = username
    if password: admin_data["password"] = password
    return RedirectResponse(url="/profile", status_code=303)
