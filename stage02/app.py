from flask import Flask, request, render_template_string, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = 'nexus-portal-session'

import hashlib

USERS = {
    'alex': {
        'name': 'Alex Morgan',
        'email': 'alex.morgan@nexus-corp.local',
        'role': 'Operations Analyst',
        'department': 'Operations',
        'password': 'Nexus@2026',
        'user_id': 1002,
        'status': 'Active'
    },
    'admin': {
        'name': 'Amelia Reed',
        'email': 'amelia.reed@nexus-corp.local',
        'role': 'System Administrator',
        'department': 'Infrastructure & Security',
        'password_hash': '97141555d57dfba0c099fc59da278f74',
        'password_hash_type': 'md5',
        'user_id': 1,
        'status': 'Privileged'
    }
}

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nexus Corp | Employee Portal</title>
    <meta name="description" content="Nexus Corporation internal employee portal and access dashboard.">
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='12' fill='%230b1020'/%3E%3Cpath d='M10 18L32 10l22 8v28L32 54 10 46z' fill='none' stroke='%2300c3ff' stroke-width='4'/%3E%3Cpath d='M10 18l22 8 22-8M32 26v28' stroke='%2300c3ff' stroke-width='4' fill='none'/%3E%3C/svg%3E">
    <style>
        :root {
            --bg: #061018;
            --panel: rgba(11, 19, 32, 0.92);
            --line: rgba(255,255,255,0.08);
            --text: #edf6ff;
            --muted: #8ea9c3;
            --blue: #00c3ff;
            --blue-strong: #0066ff;
            --green: #45f5b5;
            --red: #ff5a7a;
            --amber: #ffd76e;
            --purple: #aa71ff;
        }
        * { box-sizing: border-box; }
        body {
            margin: 0;
            font-family: system-ui, -apple-system, sans-serif;
            background: radial-gradient(circle at top left, rgba(0,195,255,0.14), transparent 32%), var(--bg);
            color: var(--text);
            min-height: 100vh;
        }
        a { text-decoration: none; color: inherit; }
        button, input { font: inherit; }
        .container { width: min(1180px, calc(100% - 32px)); margin: 0 auto; }
        header {
            position: sticky;
            top: 0;
            z-index: 50;
            background: rgba(6, 16, 24, 0.82);
            backdrop-filter: blur(16px);
            border-bottom: 1px solid var(--line);
        }
        .nav {
            min-height: 76px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 18px;
        }
        .brand {
            display: flex;
            align-items: center;
            gap: 12px;
            font-weight: 800;
            letter-spacing: -0.05em;
            font-size: 1.3rem;
            text-transform: uppercase;
        }
        .brand-mark {
            width: 30px;
            height: 30px;
            border-radius: 8px;
            display: grid;
            place-items: center;
            background: linear-gradient(135deg, var(--blue), var(--blue-strong));
            box-shadow: 0 12px 30px rgba(0, 195, 255, 0.25);
            font-size: 0.82rem;
        }
        .brand span { color: var(--blue); }
        .nav-links {
            display: flex;
            gap: 22px;
            color: var(--muted);
            font-size: 0.9rem;
        }
        .nav-links a { transition: color 0.2s ease; }
        .nav-links a:hover { color: var(--text); }
        .pill {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 0.75rem 1.1rem;
            border-radius: 10px;
            border: 1px solid rgba(0, 195, 255, 0.30);
            background: rgba(0, 195, 255, 0.08);
            color: var(--text);
            font-weight: 600;
        }
        .page-shell {
            display: grid;
            grid-template-columns: 260px minmax(0, 1fr);
            gap: 22px;
            padding: 34px 0 26px;
        }
        .sidebar, .content-panel, .auth-card {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 20px;
            box-shadow: 0 18px 45px rgba(2, 8, 16, 0.35);
        }
        .sidebar { overflow: hidden; }
        .sidebar-header {
            padding: 14px 18px;
            border-bottom: 1px solid var(--line);
            font-family: 'system-ui', monospace;
            font-size: 0.7rem;
            letter-spacing: 0.12em;
            color: var(--muted);
            text-transform: uppercase;
            background: rgba(255,255,255,0.02);
        }
        .menu { display: flex; flex-direction: column; gap: 8px; padding: 12px; }
        .menu a {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 11px 12px;
            border-radius: 10px;
            color: var(--muted);
            transition: all 0.2s ease;
        }
        .menu a:hover, .menu a.active {
            background: rgba(0,195,255,0.08);
            color: var(--text);
            border: 1px solid rgba(0,195,255,0.15);
        }
        .menu-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: var(--muted);
        }
        .menu a.active .menu-dot { background: var(--blue); }
        .status-box { margin-top: 18px; padding: 14px 18px 18px; }
        .status-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 0.8rem;
            color: var(--muted);
            margin-top: 8px;
        }
        .status-ok {
            color: var(--green);
            font-family: 'system-ui', monospace;
            font-size: 0.72rem;
        }
        .content-panel { padding: 22px; }
        .crumbs {
            font-family: 'system-ui', monospace;
            font-size: 0.7rem;
            color: var(--muted);
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 20px;
        }
        .crumbs span { color: var(--blue); }
        .topbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 14px;
            margin-bottom: 22px;
        }
        .h1 {
            font-size: clamp(1.7rem, 3vw, 2.5rem);
            letter-spacing: -0.05em;
        }
        .subtle {
            color: var(--muted);
            margin-top: 6px;
            font-size: 0.8rem;
            font-family: 'system-ui', monospace;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }
        .action-row { display: flex; flex-wrap: wrap; gap: 10px; }
        .mini-btn {
            padding: 0.7rem 1rem;
            border-radius: 10px;
            border: 1px solid var(--line);
            background: rgba(255,255,255,0.02);
            color: var(--text);
        }
        .card {
            background: rgba(255,255,255,0.02);
            border: 1px solid var(--line);
            border-radius: 18px;
            overflow: hidden;
        }
        .profile-header {
            display: flex;
            align-items: center;
            gap: 18px;
            padding: 22px 24px;
            border-bottom: 1px solid var(--line);
            background: rgba(255,255,255,0.015);
        }
        .avatar {
            width: 66px;
            height: 66px;
            border-radius: 50%;
            display: grid;
            place-items: center;
            font-weight: 800;
            font-size: 1.2rem;
            background: linear-gradient(135deg, var(--blue), var(--purple));
            box-shadow: 0 12px 28px rgba(0,195,255,0.18);
        }
        .profile-meta { flex: 1; }
        .profile-name { font-size: 1.4rem; font-weight: 700; margin-bottom: 4px; }
        .profile-role {
            color: var(--muted);
            font-size: 0.82rem;
            font-family: 'system-ui', monospace;
        }
        .badges { margin-top: 10px; display: flex; flex-wrap: wrap; gap: 8px; }
        .badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 999px;
            border: 1px solid rgba(255,255,255,0.08);
            padding: 5px 10px;
            font-family: 'system-ui', monospace;
            font-size: 0.6rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .badge.blue { color: var(--blue); background: rgba(0,195,255,0.06); }
        .badge.green { color: var(--green); background: rgba(69,245,181,0.06); }
        .badge.red { color: var(--red); background: rgba(255,90,122,0.05); }
        .badge.purple { color: var(--purple); background: rgba(170,113,255,0.05); }
        .profile-body { padding: 22px 24px 24px; }
        .grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 16px;
        }
        .field { display: flex; flex-direction: column; gap: 7px; }
        .field label {
            color: var(--muted);
            font-family: 'system-ui', monospace;
            font-size: 0.62rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }
        .field div {
            border: 1px solid var(--line);
            border-radius: 10px;
            background: rgba(255,255,255,0.02);
            padding: 12px 14px;
            color: var(--text);
        }
        .monospace {
            font-family: 'system-ui', monospace;
            font-size: 0.8rem;
            letter-spacing: 0.04em;
            word-break: break-all;
        }
        .flag {
            color: var(--green);
            background: rgba(69,245,181,0.04);
            border-color: rgba(69,245,181,0.2) !important;
            font-weight: 700;
        }
        .auth-wrap {
            display: grid;
            place-items: center;
            min-height: 70vh;
            padding: 32px 0;
        }
        .auth-card { width: min(450px, calc(100% - 20px)); overflow: hidden; }
        .auth-head {
            padding: 28px 26px 18px;
            text-align: center;
            border-bottom: 1px solid var(--line);
            background: rgba(255,255,255,0.02);
        }
        .auth-head .lock { font-size: 2.2rem; margin-bottom: 12px; }
        .auth-head h2 { font-size: 1.5rem; margin-bottom: 6px; letter-spacing: -0.04em; }
        .auth-head p {
            color: var(--muted);
            font-size: 0.9rem;
            line-height: 1.6;
        }
        .auth-body { padding: 24px 26px 22px; }
        .form-row { display: flex; flex-direction: column; gap: 8px; margin-bottom: 14px; }
        .label {
            color: var(--muted);
            font-family: 'system-ui', monospace;
            font-size: 0.65rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }
        .input {
            width: 100%;
            border: 1px solid var(--line);
            border-radius: 10px;
            padding: 0.9rem 1rem;
            background: rgba(7,14,23,0.85);
            color: var(--text);
            outline: none;
            transition: border 0.2s ease, box-shadow 0.2s ease;
        }
        .input:focus {
            border-color: rgba(0,195,255,0.45);
            box-shadow: 0 0 0 3px rgba(0,195,255,0.08);
        }
        .submit {
            width: 100%;
            margin-top: 8px;
            border: none;
            border-radius: 10px;
            padding: 0.95rem 1rem;
            background: linear-gradient(135deg, var(--blue), var(--blue-strong));
            color: white;
            font-weight: 700;
            cursor: pointer;
        }
        .error {
            margin-top: 16px;
            padding: 10px 12px;
            border-radius: 10px;
            background: rgba(255,90,122,0.06);
            border: 1px solid rgba(255,90,122,0.25);
            color: #ff93a8;
            font-size: 0.84rem;
        }
        .cta-link {
            text-align: center;
            margin-top: 16px;
            color: var(--muted);
            font-size: 0.82rem;
        }
        .cta-link a { color: var(--blue); }
        @media (max-width: 860px) {
            .page-shell { grid-template-columns: 1fr; }
            .grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <header>
        <div class="container nav">
            <div class="brand">NEXUS<span>CORP</span></div>
            <nav class="nav-links" aria-label="Main navigation">
                <a href="http://localhost:8000/">Corporate Site</a>
                <a href="#" style="opacity: 0.5; text-decoration: line-through; cursor: not-allowed;">Directory</a>
                <a href="#" style="opacity: 0.5; text-decoration: line-through; cursor: not-allowed;">Payroll</a>
                <a href="http://localhost:8081/">Support (ARIA)</a>
            </nav>
            <a class="pill" href="http://localhost:8081/">ARIA Support</a>
        </div>
    </header>

    {% if not logged_in %}
    <div class="container auth-wrap">
        <div class="auth-card">
            <div class="auth-head">
                <div class="lock">🔒</div>
                <h2>{% if mode == 'login' %}Employee Login{% else %}Secure Employee Access{% endif %}</h2>
                <p>{% if mode == 'login' %}Sign in to continue to your internal dashboard.{% else %}Create your employee profile to access the Nexus internal portal.{% endif %}</p>
            </div>
            <div class="auth-body">
                {% if registration_success %}<div class="error" style="background:rgba(69,245,181,0.06);border-color:rgba(69,245,181,0.25);color:var(--green);" role="status">Employee profile created. Sign in with your new credentials.</div>{% endif %}
                {% if mode == 'login' %}
                <form method="POST" action="/login">
                    <div class="form-row">
                        <label class="label" for="login_email">Work email</label>
                        <input id="login_email" class="input" type="email" name="email" placeholder="name@nexus-corp.local" required>
                    </div>
                    <div class="form-row">
                        <label class="label" for="login_password">Password</label>
                        <input id="login_password" class="input" type="password" name="password" placeholder="Enter your password" required>
                    </div>
                    <button class="submit" type="submit">Log in to portal</button>
                </form>
                <div class="cta-link">Need an account? <a href="/register">Register here</a></div>
                {% else %}
                <form method="POST" action="/register">
                    <div class="form-row">
                        <label class="label" for="reg_name">Full name</label>
                        <input id="reg_name" class="input" type="text" name="full_name" placeholder="e.g. Alex Morgan" required>
                    </div>
                    <div class="form-row">
                        <label class="label" for="login_email">Work email</label>
                        <input id="login_email" class="input" type="email" name="email" placeholder="name@nexus-corp.local" required>
                    </div>
                    <div class="form-row">
                        <label class="label" for="login_password">Password</label>
                        <input id="login_password" class="input" type="password" name="password" placeholder="Create a secure password" required>
                    </div>
                    <button class="submit" type="submit">Create employee account</button>
                </form>
                <div class="cta-link">Already registered? <a href="/login">Log in</a></div>
                {% endif %}
                {% if error %}<div class="error">{{ error }}</div>{% endif %}
            </div>
        </div>
    </div>
    {% else %}
    <main class="container page-shell">
        <aside class="sidebar">
            <div class="sidebar-header">Main Menu</div>
            <div class="menu">
                <a class="active" href="/dashboard"><span class="menu-dot"></span>Dashboard</a>
                <a href="/profile?user_id={{ user.user_id }}"><span class="menu-dot"></span>My Profile</a>
                <a href="http://localhost:8000/"><span class="menu-dot"></span>Main Corporate Site</a>
                <a href="http://localhost:8081/"><span class="menu-dot"></span>ARIA Agent</a>
            </div>
        </aside>
        <div class="content">
            <div class="page-head" style="margin-bottom: 20px;">
            </div>
            
            {% if request.path == '/dashboard' %}
            <div class="profile-body" style="padding-top:0;">
                <h3 style="margin-bottom: 20px;">Welcome back, {{ user.name }}</h3>
                <p style="color: var(--muted); font-size: 0.9rem; margin-bottom: 30px; max-width: 600px;">
                    This is your personal employee dashboard. Access to internal networks and data is restricted based on your role ({{ user.role }}). Ensure all confidential materials are handled according to Nexus Corp policies.
                </p>
                <div class="grid">
                    <div class="field"><label>Employee ID</label><div>{{ user.user_id }}</div></div>
                    <div class="field"><label>Role</label><div>{{ user.role }}</div></div>
                    <div class="field"><label>Department</label><div>{{ user.department }}</div></div>
                    <div class="field"><label>Account Status</label><div style="color: var(--green);">{{ user.status }}</div></div>
                </div>
            </div>
            {% elif request.path == '/profile' %}
            <div class="profile-body" style="padding-top:0;">
                <h3 style="margin-bottom: 20px;">Employee Profile</h3>
                <div class="grid">
                    <div class="field"><label>Employee Name</label><div>{{ target_user.name }}</div></div>
                    <div class="field"><label>Email Address</label><div>{{ target_user.email }}</div></div>
                    <div class="field"><label>Department</label><div>{{ target_user.department }}</div></div>
                    <div class="field"><label>Role</label><div>{{ target_user.role }}</div></div>
                    {% if is_admin %}
                    <div class="field"><label>Credential Hash (MD5)</label><div class="monospace">{{ target_user.password_hash }}</div></div>
                    <div class="field"><label>Admin Flag</label><div class="flag">CTF{1d0r_c4n_b3_f4t4l}</div></div>
                    {% endif %}
                </div>
            </div>
            {% endif %}
            
        </div>
    </main>
    {% endif %}
</body>
</html>
'''

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        
        for u_id, u_info in USERS.items():
            if u_info['email'].lower() != email.strip().lower():
                continue
            if u_info.get('password_hash_type') == 'md5':
                authenticated = hashlib.md5(password.encode()).hexdigest() == u_info['password_hash']
            elif u_info.get('password_hash_type') == 'werkzeug':
                authenticated = check_password_hash(u_info['password_hash'], password)
            else:
                authenticated = u_info.get('password') == password
            if authenticated:
                session['user'] = u_id
                return redirect(url_for('dashboard'))
                
        return render_template_string(HTML_TEMPLATE, logged_in=False, mode='login', error='Invalid email or password.')
        
    return render_template_string(HTML_TEMPLATE, logged_in=False, mode='login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        if not name or '@' not in email or len(password) < 8:
            return render_template_string(HTML_TEMPLATE, logged_in=False, mode='register',
                                          error='Enter a name, a valid email address, and a password of at least 8 characters.')
        if any(u_info['email'].lower() == email for u_info in USERS.values()):
            return render_template_string(HTML_TEMPLATE, logged_in=False, mode='register',
                                          error='An account already exists for this email address.')
        new_id = max(u_info['user_id'] for u_info in USERS.values()) + 1
        USERS[f'user_{new_id}'] = {
            'name': name,
            'email': email,
            'role': 'Employee',
            'department': 'Unassigned',
            'password_hash': generate_password_hash(password),
            'password_hash_type': 'werkzeug',
            'user_id': new_id,
            'status': 'Active'
        }
        return render_template_string(HTML_TEMPLATE, logged_in=False, mode='login',
                                      registration_success=True)
    return render_template_string(HTML_TEMPLATE, logged_in=False, mode='register')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    if isinstance(session['user'], dict) or session['user'] not in USERS:
        session.clear()
        return redirect(url_for('login'))
    user = USERS[session['user']]
    return render_template_string(HTML_TEMPLATE, logged_in=True, user=user)

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    if isinstance(session['user'], dict) or session['user'] not in USERS:
        session.clear()
        return redirect(url_for('login'))
        
    user = USERS[session['user']]
    
    # IDOR vulnerability here!
    target_id = request.args.get('user_id', str(user['user_id']))
    
    target_user = None
    for u_info in USERS.values():
        if str(u_info['user_id']) == target_id:
            target_user = u_info
            break
            
    if not target_user:
        return "User not found", 404
        
    is_admin = (str(target_user['user_id']) == '1')
    
    return render_template_string(HTML_TEMPLATE, logged_in=True, user=user, target_user=target_user, is_admin=is_admin)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
