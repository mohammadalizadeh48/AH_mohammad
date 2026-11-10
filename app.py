import json, os, secrets, sqlite3
from pathlib import Path
from datetime import datetime, timezone
from flask import Flask, abort, redirect, render_template_string, request, session, url_for, jsonify

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "site_data.json"
DB_FILE = Path(os.environ.get("DATA_DB_PATH", str(BASE_DIR / "mohammad_studio.sqlite3")))
app = Flask(__name__, static_folder=str(BASE_DIR), static_url_path="")
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax", SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "0") == "1", MAX_CONTENT_LENGTH=1024*1024)
DEFAULT_DATA = {"contact":"https://t.me/mohammad52766","projects":[]}

def load_data():
    try:
        d=json.loads(DATA_FILE.read_text(encoding="utf-8"))
        if isinstance(d,dict) and isinstance(d.get("projects"),list): return d
    except (OSError,ValueError): pass
    return DEFAULT_DATA

def db():
    c=sqlite3.connect(DB_FILE); c.row_factory=sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    c.executescript("""
    CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,kind TEXT NOT NULL,message TEXT NOT NULL,created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS suggestions(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,description TEXT NOT NULL,created_at TEXT NOT NULL,votes INTEGER NOT NULL DEFAULT 0);
    CREATE TABLE IF NOT EXISTS votes(suggestion_id INTEGER NOT NULL,visitor TEXT NOT NULL,PRIMARY KEY(suggestion_id,visitor));
    CREATE TABLE IF NOT EXISTS visits(day TEXT PRIMARY KEY,count INTEGER NOT NULL DEFAULT 0);
    CREATE TABLE IF NOT EXISTS shortlinks(code TEXT PRIMARY KEY,target TEXT NOT NULL,created_at TEXT NOT NULL);
    """)
    return c

def stamp(): return datetime.now(timezone.utc).isoformat()
def visitor():
    if not session.get("visitor_id"): session["visitor_id"]=secrets.token_urlsafe(20)
    return session["visitor_id"]

@app.before_request
def track():
    if request.endpoint=="home" and request.method=="GET":
        with db() as c:
            day=datetime.now(timezone.utc).date().isoformat()
            c.execute("INSERT INTO visits(day,count) VALUES(?,1) ON CONFLICT(day) DO UPDATE SET count=count+1",(day,))

@app.get("/")
def home(): return app.send_static_file("index.html")
@app.get("/api/site")
def site(): return jsonify(load_data())

@app.get("/api/stats")
def stats():
    d=load_data()
    with db() as c:
        visits=c.execute("SELECT COALESCE(SUM(count),0) n FROM visits").fetchone()["n"]
        suggestions=c.execute("SELECT COUNT(*) n FROM suggestions").fetchone()["n"]
        messages=c.execute("SELECT COUNT(*) n FROM messages").fetchone()["n"]
    return jsonify(bots=len(d.get("projects",[])),projects=None,users=None,visits=visits,services=None,suggestions=suggestions,messages=messages)

@app.get("/api/status")
def status():
    # Public Telegram bot links do not expose a trustworthy health-check endpoint.
    return jsonify([{"name":p.get("title","ربات"),"status":"unknown","label":"وضعیت نامشخص"} for p in load_data().get("projects",[])])

@app.post("/api/contact")
def contact():
    b=request.get_json(silent=True) or request.form
    name=str(b.get("name","")).strip()[:80]; kind=str(b.get("kind","پیام")).strip()[:40]; msg=str(b.get("message","")).strip()[:3000]
    if len(name)<2 or len(msg)<3: return jsonify(error="نام و متن پیام را کامل وارد کن."),400
    with db() as c: c.execute("INSERT INTO messages(name,kind,message,created_at) VALUES(?,?,?,?)",(name,kind,msg,stamp()))
    return jsonify(ok=True,message="پیام با موفقیت ذخیره شد.")

@app.route("/api/suggestions",methods=["GET","POST"])
def suggestions():
    if request.method=="POST":
        b=request.get_json(silent=True) or request.form
        title=str(b.get("title","")).strip()[:100]; desc=str(b.get("description","")).strip()[:1000]
        if len(title)<3: return jsonify(error="عنوان پیشنهاد باید حداقل ۳ نویسه باشد."),400
        with db() as c: c.execute("INSERT INTO suggestions(title,description,created_at) VALUES(?,?,?)",(title,desc,stamp()))
        return jsonify(ok=True,message="پیشنهاد ثبت شد.")
    with db() as c: rows=c.execute("SELECT id,title,description,created_at,votes FROM suggestions ORDER BY votes DESC,id DESC LIMIT 100").fetchall()
    return jsonify([dict(x) for x in rows])

@app.post("/api/suggestions/<int:item_id>/vote")
def vote(item_id):
    with db() as c:
        if not c.execute("SELECT 1 FROM suggestions WHERE id=?",(item_id,)).fetchone(): return jsonify(error="پیشنهاد پیدا نشد."),404
        try: c.execute("INSERT INTO votes(suggestion_id,visitor) VALUES(?,?)",(item_id,visitor()))
        except sqlite3.IntegrityError: return jsonify(error="قبلاً به این پیشنهاد رأی داده‌ای."),409
        c.execute("UPDATE suggestions SET votes=votes+1 WHERE id=?",(item_id,))
    return jsonify(ok=True)

@app.post("/api/shorten")
def shorten():
    b=request.get_json(silent=True) or {}; target=str(b.get("url","")).strip()
    if not (target.startswith("https://") or target.startswith("http://")): return jsonify(error="لینک معتبر با http یا https وارد کن."),400
    code=secrets.token_urlsafe(6).replace("-","").replace("_","")[:8]
    with db() as c: c.execute("INSERT INTO shortlinks(code,target,created_at) VALUES(?,?,?)",(code,target,stamp()))
    return jsonify(url=request.host_url.rstrip("/")+"/s/"+code)
@app.get("/s/<code>")
def shortlink(code):
    with db() as c: row=c.execute("SELECT target FROM shortlinks WHERE code=?",(code,)).fetchone()
    if not row: abort(404)
    return redirect(row["target"],code=302)

LOGIN='''<!doctype html><html lang="fa" dir="rtl"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ورود مدیر</title><style>body{background:#071225;color:white;font-family:Tahoma;display:grid;place-items:center;min-height:100vh}.box{padding:28px;background:#0a1b33;border:1px solid #164a79;border-radius:18px;width:min(400px,85vw)}input,button{box-sizing:border-box;width:100%;padding:13px;margin-top:12px;border-radius:9px}input{background:#061020;color:white;border:1px solid #24527c}button{background:#00d8ef;font-weight:bold}</style><div class="box"><h1>ورود مدیر</h1>{% if error %}<p>{{error}}</p>{% endif %}<form method="post"><input name="password" type="password" placeholder="رمز مدیر" required><button>ورود</button></form></div></html>'''
PANEL='''<!doctype html><html lang="fa" dir="rtl"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>مدیریت محمد استودیو</title><style>body{background:#061020;color:white;font-family:Tahoma}.wrap{max-width:900px;margin:30px auto;padding:18px}.card{background:#0a1b33;border:1px solid #17436c;border-radius:15px;padding:20px;margin:15px 0}input,textarea{width:100%;box-sizing:border-box;background:#061020;color:white;border:1px solid #25547c;border-radius:8px;padding:11px;margin:8px 0}button,a{display:inline-block;background:#00d8ef;color:#031225;padding:10px 18px;border-radius:8px;text-decoration:none;border:0;margin:8px 0}</style><div class="wrap"><h1>پنل مدیریت محمد استودیو</h1><a href="/">مشاهده سایت</a><a href="/admin/logout">خروج</a>{% if saved %}<p>ذخیره شد.</p>{% endif %}<form method="post"><div class="card"><h2>ارتباط</h2><input name="contact" value="{{data.contact}}"></div>{% for p in data.projects %}<div class="card"><h2>ربات {{loop.index}}</h2><input name="title_{{loop.index0}}" value="{{p.title}}"><textarea name="description_{{loop.index0}}">{{p.description}}</textarea><input name="url_{{loop.index0}}" value="{{p.url}}"><label><input type="checkbox" name="delete_{{loop.index0}}" value="1" style="width:auto"> حذف</label></div>{% endfor %}<div class="card"><h2>ربات جدید</h2><input name="new_title" placeholder="نام"><textarea name="new_description" placeholder="توضیحات"></textarea><input name="new_url" placeholder="https://t.me/..."></div><button>ذخیره تغییرات</button></form></div>'''

@app.route("/admin",methods=["GET","POST"])
def admin():
    password=os.environ.get("ADMIN_PASSWORD")
    if not password: return "برای فعال‌سازی پنل، متغیر محیطی ADMIN_PASSWORD را در Runflare تنظیم کن.",503
    if not session.get("admin_ok"):
        error=None
        if request.method=="POST":
            if secrets.compare_digest(request.form.get("password",""),password): session["admin_ok"]=True; return redirect(url_for("admin"))
            error="رمز عبور نادرست است."
        return render_template_string(LOGIN,error=error),401 if error else 200
    data,saved=load_data(),False
    if request.method=="POST":
        contact_url=request.form.get("contact","").strip()
        if not contact_url.startswith("https://t.me/"): abort(400)
        data["contact"]=contact_url; updated=[]
        for i,p in enumerate(data["projects"]):
            if request.form.get(f"delete_{i}")=="1": continue
            title=request.form.get(f"title_{i}",p["title"]).strip()[:100]; desc=request.form.get(f"description_{i}",p.get("description","")).strip()[:500]; url=request.form.get(f"url_{i}",p["url"]).strip()
            if not title or not url.startswith("https://t.me/"): abort(400)
            updated.append({"title":title,"description":desc,"url":url})
        nt=request.form.get("new_title","").strip()[:100]; nd=request.form.get("new_description","").strip()[:500]; nu=request.form.get("new_url","").strip()
        if nt or nu:
            if not nt or not nu.startswith("https://t.me/"): abort(400)
            updated.append({"title":nt,"description":nd,"url":nu})
        data["projects"]=updated; DATA_FILE.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8"); saved=True
    return render_template_string(PANEL,data=data,saved=saved)
@app.get("/admin/logout")
def logout(): session.clear(); return redirect(url_for("admin"))
if __name__=="__main__": app.run(host="0.0.0.0",port=int(os.environ.get("PORT","3000")),debug=False)
