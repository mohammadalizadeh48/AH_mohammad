import base64, io, json, os, secrets, sqlite3, uuid
from pathlib import Path
from datetime import datetime, timezone
from flask import Flask, abort, redirect, render_template_string, request, session, url_for, jsonify, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "site_data.json"
DB_FILE = Path(os.environ.get("DATA_DB_PATH", str(BASE_DIR / "mohammad_studio.sqlite3")))
app = Flask(__name__, static_folder=str(BASE_DIR), static_url_path="")
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax", SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "0") == "1", MAX_CONTENT_LENGTH=25*1024*1024)
UPLOAD_DIR = Path(os.environ.get("MEDIA_UPLOAD_DIR", str(BASE_DIR / "uploads"))).resolve()
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
QR_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}
QR_MEDIA_EXTENSIONS = QR_IMAGE_EXTENSIONS | {".mp4", ".webm", ".mov", ".m4v"}

def make_qr_data(value):
    import qrcode
    from qrcode.constants import ERROR_CORRECT_M
    image = qrcode.make(value, error_correction=ERROR_CORRECT_M, box_size=8, border=4)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")
DEFAULT_DATA = {"contact":"https://t.me/mohammad52766","projects":[],"portfolio":[]}

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
    return jsonify(bots=len(d.get("projects",[])),projects=len(d.get("portfolio",[])),users=None,visits=visits,services=None,suggestions=suggestions,messages=messages)

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


@app.post("/api/qr/generate")
def qr_generate():
    body = request.get_json(silent=True) or {}
    value = str(body.get("text", "")).strip()
    if not value:
        return jsonify(error="متن یا لینک را وارد کن."), 400
    if len(value.encode("utf-8")) > 2800:
        return jsonify(error="متن برای ساخت QR بیش از حد طولانی است."), 400
    try:
        return jsonify(qr=make_qr_data(value), content=value)
    except Exception:
        app.logger.exception("QR generation failed")
        return jsonify(error="ساخت QR انجام نشد؛ متن کوتاه‌تری امتحان کن."), 500

@app.post("/api/qr/upload")
def qr_upload():
    uploaded = request.files.get("file")
    if not uploaded or not uploaded.filename:
        return jsonify(error="ابتدا یک عکس یا ویدیو انتخاب کن."), 400
    extension = Path(uploaded.filename).suffix.lower()
    if extension not in QR_MEDIA_EXTENSIONS:
        return jsonify(error="فرمت فایل پشتیبانی نمی‌شود. عکس PNG/JPG/WEBP/GIF یا ویدیوی MP4/WEBM/MOV انتخاب کن."), 400
    filename = uuid.uuid4().hex + extension
    destination = UPLOAD_DIR / filename
    uploaded.save(destination)
    public_url = request.url_root.rstrip("/") + url_for("uploaded_media", filename=filename)
    try:
        qr = make_qr_data(public_url)
    except Exception:
        destination.unlink(missing_ok=True)
        app.logger.exception("QR generation for uploaded media failed")
        return jsonify(error="فایل ذخیره شد اما ساخت QR ناموفق بود."), 500
    return jsonify(url=public_url, qr=qr, filename=filename)

@app.get("/media/<path:filename>")
def uploaded_media(filename):
    return send_from_directory(UPLOAD_DIR, filename, as_attachment=False, conditional=True)

@app.post("/api/qr/decode")
def qr_decode():
    uploaded = request.files.get("file")
    if not uploaded or not uploaded.filename:
        return jsonify(error="تصویر حاوی QR را انتخاب کن."), 400
    extension = Path(uploaded.filename).suffix.lower()
    if extension not in QR_IMAGE_EXTENSIONS:
        return jsonify(error="برای خواندن QR فقط فایل تصویری PNG/JPG/WEBP/BMP/GIF انتخاب کن."), 400
    try:
        import cv2
        import numpy as np
        raw = uploaded.read()
        if not raw:
            return jsonify(error="فایل تصویر خالی است."), 400
        image = cv2.imdecode(np.frombuffer(raw, dtype=np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            return jsonify(error="تصویر قابل خواندن نیست."), 400
        detector = cv2.QRCodeDetector()
        decoded = []
        multi = detector.detectAndDecodeMulti(image)
        if multi and multi[0]:
            decoded = [item for item in multi[1] if item]
        if not decoded:
            value, points, _ = detector.detectAndDecode(image)
            if value:
                decoded = [value]
        if not decoded:
            return jsonify(error="هیچ کد QR خوانایی در این تصویر پیدا نشد."), 422
        return jsonify(contents=decoded, content=decoded[0], count=len(decoded))
    except Exception:
        app.logger.exception("QR decoding failed")
        return jsonify(error="خواندن QR با خطا روبه‌رو شد."), 500

@app.errorhandler(413)
def request_entity_too_large(_error):
    return jsonify(error="حجم فایل بیشتر از حد مجاز ۲۵ مگابایت است."), 413

LOGIN='''<!doctype html><html lang="fa" dir="rtl"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ورود مدیر</title><style>body{background:#071225;color:white;font-family:Tahoma;display:grid;place-items:center;min-height:100vh}.box{padding:28px;background:#0a1b33;border:1px solid #164a79;border-radius:18px;width:min(400px,85vw)}input,button{box-sizing:border-box;width:100%;padding:13px;margin-top:12px;border-radius:9px}input{background:#061020;color:white;border:1px solid #24527c}button{background:#00d8ef;font-weight:bold}</style><div class="box"><h1>ورود مدیر</h1>{% if error %}<p>{{error}}</p>{% endif %}<form method="post"><input name="password" type="password" placeholder="رمز مدیر" required><button>ورود</button></form></div></html>'''
PANEL='''<!doctype html><html lang="fa" dir="rtl"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>مدیریت محمد استودیو</title><style>body{background:#061020;color:white;font-family:Tahoma}.wrap{max-width:900px;margin:30px auto;padding:18px}.card{background:#0a1b33;border:1px solid #17436c;border-radius:15px;padding:20px;margin:15px 0}input,textarea{width:100%;box-sizing:border-box;background:#061020;color:white;border:1px solid #25547c;border-radius:8px;padding:11px;margin:8px 0}button,a{display:inline-block;background:#00d8ef;color:#031225;padding:10px 18px;border-radius:8px;text-decoration:none;border:0;margin:8px 0}</style><div class="wrap"><h1>پنل مدیریت محمد استودیو</h1><a href="/">مشاهده سایت</a><a href="/admin/logout">خروج</a>{% if saved %}<p>ذخیره شد.</p>{% endif %}<form method="post"><div class="card"><h2>ارتباط</h2><input name="contact" value="{{data.contact}}"></div>{% for p in data.projects %}<div class="card"><h2>ربات {{loop.index}}</h2><input name="title_{{loop.index0}}" value="{{p.title}}"><textarea name="description_{{loop.index0}}">{{p.description}}</textarea><input name="url_{{loop.index0}}" value="{{p.url}}"><label><input type="checkbox" name="delete_{{loop.index0}}" value="1" style="width:auto"> حذف</label></div>{% endfor %}<div class="card"><h2>ربات جدید</h2><input name="new_title" placeholder="نام"><textarea name="new_description" placeholder="توضیحات"></textarea><input name="new_url" placeholder="https://t.me/..."></div>{% for p in data.get("portfolio",[]) %}<div class="card"><h2>پروژه سایت {{loop.index}}</h2><input name="portfolio_title_{{loop.index0}}" value="{{p.title}}" placeholder="عنوان پروژه"><textarea name="portfolio_description_{{loop.index0}}" placeholder="توضیحات">{{p.description}}</textarea><input name="portfolio_category_{{loop.index0}}" value="{{p.category}}" placeholder="دسته‌بندی؛ مثلاً پروژه وب"><input name="portfolio_url_{{loop.index0}}" value="{{p.url}}" placeholder="لینک پروژه (اختیاری)"><input name="portfolio_image_{{loop.index0}}" value="{{p.image}}" placeholder="آدرس تصویر (اختیاری)"><label><input type="checkbox" name="portfolio_delete_{{loop.index0}}" value="1" style="width:auto"> حذف پروژه</label></div>{% endfor %}<div class="card"><h2>افزودن پروژه جدید</h2><input name="portfolio_new_title" placeholder="عنوان پروژه"><textarea name="portfolio_new_description" placeholder="توضیحات پروژه"></textarea><input name="portfolio_new_category" placeholder="دسته‌بندی"><input name="portfolio_new_url" placeholder="لینک پروژه (اختیاری)"><input name="portfolio_new_image" placeholder="آدرس تصویر (اختیاری)"></div><button>ذخیره تغییرات</button></form></div>'''

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
        data["projects"]=updated
        portfolio=[]
        for i,p in enumerate(data.get("portfolio",[])):
            if request.form.get(f"portfolio_delete_{i}")=="1": continue
            title=request.form.get(f"portfolio_title_{i}","").strip()[:100]
            desc=request.form.get(f"portfolio_description_{i}","").strip()[:1000]
            category=request.form.get(f"portfolio_category_{i}","").strip()[:60] or "پروژه"
            url=request.form.get(f"portfolio_url_{i}","").strip()[:500]
            image=request.form.get(f"portfolio_image_{i}","").strip()[:500]
            if not title: abort(400)
            if url and not url.startswith(("https://","http://")): abort(400)
            if image and not (image.startswith(("https://","http://","/"))): abort(400)
            portfolio.append({"title":title,"description":desc,"category":category,"url":url,"image":image})
        nt=request.form.get("portfolio_new_title","").strip()[:100]
        nd=request.form.get("portfolio_new_description","").strip()[:1000]
        nc=request.form.get("portfolio_new_category","").strip()[:60] or "پروژه"
        nu=request.form.get("portfolio_new_url","").strip()[:500]
        ni=request.form.get("portfolio_new_image","").strip()[:500]
        if nt or nd or nu or ni:
            if not nt: abort(400)
            if nu and not nu.startswith(("https://","http://")): abort(400)
            if ni and not (ni.startswith(("https://","http://","/"))): abort(400)
            portfolio.append({"title":nt,"description":nd,"category":nc,"url":nu,"image":ni})
        data["portfolio"]=portfolio
        DATA_FILE.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8"); saved=True
    return render_template_string(PANEL,data=data,saved=saved)
@app.get("/admin/logout")
def logout(): session.clear(); return redirect(url_for("admin"))
if __name__=="__main__": app.run(host="0.0.0.0",port=int(os.environ.get("PORT","3000")),debug=False)
