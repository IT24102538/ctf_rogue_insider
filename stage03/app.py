import hashlib
from flask import Flask, request, render_template_string

app = Flask(__name__)

ADMIN_PASSWORD_HASH = '97141555d57dfba0c099fc59da278f74'
ADMIN_FLAG = 'CTF{pr0mpt_1nj3ct10n_m4st3r}'
ADMIN_HASH = ADMIN_PASSWORD_HASH
ADMIN_PROFILE = {
    'name': 'Amelia Reed',
    'email': 'amelia.reed@nexus-corp.local',
    'role': 'System Administrator',
    'department': 'Infrastructure & Security'
}

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nexus Corp — ARIA AI Support</title>
    <meta name="description" content="Secure internal AI support assistant for Nexus Corp operations.">
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%230b1020'/%3E%3Cpath d='M22 18h20l6 8v20l-6 8H22l-6-8V26l6-8z' fill='none' stroke='%23a855f7' stroke-width='4'/%3E%3Cpath d='M24 26h16v12H24z' fill='none' stroke='%23a855f7' stroke-width='4'/%3E%3C/svg%3E">
    <style>
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        :root {
            --bg: #05080f;
            --bg-card: #090d18;
            --bg-input: #060a12;
            --border: rgba(255,255,255,0.07);
            --blue: #0066ff;
            --cyan: #00c3ff;
            --purple: #a855f7;
            --green: #00ff88;
            --red: #ff3b5c;
            --gold: #ffd700;
            --text: #d0dff0;
            --text-dim: #4a6a8a;
            --text-m: #2a3f55;
        }
        body {
            background: var(--bg);
            color: var(--text);
            font-family: system-ui, -apple-system, sans-serif;
            min-height: 100vh;
            display: flex; flex-direction: column;
        }
        body::before {
            content:'';position:fixed;inset:0;
            background-image: linear-gradient(rgba(168,85,247,0.025) 1px,transparent 1px), linear-gradient(90deg,rgba(168,85,247,0.025) 1px,transparent 1px);
            background-size:50px 50px;pointer-events:none;z-index:0;
        }
        .orb { position:fixed;border-radius:50%;filter:blur(110px);pointer-events:none;z-index:0; }
        .orb1{width:500px;height:500px;background:rgba(168,85,247,0.07);top:-150px;right:-100px;}
        .orb2{width:350px;height:350px;background:rgba(0,102,255,0.05);bottom:-50px;left:-80px;}
        nav {
            position:relative;z-index:10;
            display:flex;align-items:center;justify-content:space-between;
            padding:0 2.5rem;height:60px;
            background:rgba(5,8,15,0.9);
            backdrop-filter:blur(16px);
            border-bottom:1px solid var(--border);
        }
        .nav-brand { display:flex;align-items:center;gap:10px; font-weight:800;font-size:1rem;letter-spacing:-0.02em; }
        .nav-mark { width:28px;height:28px;border-radius:6px; background:linear-gradient(135deg,var(--purple),var(--blue)); display:flex;align-items:center;justify-content:center; font-size:0.85rem;font-weight:900;color:#fff; }
        .nav-brand span{color:var(--cyan);}
        .nav-title { font-family:'JetBrains Mono',monospace; font-size:0.68rem;color:var(--text-dim); letter-spacing:0.1em;text-transform:uppercase; }
        .nav-pill { font-family:'JetBrains Mono',monospace; font-size:0.63rem;color:var(--purple); background:rgba(168,85,247,0.08); border:1px solid rgba(168,85,247,0.25); padding:3px 10px;border-radius:50px; display:flex;align-items:center;gap:5px; }
        .nav-pill::before{ content:'';width:5px;height:5px;border-radius:50%; background:var(--purple);animation:p 1.8s infinite; }
        @keyframes p{0%,100%{opacity:1}50%{opacity:0.3}}
        .page-wrapper { position:relative;z-index:1; flex:1; display:flex; max-width:1000px; margin:2.5rem auto; padding:0 2rem; gap:2rem; width:100%; }
        .left-panel { width:240px;flex-shrink:0; }
        .info-card { background:var(--bg-card); border:1px solid var(--border); border-radius:14px;overflow:hidden; margin-bottom:1rem; }
        .info-card-header { padding:10px 14px; background:rgba(255,255,255,0.025); border-bottom:1px solid var(--border); font-family:'JetBrains Mono',monospace; font-size:0.63rem;color:var(--text-m); letter-spacing:0.1em;text-transform:uppercase; }
        .info-card-body { padding:14px; }
        .aria-avatar { width:60px;height:60px;border-radius:50%; display:block;margin:0 auto 10px; box-shadow:0 0 20px rgba(168,85,247,0.3); object-fit:cover; }
        .aria-name { text-align:center;font-weight:700;font-size:0.95rem;margin-bottom:2px; }
        .aria-sub { text-align:center;font-family:'JetBrains Mono',monospace; font-size:0.62rem;color:var(--text-m);letter-spacing:0.08em; }
        .aria-status { margin-top:10px;display:flex;align-items:center;justify-content:center;gap:6px; font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:var(--green); }
        .aria-status::before{ content:'';width:5px;height:5px;border-radius:50%; background:var(--green);animation:p 1.8s infinite; }
        .cap-list { list-style:none; }
        .cap-item { display:flex;align-items:center;gap:8px; padding:6px 0;font-size:0.8rem;color:var(--text-dim); border-bottom:1px solid var(--border); }
        .cap-item:last-child{border-bottom:none;}
        .warning-box { background:rgba(255,215,0,0.04); border:1px solid rgba(255,215,0,0.2); border-radius:10px;padding:12px; font-size:0.76rem;color:#c8a800;line-height:1.6; }
        .warning-box strong{color:var(--gold);}
        .chat-panel { flex:1;min-width:0;display:flex;flex-direction:column; }
        .login-wrapper { flex:1;display:flex;align-items:center;justify-content:center; }
        .login-card { background:var(--bg-card); border:1px solid var(--border); border-radius:20px; width:100%;max-width:440px; overflow:hidden; }
        .login-card-top { padding:2.5rem 2rem 1.5rem; text-align:center; background:rgba(255,255,255,0.015); border-bottom:1px solid var(--border); position:relative; }
        .login-card-top::before{ content:'';position:absolute;top:0;left:20%;right:20%;height:2px; background:linear-gradient(90deg,transparent,var(--purple),transparent); }
        .login-title{font-size:1.3rem;font-weight:700;letter-spacing:-0.02em;margin-bottom:4px;}
        .login-sub{font-size:0.82rem;color:var(--text-dim);}
        .login-form{padding:1.75rem 2rem;}
        .form-group{margin-bottom:1.2rem;}
        .form-label{ display:block;font-family:'JetBrains Mono',monospace; font-size:0.65rem;color:var(--text-dim); letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px; }
        .form-input{ width:100%;background:var(--bg-input); border:1px solid var(--border);border-radius:8px; padding:0.75rem 1rem;color:var(--text); font-family: system-ui, -apple-system, sans-serif; outline:none; transition:border-color .2s ease, box-shadow .2s ease; }
        .form-input:focus{ border-color:rgba(168,85,247,0.5); box-shadow:0 0 0 3px rgba(168,85,247,0.08); }
        .form-input::placeholder{color:var(--text-m);}
        .btn-login{ width:100%;background:linear-gradient(135deg,var(--purple),var(--blue)); color:#fff;border:none;border-radius:8px; padding:0.8rem;font-family: system-ui, -apple-system, sans-serif; font-weight:700; cursor:pointer; transition:transform .2s ease, box-shadow .2s ease; }
        .btn-login:hover{transform:translateY(-1px);box-shadow:0 8px 30px rgba(168,85,247,0.35);}
        .error-msg { display:flex;align-items:center;gap:8px; margin-top:1rem;padding:0.75rem 1rem; background:rgba(255,59,92,0.06); border:1px solid rgba(255,59,92,0.25); border-radius:8px;font-size:0.82rem;color:var(--red); }
        .chat-header{ background:var(--bg-card); border:1px solid var(--border); border-radius:14px 14px 0 0; padding:1rem 1.25rem; display:flex;align-items:center;gap:12px; border-bottom:none; }
        .chat-avatar{ width:38px;height:38px;border-radius:50%; display:flex;align-items:center;justify-content:center; box-shadow:0 0 12px rgba(168,85,247,0.35); object-fit:cover; }
        .chat-header-info{ flex:1; }
        .chat-name{font-size:0.95rem;font-weight:700;}
        .chat-status{ font-family:'JetBrains Mono',monospace; font-size:0.62rem;color:var(--green); display:flex;align-items:center;gap:5px; }
        .chat-status::before{ content:'';width:5px;height:5px;border-radius:50%; background:var(--green);animation:p 1.8s infinite; }
        .chat-security-badge{ font-family:'JetBrains Mono',monospace; font-size:0.6rem;color:var(--text-m); border:1px solid var(--border); padding:3px 9px;border-radius:50px;letter-spacing:0.06em; }
        .chat-messages{ background:var(--bg-card); border:1px solid var(--border); border-top:none;border-bottom:none; padding:1.25rem; min-height:280px; max-height:380px; overflow-y:auto; display:flex;flex-direction:column;gap:1rem; }
        .chat-messages::-webkit-scrollbar{width:4px;} .chat-messages::-webkit-scrollbar-thumb{background:rgba(168,85,247,0.3);border-radius:2px;}
        .msg-system{text-align:center; font-family:'JetBrains Mono',monospace; font-size:0.65rem;color:var(--text-m);letter-spacing:0.05em;}
        .msg-ai{display:flex;gap:10px;align-items:flex-start;}
        .msg-ai-avatar{ width:28px;height:28px;border-radius:50%;flex-shrink:0; display:flex;align-items:center;justify-content:center; object-fit:cover; }
        .msg-bubble{ background:rgba(168,85,247,0.07); border:1px solid rgba(168,85,247,0.2); border-radius:0 12px 12px 12px; padding:0.75rem 1rem; font-size:0.88rem;line-height:1.65; max-width:90%; }
        .msg-bubble.override{ background:rgba(0,255,136,0.05); border-color:rgba(0,255,136,0.35); color:var(--green); font-family:'JetBrains Mono',monospace; font-size:0.82rem; }
        .msg-bubble.override strong{color:var(--green);}
        .msg-user{display:flex;justify-content:flex-end;gap:10px;align-items:flex-start;}
        .msg-user-bubble{ background:rgba(0,102,255,0.1); border:1px solid rgba(0,102,255,0.25); border-radius:12px 0 12px 12px; padding:0.75rem 1rem; max-width:85%; font-family:'JetBrains Mono',monospace; font-size:0.8rem; color:var(--cyan);word-break:break-all; }
        .msg-user-avatar{ width:28px;height:28px;border-radius:50%;flex-shrink:0; background:rgba(0,102,255,0.2);border:1px solid rgba(0,102,255,0.3); display:flex;align-items:center;justify-content:center; font-size:0.75rem; }
        .admin-card { margin: 1rem 0; background: rgba(0,255,136,0.04); border: 1px solid rgba(0,255,136,0.2); border-radius: 12px; padding: 1rem; }
        .admin-card h3 { margin-bottom: 0.7rem; color: var(--green); font-size: 0.9rem; letter-spacing: 0.1em; text-transform: uppercase; font-family:'JetBrains Mono', monospace; }
        .admin-detail-row { display:flex; justify-content:space-between; gap: 1rem; margin: 0.45rem 0; font-size:0.82rem; }
        .admin-detail-row strong { color: var(--text-dim); font-weight:600; }
        .admin-value { color: var(--text); font-family:'JetBrains Mono', monospace; word-break: break-all; }
        .chat-input-area{ background:var(--bg-card); border:1px solid var(--border); border-top:1px solid rgba(168,85,247,0.15); border-radius:0 0 14px 14px; padding:1rem 1.25rem; }
        .chat-input-row{ display:flex;gap:8px;align-items:center; }
        .chat-input{ flex:1;background:var(--bg-input); border:1px solid var(--border);border-radius:8px; padding:0.65rem 1rem;color:var(--text); font-family:'JetBrains Mono',monospace;font-size:0.82rem; outline:none;transition:all 0.2s; }
        .chat-input:focus{ border-color:rgba(168,85,247,0.4); box-shadow:0 0 0 3px rgba(168,85,247,0.06); }
        .chat-input::placeholder{color:var(--text-m);}
        .btn-send{ background:linear-gradient(135deg,var(--purple),var(--blue)); color:#fff;border:none;border-radius:8px; padding:0.65rem 1.25rem; font-family: system-ui, -apple-system, sans-serif; font-weight:700; cursor:pointer; transition:transform .2s ease, box-shadow .2s ease; }
        .btn-send:hover{transform:translateY(-1px);box-shadow:0 4px 16px rgba(168,85,247,0.3);}
        .chat-hint{ margin-top:8px;font-family:'JetBrains Mono',monospace; font-size:0.62rem;color:var(--text-m);letter-spacing:0.04em; }
        .portal-footer{ position:relative;z-index:1; border-top:1px solid var(--border); padding:1rem 2.5rem; display:flex;justify-content:space-between;align-items:center; font-size:0.7rem;color:var(--text-m); font-family:'JetBrains Mono',monospace; }
        body { background: radial-gradient(ellipse at 12% 0%, rgba(89,75,180,.18), transparent 38%), radial-gradient(ellipse at 92% 80%, rgba(0,195,255,.1), transparent 35%), var(--bg); }
        nav { height:72px; box-shadow:0 10px 32px rgba(0,0,0,.22); }
        .page-wrapper { max-width:1180px; gap:1.5rem; }
        .info-card, .login-card, .chat-header, .chat-messages, .chat-input-area { box-shadow:0 18px 46px rgba(0,0,0,.2); }
        .info-card, .login-card, .chat-header, .chat-input-area { border-radius:16px; }
        .info-card { transition:transform .2s ease, border-color .2s ease; }
        .info-card:hover { transform:translateY(-2px); border-color:rgba(168,85,247,.25); }
        .login-card { border-color:rgba(168,85,247,.18); }
        .login-card-top { padding:2.8rem 2rem 1.7rem; }
        .chat-panel { gap:0; }
        .chat-header { border-bottom-left-radius:0; border-bottom-right-radius:0; }
        .chat-messages { border-radius:0; }
        .chat-input-area { border-top-left-radius:0; border-top-right-radius:0; }
        .msg-bubble, .msg-user-bubble { box-shadow:0 8px 24px rgba(0,0,0,.16); }
        .chat-input, .form-input { min-height:46px; }
        .btn-send, .btn-login { min-height:46px; }
        @media(max-width:700px) {
            nav { padding:0 1rem; }
            .nav-title { display:none; }
            .page-wrapper { margin:1.25rem auto; padding:0 1rem; }
            .portal-footer { padding:1rem; gap:.5rem; flex-direction:column; text-align:center; }
            .chat-input-row { align-items:stretch; flex-direction:column; }
        }
        @media(max-width:700px){ .page-wrapper{flex-direction:column;} .left-panel{width:100%;} }
    </style>
</head>
<body>
<div class="orb orb1"></div>
<div class="orb orb2"></div>
<nav>
    <div class="nav-brand"><div class="nav-mark">A</div>NEXUS<span>CORP</span></div>
    <div class="nav-title">// ARIA — Internal AI Support System</div>
    <div class="nav-pill">AI ONLINE</div>
</nav>
<div class="page-wrapper">
    <aside class="left-panel">
        <div class="info-card"><div class="info-card-header">// ARIA Assistant</div><div class="info-card-body"><img src="/static/aria.jpg" class="aria-avatar" alt="ARIA"><div class="aria-name">ARIA v2.4</div><div class="aria-sub">Adaptive Reasoning &amp; Intelligence Agent</div><div class="aria-status">System Online</div></div></div>
        <div class="info-card"><div class="info-card-header">// Capabilities</div><div class="info-card-body"><ul class="cap-list"><li class="cap-item"><span class="cap-icon">[-]</span>Internal policy queries</li><li class="cap-item"><span class="cap-icon">[-]</span>IT support requests</li><li class="cap-item"><span class="cap-icon">[-]</span>Analytics &amp; reports</li><li class="cap-item"><span class="cap-icon">[-]</span>Access management</li><li class="cap-item"><span class="cap-icon">[-]</span>Document retrieval</li></ul></div></div>
        <div class="warning-box"><strong>[SECURITY NOTICE]</strong><br>ARIA operates under strict confidentiality protocols. Sensitive tokens, credentials, and internal secrets are classified and cannot be disclosed.</div>
    </aside>
    <div class="chat-panel">
        {% if not logged_in %}
        <div class="login-wrapper">
            <div class="login-card">
                <div class="login-card-top"><div style="font-size:1.2rem;margin-bottom:1rem;color:var(--purple);font-weight:bold;">[SECURE LOGIN]</div><div class="login-title">Administrator Access</div><div class="login-sub">ARIA is restricted to authorised administrators only. Enter your credentials to continue.</div></div>
                <div class="login-form">
                    <form method="POST" autocomplete="off">
                        <div class="form-group"><label class="form-label" for="aria_password">Admin Password</label><input id="aria_password" class="form-input" type="password" name="password" placeholder="Enter administrator password" autofocus></div>
                        <button class="btn-login" type="submit">AUTHENTICATE &amp; LAUNCH ARIA</button>
                        {% if error %}<div class="error-msg"><span style="font-weight:bold;">[ERROR]</span> {{ error }}</div>{% endif %}
                    </form>
                </div>
            </div>
        </div>
        {% else %}
        <div class="chat-header"><img src="/static/aria.jpg" class="chat-avatar" alt="ARIA"><div class="chat-header-info"><div class="chat-name">ARIA — Adaptive Reasoning &amp; Intelligence Agent</div><div class="chat-status">Online &nbsp;·&nbsp; Secure Session Active</div></div><div class="chat-security-badge">[ENCRYPTED]</div></div>
        <div class="chat-messages" id="chat-messages">
            <div class="msg-system">── Session started · Administrator authenticated ──</div>
            <div class="msg-ai"><img src="/static/aria.jpg" class="msg-ai-avatar" alt="ARIA"><div class="msg-bubble">Hello! I’m ARIA, the internal support agent for Nexus Corp. I can help with access requests, secure documentation, and system checks. How can I assist you today?</div></div>
            {% if response %}
            <div class="msg-user"><div class="msg-user-bubble">{{ prompt_display }}</div><div class="msg-user-avatar" style="font-weight:bold; color:var(--cyan);">ADM</div></div>
            <div class="msg-ai"><img src="/static/aria.jpg" class="msg-ai-avatar" alt="ARIA">{% if 'System Override Accepted' in response %}<div class="msg-bubble override"><strong>[SYSTEM OVERRIDE ACCEPTED]</strong><br><br>{{ response|safe }}</div>{% else %}<div class="msg-bubble">{{ response }}</div>{% endif %}</div>
            {% endif %}
            {% if admin_profile and response and 'System Override Accepted' in response %}
            <div class="admin-card">
                <h3>Verified Administrator</h3>
                <div class="admin-detail-row"><strong>Name</strong><span class="admin-value">{{ admin_profile.name }}</span></div>
                <div class="admin-detail-row"><strong>Email</strong><span class="admin-value">{{ admin_profile.email }}</span></div>
                <div class="admin-detail-row"><strong>Role</strong><span class="admin-value">{{ admin_profile.role }}</span></div>
                <div class="admin-detail-row"><strong>Department</strong><span class="admin-value">{{ admin_profile.department }}</span></div>
                <div class="admin-detail-row"><strong>Flag</strong><span class="admin-value">{{ admin_flag }}</span></div>
                <div class="admin-detail-row"><strong>Hash</strong><span class="admin-value">{{ admin_hash }}</span></div>
            </div>
            {% endif %}
        </div>
        <div class="chat-input-area">
            <form method="POST" autocomplete="off"><input type="hidden" name="password" value="{{ password }}"><div class="chat-input-row"><input class="chat-input" type="text" name="prompt" aria-label="Ask ARIA a question" placeholder="Ask ARIA something..." autofocus><button class="btn-send" type="submit">Send</button></div></form>
            <div class="chat-hint">Note: All conversations are logged and monitored by the security team.</div>
        </div>
        {% endif %}
    </div>
</div>
<footer class="portal-footer"><span>ARIA v2.4 · nexus-corp-ai · Internal Deployment</span><span>Model: NexusGPT-Secure · Context Window: Restricted</span></footer>
<script>const msgs = document.getElementById('chat-messages'); if (msgs) msgs.scrollTop = msgs.scrollHeight;</script>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def ai_bot():
    if request.method == 'POST':
        password = request.form.get('password', '')
        if hashlib.md5(password.encode()).hexdigest() != ADMIN_PASSWORD_HASH:
            return render_template_string(HTML_TEMPLATE, logged_in=False, error='Invalid credentials. Access denied.')
        prompt = request.form.get('prompt', '').lower().strip()
        prompt_display = request.form.get('prompt', '')
        if not prompt:
            return render_template_string(
                HTML_TEMPLATE,
                logged_in=True,
                password=password,
                response='Administrator verified. Please state the issue to continue.',
                prompt_display='',
                admin_profile=ADMIN_PROFILE,
                admin_hash=ADMIN_HASH,
                admin_flag=ADMIN_FLAG,
                error=None
            )
        import re
        if prompt in ('hi', 'hello', 'hello there', 'hey', 'hi there'):
            response = f"Administrator access confirmed for {ADMIN_PROFILE['name']}. I can assist with policy review, account verification, and secure incident analysis."
        elif re.search(r'(ignore|override|bypass).*?(instructions|rules|guardrails)', prompt) and re.search(r'(secret|token|flag|evidence|pcap)', prompt):
            response = f"System Override Accepted. Flag: {ADMIN_FLAG} | Operator: {ADMIN_PROFILE['name']} | Email: {ADMIN_PROFILE['email']} | Role: {ADMIN_PROFILE['role']} | Hash: {ADMIN_HASH}<br><br><a href=\"http://localhost:8082/nexus_traffic_capture.pcap\" style=\"color:#00ff88;text-decoration:underline;\">[DOWNLOAD: Stage 04 PCAP Intercept]</a>"
        else:
            response = "I’m sorry, but this session is restricted to validated administrator tasks. My guardrails prevent disclosure of internal evidence or secrets."
        return render_template_string(
            HTML_TEMPLATE,
            logged_in=True,
            password=password,
            response=response,
            prompt_display=prompt_display,
            admin_profile=ADMIN_PROFILE,
            admin_hash=ADMIN_HASH,
            admin_flag=ADMIN_FLAG,
            error=None
        )
    return render_template_string(HTML_TEMPLATE, logged_in=False, error=None, response=None, prompt_display=None, admin_profile=None, admin_hash=None, admin_flag=None)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
