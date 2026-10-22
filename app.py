import json, os, secrets
from pathlib import Path
from flask import Flask, abort, redirect, render_template_string, request, session, url_for, jsonify
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "site_data.json"
app = Flask(__name__, static_folder=str(BASE_DIR), static_url_path="")
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax", SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "0") == "1")
DEFAULT_DATA = {"contact":"https://t.me/mohammad52766", "projects":[{"title":"بازی جنگی تفننی","description":"اگر بازی جنگی تفننی می‌خواهی، این برای توئه!","url":"https://t.me/mohammad123alizadeh_bot"},{"title":"ربات قیمت دلار","description":"ربات تلگرامی قیمت دلار","url":"https://t.me/mohammad12543778alizadeh_bot"}]}
def load_data():
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("projects"), list): return data
    except (OSError, ValueError): pass
    return DEFAULT_DATA
def save_data(data): DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
LOGIN = '''<!doctype html><html lang="fa" dir="rtl"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ورود مدیر</title><style>body{margin:0;background:#071225;color:#eef6ff;font-family:Tahoma;display:grid;place-items:center;min-height:100vh}.box{width:min(410px,88vw);padding:28px;border:1px solid #164a79;border-radius:18px;background:#0a1b33;box-sizing:border-box}p{color:#aac4e2}input,button{width:100%;box-sizing:border-box;padding:13px;border-radius:9px;margin-top:12px;font:inherit}input{background:#061020;color:white;border:1px solid #24527c}button{border:0;background:#00d8ef;color:#031225;font-weight:bold}.error{color:#ff9ba9}</style><div class="box"><h1>ورود به پنل مدیریت</h1><p>رمز مدیر را وارد کن.</p>{% if error %}<p class="error">{{ error }}</p>{% endif %}<form method="post"><input name="password" type="password" placeholder="رمز عبور مدیر" required autofocus><button>ورود</button></form></div></html>'''
PANEL = '''<!doctype html><html lang="fa" dir="rtl"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>پنل مدیریت</title><style>body{margin:0;background:#061020;color:#eff7ff;font-family:Tahoma;line-height:1.8}.wrap{max-width:900px;margin:30px auto;padding:18px}.top,.card{background:#0a1b33;border:1px solid #17436c;border-radius:15px;padding:20px;margin-bottom:18px}label{display:block;margin:12px 0 5px}input,textarea{width:100%;box-sizing:border-box;background:#061020;color:white;border:1px solid #25547c;border-radius:8px;padding:11px;font:inherit}textarea{min-height:65px}button,.link{display:inline-block;border:0;border-radius:8px;background:#00d8ef;color:#031225;padding:10px 18px;font:inherit;font-weight:bold;text-decoration:none;margin-top:14px}.muted{color:#a9c3e0;font-size:13px}.success{color:#7fffc4}.grid{display:grid;grid-template-columns:1fr 1fr;gap:15px}@media(max-width:650px){.grid{grid-template-columns:1fr}.wrap{padding:12px}}</style><div class="wrap"><div class="top"><h1>پنل مدیریت سایت</h1><p class="muted">نام، توضیحات و لینک ربات‌ها را ویرایش کن.</p>{% if saved %}<p class="success">تغییرات ذخیره شد.</p>{% endif %}<a class="link" href="/">مشاهده سایت</a> <a class="link" href="/admin/logout">خروج</a></div><form method="post"><div class="card"><h2>راه ارتباطی</h2><label>لینک تلگرام مدیر</label><input name="contact" value="{{ data.contact }}" required></div><div class="grid">{% for p in data.projects %}<div class="card"><h2>ربات {{ loop.index }}</h2><label>نام</label><input name="title_{{ loop.index0 }}" value="{{ p.title }}" required><label>توضیحات</label><textarea name="description_{{ loop.index0 }}">{{ p.description }}</textarea><label>لینک ربات</label><input name="url_{{ loop.index0 }}" value="{{ p.url }}" required></div>{% endfor %}</div><button type="submit">ذخیره تغییرات</button></form></div></html>'''
@app.get("/")
def home(): return app.send_static_file("index.html")
@app.get("/api/site")
def api_site(): return jsonify(load_data())
@app.route("/admin", methods=["GET", "POST"])
def admin():
    password = os.environ.get("ADMIN_PASSWORD")
    if not password: return "برای فعال‌سازی پنل، متغیر محیطی ADMIN_PASSWORD را روی سرور تنظیم کن.", 503
    if not session.get("admin_ok"):
        error = None
        if request.method == "POST":
            if secrets.compare_digest(request.form.get("password", ""), password): session["admin_ok"] = True; return redirect(url_for("admin"))
            error = "رمز عبور نادرست است."
        return render_template_string(LOGIN, error=error), 401 if error else 200
    data, saved = load_data(), False
    if request.method == "POST":
        contact = request.form.get("contact", "").strip()
        if not contact.startswith("https://t.me/"): abort(400, "لینک تماس باید https://t.me/ باشد")
        data["contact"] = contact
        for i, p in enumerate(data["projects"]):
            p["title"] = request.form.get(f"title_{i}", p["title"]).strip()[:100]
            p["description"] = request.form.get(f"description_{i}", p["description"]).strip()[:500]
            url = request.form.get(f"url_{i}", p["url"]).strip()
            if not url.startswith("https://t.me/"): abort(400, "لینک ربات باید https://t.me/ باشد")
            p["url"] = url
        save_data(data); saved = True
    return render_template_string(PANEL, data=data, saved=saved)
@app.get("/admin/logout")
def logout(): session.clear(); return redirect(url_for("admin"))
if __name__ == "__main__": app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "3000")), debug=False)
