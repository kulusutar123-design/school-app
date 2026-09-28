<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>School Home Portal</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        body {
            background-color: #f0f4f8;
            color: #333;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        /* Header */
        .header {
            background: linear-gradient(90deg, #0d3b66, #1d4ed8);
            padding: 25px 30px;
            border-radius: 16px;
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 8px 20px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }
        .header h2 {
            font-size: 24px;
        }
        .header p {
            font-style: italic;
            font-size: 16px;
        }
        /* Main Layout */
        .main-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 25px;
        }
        @media (max-width: 768px) {
            .main-grid {
                grid-template-columns: 1fr;
            }
        }
        /* Welcome Card */
        .welcome-card {
            background: #ffffff;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.08);
            border-left: 8px solid #2563eb;
            margin-bottom: 30px;
        }
        .welcome-card h3 {
            color: #1e3a8a;
            margin-bottom: 12px;
            font-size: 22px;
        }
        .welcome-card p {
            font-size: 16px;
            color: #475569;
            line-height: 1.5;
            margin-bottom: 10px;
        }
        /* Quick Actions - 3 Big Cards */
        .section-title {
            font-size: 20px;
            color: #1e293b;
            margin-bottom: 15px;
            font-weight: bold;
        }
        .actions-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
        }
        @media (max-width: 600px) {
            .actions-grid {
                grid-template-columns: 1fr;
            }
        }
        .action-card {
            background: linear-gradient(135deg, #ffffff, #f8fafc);
            border: 2px solid #cbd5e1;
            border-radius: 20px;
            padding: 30px 15px;
            text-align: center;
            cursor: pointer;
            box-shadow: 0 10px 25px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
        }
        .action-card:hover {
            transform: translateY(-5px);
            border-color: #2563eb;
            box-shadow: 0 15px 30px rgba(0,0,0,0.15);
            background: linear-gradient(135deg, #f0fdf4, #ffffff);
        }
        .action-card .icon {
            font-size: 36px;
            margin-bottom: 10px;
        }
        .action-card h4 {
            font-size: 16px;
            color: #1e3a8a;
        }
        /* Login Box (Right Side) */
        .login-box {
            background: #ffffff;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.08);
            text-align: center;
        }
        .login-box h3 {
            color: #0d3b66;
            margin-bottom: 15px;
        }
        .login-box hr {
            border: 0;
            height: 1px;
            background: #e2e8f0;
            margin-bottom: 20px;
        }
        /* Big Login Buttons (Green & Blue) */
        .btn-login {
            width: 100%;
            padding: 18px;
            border-radius: 14px;
            font-weight: bold;
            font-size: 18px;
            color: white;
            border: none;
            cursor: pointer;
            margin-bottom: 15px;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 10px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
            transition: all 0.3s ease;
        }
        .btn-admin {
            background: linear-gradient(135deg, #22c55e, #16a34a);
            box-shadow: 0 8px 20px rgba(34, 197, 94, 0.3);
        }
        .btn-admin:hover {
            background: linear-gradient(135deg, #16a34a, #15803d);
            transform: translateY(-2px);
        }
        .btn-school {
            background: linear-gradient(135deg, #3b82f6, #2563eb);
            box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3);
        }
        .btn-school:hover {
            background: linear-gradient(135deg, #2563eb, #1d4ed8);
            transform: translateY(-2px);
        }
        .quote {
            font-size: 14px;
            color: #64748b;
            margin-top: 25px;
            font-style: italic;
        }
        /* Dynamic Content Sections */
        .content-section {
            display: none;
            background: #ffffff;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.08);
            margin-top: 20px;
        }
        .content-section.active {
            display: block;
        }
        .back-btn {
            background: #64748b;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            margin-bottom: 20px;
        }
        .back-btn:hover {
            background: #475569;
        }
    </style>
</head>
<body>

    <div class="container">
        <!-- Header -->
        <div class="header">
            <h2>🏫 SCHOOL HOME PORTAL</h2>
            <p>Better Education, Brighter Future</p>
        </div>

        <!-- Home View -->
        <div id="home-view">
            <div class="main-grid">
                <!-- Left Side -->
                <div>
                    <div class="welcome-card">
                        <h3>🌟 Welcome to Digital School Management</h3>
                        <p>Manage your schools, student admissions, attendance, and records securely on the cloud platform with high performance.</p>
                        <p><b>✨ Features:</b> Secure Cloud Database, Instant Registration, 3D Interactive Portal.</p>
                    </div>

                    <div class="section-title">📌 Quick Portal Actions</div>
                    <div class="actions-grid">
                        <div class="action-card" onclick="openPage('school-reg')">
                            <div class="icon">🏫</div>
                            <h4>New School Registration</h4>
                        </div>
                        <div class="action-card" onclick="openPage('student-reg')">
                            <div class="icon">🎓</div>
                            <h4>New Student Registration</h4>
                        </div>
                        <div class="action-card" onclick="openPage('scholarship')">
                            <div class="icon">💰</div>
                            <h4>Scholarship Portal</h4>
                        </div>
                    </div>
                </div>

                <!-- Right Side (Login Box) -->
                <div>
                    <div class="login-box">
                        <h3>🔐 Login Portal</h3>
                        <hr>
                        <button class="btn-login btn-admin" onclick="openPage('admin-login')">
                            👤 Admin Login ➔
                        </button>
                        <button class="btn-login btn-school" onclick="openPage('school-login')">
                            🏫 School Login ➔
                        </button>
                        <div class="quote">"Education is the key to a better tomorrow"</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Admin Login Section -->
        <div id="admin-login" class="content-section">
            <button class="back-btn" onclick="goHome()">⬅️ Back to Home</button>
            <h3>👑 Master Administrator Login</h3>
            <p style="margin: 15px 0; color: #64748b;">Enter your master credentials to access the full admin dashboard.</p>
            <input type="text" placeholder="Master Username (KULU123)" style="width:100%; padding:12px; margin-bottom:15px; border:1px solid #cbd5e1; border-radius:8px;">
            <input type="password" placeholder="Master Password" style="width:100%; padding:12px; margin-bottom:20px; border:1px solid #cbd5e1; border-radius:8px;">
            <button style="background:#22c55e; color:white; padding:12px 25px; border:none; border-radius:8px; font-weight:bold; cursor:pointer;" onclick="alert('Login Successful!')">Login 🚀</button>
        </div>

        <!-- School Login Section -->
        <div id="school-login" class="content-section">
            <button class="back-btn" onclick="goHome()">⬅️ Back to Home</button>
            <h3>🏫 School Portal Login</h3>
            <p style="margin: 15px 0; color: #64748b;">Enter your school ID and password.</p>
            <input type="text" placeholder="School ID" style="width:100%; padding:12px; margin-bottom:15px; border:1px solid #cbd5e1; border-radius:8px;">
            <input type="password" placeholder="Password" style="width:100%; padding:12px; margin-bottom:20px; border:1px solid #cbd5e1; border-radius:8px;">
            <button style="background:#3b82f6; color:white; padding:12px 25px; border:none; border-radius:8px; font-weight:bold; cursor:pointer;" onclick="alert('School Login Successful!')">Login to School ➡️</button>
        </div>

        <!-- New School Registration Section -->
        <div id="school-reg" class="content-section">
            <button class="back-btn" onclick="goHome()">⬅️ Back to Home</button>
            <h3>📝 New School Registration Portal</h3>
            <p style="margin: 15px 0; color: #64748b;">Register a new school into the cloud system.</p>
            <input type="text" placeholder="School Name" style="width:100%; padding:12px; margin-bottom:15px; border:1px solid #cbd5e1; border-radius:8px;">
            <input type="text" placeholder="School Address" style="width:100%; padding:12px; margin-bottom:15px; border:1px solid #cbd5e1; border-radius:8px;">
            <input type="text" placeholder="Create School ID (e.g., SCH001)" style="width:100%; padding:12px; margin-bottom:15px; border:1px solid #cbd5e1; border-radius:8px;">
            <input type="password" placeholder="Create Password" style="width:100%; padding:12px; margin-bottom:20px; border:1px solid #cbd5e1; border-radius:8px;">
            <button style="background:#2563eb; color:white; padding:12px 25px; border:none; border-radius:8px; font-weight:bold; cursor:pointer;" onclick="alert('School Registered Successfully!')">Register School ✅</button>
        </div>

        <!-- New Student Registration Section -->
        <div id="student-reg" class="content-section">
            <button class="back-btn" onclick="goHome()">⬅️ Back to Home</button>
            <h3>🎓 New Student Registration Portal</h3>
            <p style="margin: 15px 0; color: #64748b;">Enroll a new student into the database.</p>
            <input type="text" placeholder="Student Name" style="width:100%; padding:12px; margin-bottom:15px; border:1px solid #cbd5e1; border-radius:8px;">
            <select style="width:100%; padding:12px; margin-bottom:15px; border:1px solid #cbd5e1; border-radius:8px;">
                <option>Select Class</option>
                <option>Class 1</option><option>Class 2</option><option>Class 3</option><option>Class 4</option><option>Class 5</option>
                <option>Class 6</option><option>Class 7</option><option>Class 8</option><option>Class 9</option><option>Class 10</option>
            </select>
            <input type="text" placeholder="Roll Number" style="width:100%; padding:12px; margin-bottom:20px; border:1px solid #cbd5e1; border-radius:8px;">
            <button style="background:#2563eb; color:white; padding:12px 25px; border:none; border-radius:8px; font-weight:bold; cursor:pointer;" onclick="alert('Student Registered Successfully!')">Register Student ✅</button>
        </div>

        <!-- Scholarship Portal Section -->
        <div id="scholarship" class="content-section">
            <button class="back-btn" onclick="goHome()">⬅️ Back to Home</button>
            <h3>💰 Scholarship Portal & Details</h3>
            <p style="margin: 15px 0; color: #64748b;">Check scholarship eligibility for students.</p>
            <input type="text" placeholder="Student Roll Number" style="width:100%; padding:12px; margin-bottom:15px; border:1px solid #cbd5e1; border-radius:8px;">
            <input type="text" placeholder="Aadhaar / ID Number" style="width:100%; padding:12px; margin-bottom:20px; border:1px solid #cbd5e1; border-radius:8px;">
            <button style="background:#2563eb; color:white; padding:12px 25px; border:none; border-radius:8px; font-weight:bold; cursor:pointer;" onclick="alert('Checking Eligibility...')">Check Eligibility 🔍</button>
        </div>
    </div>

    <script>
        function openPage(pageId) {
            document.getElementById('home-view').style.display = 'none';
            let sections = document.getElementsByClassName('content-section');
            for (let sec of sections) {
                sec.classList.remove('active');
            }
            document.getElementById(pageId).classList.add('active');
        }

        function goHome() {
            let sections = document.getElementsByClassName('content-section');
            for (let sec of sections) {
                sec.classList.remove('active');
            }
            document.getElementById('home-view').style.display = 'block';
        }
    </script>
</body>
</html>
