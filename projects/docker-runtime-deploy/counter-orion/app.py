from datetime import datetime, timedelta, timezone
from functools import wraps
import os

import jwt
from flask import Flask, Response, g, jsonify, request, send_file
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

APP_NAME = os.getenv("APP_NAME", "counter-orion")
APP_VERSION = os.getenv("APP_VERSION", "dev")
JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
JWT_ACCESS_TTL_MIN = int(os.getenv("JWT_ACCESS_TTL_MIN", "30"))
JWT_REFRESH_TTL_DAYS = int(os.getenv("JWT_REFRESH_TTL_DAYS", "7"))

raw_db_url = os.getenv("DATABASE_URL", "sqlite:////tmp/counter_orion.db")
if raw_db_url.startswith("postgresql://"):
    raw_db_url = raw_db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = raw_db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class SkinCatalog(db.Model):
    __tablename__ = "skins_catalog"

    id = db.Column(db.Integer, primary_key=True)
    game = db.Column(db.String(32), nullable=False, default="cs2")
    weapon = db.Column(db.String(64), nullable=False)
    skin_name = db.Column(db.String(128), nullable=False)
    rarity = db.Column(db.String(32), nullable=False)
    collection = db.Column(db.String(128), nullable=True)
    image_url = db.Column(db.String(512), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)


class UserSkin(db.Model):
    __tablename__ = "user_skins"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    catalog_skin_id = db.Column(db.Integer, db.ForeignKey("skins_catalog.id", ondelete="RESTRICT"), nullable=False, index=True)
    wear = db.Column(db.String(32), nullable=True)
    stattrak = db.Column(db.Boolean, nullable=False, default=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    note = db.Column(db.String(500), nullable=True)
    buy_price_eur = db.Column(db.Numeric(10, 2), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = db.relationship("User", backref=db.backref("skins", lazy=True, cascade="all, delete-orphan"))
    catalog_skin = db.relationship("SkinCatalog", backref=db.backref("owned_entries", lazy=True))


def _create_token(user: User, token_type: str) -> str:
    now = datetime.now(timezone.utc)
    ttl = timedelta(minutes=JWT_ACCESS_TTL_MIN) if token_type == "access" else timedelta(days=JWT_REFRESH_TTL_DAYS)
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "username": user.username,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + ttl).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def _decode_token(token: str, expected_type: str):
    payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    if payload.get("type") != expected_type:
        raise jwt.InvalidTokenError("invalid token type")
    return payload


def _catalog_to_dict(item: SkinCatalog) -> dict:
    return {
        "id": item.id,
        "weapon": item.weapon,
        "skin_name": item.skin_name,
        "rarity": item.rarity,
    }


def _user_skin_to_dict(item: UserSkin) -> dict:
    return {
        "id": item.id,
        "user_id": item.user_id,
        "catalog_skin_id": item.catalog_skin_id,
        "weapon": item.catalog_skin.weapon if item.catalog_skin else None,
        "skin_name": item.catalog_skin.skin_name if item.catalog_skin else None,
        "rarity": item.catalog_skin.rarity if item.catalog_skin else None,
        "wear": item.wear,
        "stattrak": item.stattrak,
        "quantity": item.quantity,
        "note": item.note,
        "buy_price_eur": float(item.buy_price_eur) if item.buy_price_eur is not None else None,
        "created_at": item.created_at.isoformat() if item.created_at else None,
        "updated_at": item.updated_at.isoformat() if item.updated_at else None,
    }


def auth_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "missing bearer token"}), 401

        token = auth_header.split(" ", 1)[1].strip()
        try:
            payload = _decode_token(token, "access")
            user = User.query.get(int(payload["sub"]))
            if not user:
                return jsonify({"error": "user not found"}), 401
            g.current_user = user
        except Exception:
            return jsonify({"error": "invalid or expired token"}), 401

        return fn(*args, **kwargs)

    return wrapper


@app.get("/")
def root():
    html = """
<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>__APP_NAME__</title>
  <style>
    body { font-family: Arial, sans-serif; background:#0f172a url('/assets/bg-awp-dragon-lore.jpg') center/cover fixed no-repeat; color:#e2e8f0; margin:0; }
    .wrap { max-width: 760px; margin: 8vh auto; padding: 24px; background:#1e293b; border-radius:12px; border:1px solid #334155; }
    .row { margin-top: 12px; }
    button { margin-top: 14px; margin-right: 8px; padding: 8px 14px; border:0; border-radius:8px; background:#38bdf8; color:#082f49; font-weight:700; cursor:pointer; }
    input { margin: 4px 0; width: 100%; padding: 8px; border-radius: 8px; border: 1px solid #334155; background: #0f172a; color: #e2e8f0; }
    .grid { display:grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    pre { background:#0f172a; border:1px solid #334155; border-radius:8px; padding:10px; overflow:auto; }
  </style>
</head>
<body>
  <main class=\"wrap\">
    <h1>Counter-Orion</h1>
    <p id=\"msg\">Loading...</p>
    <div class=\"row\">Service: <strong>__APP_NAME__</strong></div>
    <div class=\"row\">Version: <strong id=\"version\">__APP_VERSION__</strong></div>
    <div class=\"row\">Health: <strong id=\"health\">checking...</strong></div>

    <h2>Login / Register</h2>
    <div class=\"grid\">
      <section>
        <h3>Register</h3>
        <input id=\"reg_email\" placeholder=\"email\" />
        <input id=\"reg_username\" placeholder=\"username\" />
        <input id=\"reg_password\" type=\"password\" placeholder=\"password\" />
        <button id=\"registerBtn\">Register</button>
      </section>
      <section>
        <h3>Login</h3>
        <input id=\"login_email\" placeholder=\"email\" />
        <input id=\"login_password\" type=\"password\" placeholder=\"password\" />
        <button id=\"loginBtn\">Login</button>
      </section>
    </div>

    <button id=\"profileBtn\">Go to /profile</button>
    <button id=\"inventoryBtn\">Go to /inventory</button>
    <button id=\"meBtn\">Call /me</button>
    <pre id=\"output\">ready</pre>
  </main>
  <script>
    const output = document.getElementById('output');
    const setOutput = (value) => output.textContent = JSON.stringify(value, null, 2);

    async function refreshMeta() {
      const [healthRes, versionRes, msgRes] = await Promise.all([
        fetch('/health'),
        fetch('/version'),
        fetch('/api/message')
      ]);
      const health = await healthRes.json();
      const version = await versionRes.json();
      const msg = await msgRes.json();
      document.getElementById('health').textContent = health.status;
      document.getElementById('version').textContent = version.version;
      document.getElementById('msg').textContent = msg.message;
    }

    document.getElementById('registerBtn').addEventListener('click', async () => {
      const payload = {
        email: document.getElementById('reg_email').value,
        username: document.getElementById('reg_username').value,
        password: document.getElementById('reg_password').value,
      };
      const res = await fetch('/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      setOutput(await res.json());
    });

    document.getElementById('loginBtn').addEventListener('click', async () => {
      const payload = {
        email: document.getElementById('login_email').value,
        password: document.getElementById('login_password').value,
      };
      const res = await fetch('/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.access_token) {
        localStorage.setItem('counter_orion_access_token', data.access_token);
        localStorage.setItem('counter_orion_refresh_token', data.refresh_token || '');
        window.location.href = '/profile';
        return;
      }
      setOutput(data);
    });

    document.getElementById('profileBtn').addEventListener('click', () => {
      window.location.href = '/profile';
    });

    document.getElementById('inventoryBtn').addEventListener('click', () => {
      window.location.href = '/inventory';
    });

    document.getElementById('meBtn').addEventListener('click', async () => {
      const accessToken = localStorage.getItem('counter_orion_access_token');
      const res = await fetch('/me', {
        headers: accessToken ? { 'Authorization': `Bearer ${accessToken}` } : {}
      });
      setOutput(await res.json());
    });

    refreshMeta();
  </script>
</body>
</html>
"""
    html = html.replace("__APP_NAME__", APP_NAME).replace("__APP_VERSION__", APP_VERSION)
    return Response(html, mimetype="text/html")


@app.get("/profile")
def profile_page():
    html = """
<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>__APP_NAME__ / profile</title>
  <style>
    body { font-family: Arial, sans-serif; background:#0f172a url('/assets/bg-awp-dragon-lore.jpg') center/cover fixed no-repeat; color:#e2e8f0; margin:0; }
    .wrap { max-width: 920px; margin: 6vh auto; padding: 24px; background:#1e293b; border-radius:12px; border:1px solid #334155; }
    button { margin-top: 14px; margin-right: 8px; padding: 8px 14px; border:0; border-radius:8px; background:#38bdf8; color:#082f49; font-weight:700; cursor:pointer; }
    pre { background:#0f172a; border:1px solid #334155; border-radius:8px; padding:10px; overflow:auto; }
    table { width:100%; border-collapse: collapse; margin-top: 12px; }
    th, td { border-bottom: 1px solid #334155; padding: 8px; text-align:left; font-size: 14px; }
  </style>
</head>
<body>
  <main class=\"wrap\">
    <h1>Counter-Orion / Profile</h1>
    <p>Authenticated profile page</p>
    <pre id=\"profile\">loading...</pre>

    <h3>My inventory snapshot</h3>
    <table>
      <thead><tr><th>ID</th><th>Weapon</th><th>Skin</th><th>Rarity</th><th>Qty</th><th>Wear</th></tr></thead>
      <tbody id=\"profileInvBody\"></tbody>
    </table>

    <button id=\"refreshBtn\">Refresh profile</button>
    <button id=\"inventoryBtn\">Go to /inventory</button>
    <button id=\"logoutBtn\">Logout</button>
    <button id=\"homeBtn\">Back to /</button>
  </main>
  <script>
    const tokenKey = 'counter_orion_access_token';
    const profileEl = document.getElementById('profile');
    const invBody = document.getElementById('profileInvBody');

    async function loadProfile() {
      const accessToken = localStorage.getItem(tokenKey);
      if (!accessToken) {
        window.location.href = '/';
        return;
      }

      const [meRes, invRes] = await Promise.all([
        fetch('/me', { headers: { 'Authorization': `Bearer ${accessToken}` } }),
        fetch('/skins', { headers: { 'Authorization': `Bearer ${accessToken}` } })
      ]);

      if (meRes.status === 401 || invRes.status === 401) {
        localStorage.removeItem(tokenKey);
        localStorage.removeItem('counter_orion_refresh_token');
        window.location.href = '/';
        return;
      }

      const me = await meRes.json();
      profileEl.textContent = JSON.stringify(me, null, 2);

      const inv = await invRes.json();
      invBody.innerHTML = '';
      for (const i of (inv.items || [])) {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${i.id}</td><td>${i.weapon || ''}</td><td>${i.skin_name || ''}</td><td>${i.rarity || ''}</td><td>${i.quantity}</td><td>${i.wear || ''}</td>`;
        invBody.appendChild(tr);
      }
    }

    document.getElementById('refreshBtn').addEventListener('click', loadProfile);
    document.getElementById('inventoryBtn').addEventListener('click', () => {
      window.location.href = '/inventory';
    });
    document.getElementById('logoutBtn').addEventListener('click', () => {
      localStorage.removeItem(tokenKey);
      localStorage.removeItem('counter_orion_refresh_token');
      window.location.href = '/';
    });
    document.getElementById('homeBtn').addEventListener('click', () => {
      window.location.href = '/';
    });

    loadProfile();
  </script>
</body>
</html>
"""
    html = html.replace("__APP_NAME__", APP_NAME)
    return Response(html, mimetype="text/html")


@app.get("/inventory")
def inventory_page():
    html = """
<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>__APP_NAME__ / inventory</title>
  <style>
    body { font-family: Arial, sans-serif; background:#0f172a url('/assets/bg-awp-dragon-lore.jpg') center/cover fixed no-repeat; color:#e2e8f0; margin:0; }
    .wrap { max-width: 980px; margin: 4vh auto; padding: 24px; background:#1e293b; border-radius:12px; border:1px solid #334155; }
    .grid { display:grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    input, select { margin: 4px 0; width: 100%; padding: 8px; border-radius: 8px; border: 1px solid #334155; background: #0f172a; color: #e2e8f0; }
    button { margin-top: 8px; margin-right: 8px; padding: 8px 14px; border:0; border-radius:8px; background:#38bdf8; color:#082f49; font-weight:700; cursor:pointer; }
    table { width:100%; border-collapse: collapse; margin-top: 12px; }
    th, td { border-bottom: 1px solid #334155; padding: 8px; text-align:left; font-size: 14px; }
    .muted { color:#94a3b8; font-size: 13px; }
  </style>
</head>
<body>
  <main class=\"wrap\">
    <h1>Counter-Orion / Inventory</h1>
    <div class=\"muted\">Task 5 UI: catalog search + add + inventory CRUD</div>

    <div class=\"grid\">
      <section>
        <h3>Catalog search</h3>
        <input id=\"q\" placeholder=\"Search (e.g. Printstream)\" />
        <select id=\"rarity\">
          <option value=\"\">Any rarity</option>
          <option value=\"Covert\">Covert</option>
          <option value=\"Extraordinary\">Extraordinary</option>
        </select>
        <select id=\"weapon\">
          <option value=\"\">Any weapon</option>
          <option>AK-47</option>
          <option>AUG</option>
          <option>AWP</option>
          <option>CZ75-Auto</option>
          <option>Desert Eagle</option>
          <option>FAMAS</option>
          <option>Five-SeveN</option>
          <option>Galil AR</option>
          <option>Glock-18</option>
          <option>M4A1-S</option>
          <option>M4A4</option>
          <option>MAC-10</option>
          <option>MP7</option>
          <option>MP9</option>
          <option>P2000</option>
          <option>P250</option>
          <option>P90</option>
          <option>PP-Bizon</option>
          <option>R8 Revolver</option>
          <option>Sawed-Off</option>
          <option>SCAR-20</option>
          <option>SSG 08</option>
          <option>USP-S</option>
        </select>
        <button id=\"searchBtn\">Search catalog</button>
        <table>
          <thead><tr><th>ID</th><th>Weapon</th><th>Skin</th><th>Rarity</th></tr></thead>
          <tbody id=\"catalogBody\"></tbody>
        </table>
      </section>

      <section>
        <h3>Add to my inventory</h3>
        <input id=\"skinNameSearch\" placeholder=\"Type skin name (autocomplete)\" />
        <div id=\"skinSuggestions\" class=\"muted\"></div>
        <input id=\"catalogSkinId\" placeholder=\"catalog_skin_id (auto-filled)\" readonly />
        <select id=\"wear\">
          <option value=\"\">Wear (optional)</option>
          <option>Factory New</option>
          <option>Minimal Wear</option>
          <option>Field-Tested</option>
          <option>Well-Worn</option>
          <option>Battle-Scarred</option>
        </select>
        <input id=\"quantity\" type=\"number\" min=\"1\" value=\"1\" placeholder=\"quantity\" />
        <input id=\"buyPrice\" type=\"number\" step=\"0.01\" min=\"0\" placeholder=\"buy_price_eur\" />
        <input id=\"note\" placeholder=\"note\" />
        <label><input id=\"stattrak\" type=\"checkbox\" style=\"width:auto;\" /> StatTrak</label>
        <br />
        <button id=\"addBtn\">Add item</button>
        <button id=\"reloadBtn\">Reload inventory</button>
      </section>
    </div>

    <h3>My inventory</h3>
    <table>
      <thead><tr><th>ID</th><th>Weapon</th><th>Skin</th><th>Qty</th><th>Wear</th><th>StatTrak</th><th>Note</th><th>Actions</th></tr></thead>
      <tbody id=\"invBody\"></tbody>
    </table>

    <button id=\"homeBtn\">Back to /</button>
    <pre id=\"output\" class=\"muted\"></pre>
  </main>

  <script>
    const tokenKey = 'counter_orion_access_token';
    const output = document.getElementById('output');
    const setOutput = (v) => output.textContent = JSON.stringify(v, null, 2);

    function authHeaders() {
      const t = localStorage.getItem(tokenKey);
      if (!t) return null;
      return { 'Authorization': `Bearer ${t}`, 'Content-Type': 'application/json' };
    }

    async function api(path, method='GET', body=null) {
      const headers = authHeaders();
      if (!headers) { window.location.href='/'; return null; }
      const res = await fetch(path, { method, headers, body: body ? JSON.stringify(body) : null });
      if (res.status === 401) { localStorage.removeItem(tokenKey); window.location.href='/'; return null; }
      const data = await res.json();
      return { ok: res.ok, data, status: res.status };
    }

    function renderCatalog(items) {
      const body = document.getElementById('catalogBody');
      body.innerHTML = '';
      for (const i of items) {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${i.id}</td><td>${i.weapon}</td><td>${i.skin_name}</td><td>${i.rarity}</td>`;
        tr.onclick = () => {
          document.getElementById('catalogSkinId').value = i.id;
          document.getElementById('skinNameSearch').value = `${i.weapon} | ${i.skin_name}`;
          document.getElementById('skinSuggestions').innerHTML = `Selected: #${i.id} ${i.weapon} | ${i.skin_name}`;
        };
        body.appendChild(tr);
      }
    }

    async function autocompleteSkins() {
      const q = document.getElementById('skinNameSearch').value.trim();
      const suggestions = document.getElementById('skinSuggestions');
      if (q.length < 2) {
        suggestions.textContent = 'Type at least 2 chars...';
        return;
      }
      const r = await api('/catalog/skins/search?q=' + encodeURIComponent(q) + '&limit=8');
      if (!r || !r.ok) return;
      const items = r.data.items || [];
      suggestions.innerHTML = '';
      for (const i of items) {
        const b = document.createElement('button');
        b.type = 'button';
        b.textContent = `#${i.id} ${i.weapon} | ${i.skin_name} (${i.rarity})`;
        b.style.marginTop = '4px';
        b.onclick = () => {
          document.getElementById('catalogSkinId').value = i.id;
          document.getElementById('skinNameSearch').value = `${i.weapon} | ${i.skin_name}`;
          suggestions.innerHTML = `Selected: #${i.id} ${i.weapon} | ${i.skin_name}`;
        };
        suggestions.appendChild(b);
      }
      if (!items.length) suggestions.textContent = 'No matches';
    }

    async function loadCatalog() {
      const q = document.getElementById('q').value.trim();
      const rarity = document.getElementById('rarity').value;
      const weapon = document.getElementById('weapon').value;
      const params = new URLSearchParams({ page: '1', page_size: '8' });
      if (q) params.set('q', q);
      if (rarity) params.set('rarity', rarity);
      if (weapon) params.set('weapon', weapon);
      const r = await api('/catalog/skins?' + params.toString());
      if (!r) return;
      if (!r.ok) return setOutput(r.data);
      renderCatalog(r.data.items || []);
      setOutput({ catalog_total: r.data.total, shown: (r.data.items || []).length });
    }

    function renderInventory(items) {
      const body = document.getElementById('invBody');
      body.innerHTML = '';
      for (const i of items) {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${i.id}</td>
          <td>${i.weapon || ''}</td>
          <td>${i.skin_name || ''}</td>
          <td>${i.quantity}</td>
          <td>${i.wear || ''}</td>
          <td>${i.stattrak ? 'yes' : 'no'}</td>
          <td>${i.note || ''}</td>
          <td>
            <button data-act=\"edit\" data-id=\"${i.id}\">Edit</button>
            <button data-act=\"del\" data-id=\"${i.id}\">Delete</button>
          </td>
        `;
        body.appendChild(tr);
      }

      body.querySelectorAll('button[data-act="del"]').forEach(btn => {
        btn.addEventListener('click', async () => {
          const id = btn.getAttribute('data-id');
          const r = await api('/skins/' + id, 'DELETE');
          if (!r) return;
          setOutput(r.data);
          loadInventory();
        });
      });

      body.querySelectorAll('button[data-act="edit"]').forEach(btn => {
        btn.addEventListener('click', async () => {
          const id = btn.getAttribute('data-id');
          const quantity = Number(prompt('New quantity (>=1):', '1'));
          if (!quantity || quantity < 1) return;
          const note = prompt('New note:', 'updated via UI');
          const r = await api('/skins/' + id, 'PUT', { quantity, note });
          if (!r) return;
          setOutput(r.data);
          loadInventory();
        });
      });
    }

    async function loadInventory() {
      const r = await api('/skins');
      if (!r) return;
      if (!r.ok) return setOutput(r.data);
      renderInventory(r.data.items || []);
      setOutput({ inventory_total: r.data.total });
    }

    document.getElementById('searchBtn').addEventListener('click', loadCatalog);
    document.getElementById('skinNameSearch').addEventListener('input', autocompleteSkins);
    document.getElementById('reloadBtn').addEventListener('click', loadInventory);
    document.getElementById('homeBtn').addEventListener('click', () => window.location.href='/');

    document.getElementById('addBtn').addEventListener('click', async () => {
      const payload = {
        catalog_skin_id: Number(document.getElementById('catalogSkinId').value),
        wear: document.getElementById('wear').value,
        quantity: Number(document.getElementById('quantity').value || 1),
        buy_price_eur: document.getElementById('buyPrice').value || null,
        note: document.getElementById('note').value,
        stattrak: document.getElementById('stattrak').checked,
      };
      const r = await api('/skins', 'POST', payload);
      if (!r) return;
      setOutput(r.data);
      if (r.ok) loadInventory();
    });

    loadCatalog();
    loadInventory();
  </script>
</body>
</html>
"""
    html = html.replace("__APP_NAME__", APP_NAME)
    return Response(html, mimetype="text/html")


@app.get("/assets/bg-awp-dragon-lore.jpg")
def bg_awp_dragon_lore():
    return send_file("data/bg-awp-dragon-lore.jpg", mimetype="image/jpeg")


@app.get("/health")
def health():
    return jsonify({"status": "healthy"})


@app.get("/version")
def version():
    return jsonify({"app": APP_NAME, "version": APP_VERSION})


@app.get("/api/message")
def message():
    return jsonify({"message": "Counter-Orion auth scaffold is live 🚀"})


@app.post("/auth/register")
def register():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not email or not username or len(password) < 6:
        return jsonify({"error": "email, username, password(>=6) are required"}), 400

    if User.query.filter((User.email == email) | (User.username == username)).first():
        return jsonify({"error": "email or username already exists"}), 409

    user = User(email=email, username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"id": user.id, "email": user.email, "username": user.username}), 201


@app.post("/auth/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "invalid credentials"}), 401

    return jsonify(
        {
            "access_token": _create_token(user, "access"),
            "refresh_token": _create_token(user, "refresh"),
            "token_type": "Bearer",
        }
    )


@app.post("/auth/refresh")
def refresh():
    data = request.get_json(silent=True) or {}
    refresh_token = data.get("refresh_token") or ""

    if not refresh_token:
        return jsonify({"error": "refresh_token is required"}), 400

    try:
        payload = _decode_token(refresh_token, "refresh")
        user = User.query.get(int(payload["sub"]))
        if not user:
            return jsonify({"error": "user not found"}), 401
    except Exception:
        return jsonify({"error": "invalid or expired refresh token"}), 401

    return jsonify({"access_token": _create_token(user, "access"), "token_type": "Bearer"})


@app.get("/me")
@auth_required
def me():
    user = g.current_user
    return jsonify(
        {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }
    )


@app.get("/catalog/skins")
@auth_required
def catalog_skins():
    page = max(1, int(request.args.get("page", 1)))
    page_size = min(100, max(1, int(request.args.get("page_size", 20))))
    weapon = (request.args.get("weapon") or "").strip()
    rarity = (request.args.get("rarity") or "").strip()
    q = (request.args.get("q") or "").strip()

    query = SkinCatalog.query
    if weapon:
        query = query.filter(SkinCatalog.weapon == weapon)
    if rarity:
        query = query.filter(SkinCatalog.rarity == rarity)
    if q:
        pattern = f"%{q}%"
        query = query.filter((SkinCatalog.skin_name.ilike(pattern)) | (SkinCatalog.weapon.ilike(pattern)))

    total = query.count()
    items = (
        query.order_by(SkinCatalog.weapon.asc(), SkinCatalog.skin_name.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return jsonify(
        {
            "items": [_catalog_to_dict(i) for i in items],
            "page": page,
            "page_size": page_size,
            "total": total,
            "has_next": (page * page_size) < total,
        }
    )


@app.get("/catalog/skins/search")
@auth_required
def catalog_skins_search():
    q = (request.args.get("q") or "").strip()
    if len(q) < 2:
        return jsonify({"error": "q must be at least 2 characters"}), 400

    limit = min(50, max(1, int(request.args.get("limit", 20))))
    pattern = f"%{q}%"

    items = (
        SkinCatalog.query.filter((SkinCatalog.skin_name.ilike(pattern)) | (SkinCatalog.weapon.ilike(pattern)))
        .order_by(SkinCatalog.weapon.asc(), SkinCatalog.skin_name.asc())
        .limit(limit)
        .all()
    )

    return jsonify({"items": [_catalog_to_dict(i) for i in items], "limit": limit, "count": len(items)})


@app.get("/skins")
@auth_required
def my_skins():
    user = g.current_user
    items = (
        UserSkin.query.filter_by(user_id=user.id)
        .order_by(UserSkin.created_at.desc())
        .all()
    )
    return jsonify({"items": [_user_skin_to_dict(i) for i in items], "total": len(items)})


@app.post("/skins")
@auth_required
def add_skin():
    user = g.current_user
    data = request.get_json(silent=True) or {}

    catalog_skin_id = data.get("catalog_skin_id")
    if not catalog_skin_id:
        return jsonify({"error": "catalog_skin_id is required"}), 400

    catalog_skin = SkinCatalog.query.get(int(catalog_skin_id))
    if not catalog_skin:
        return jsonify({"error": "catalog skin not found"}), 404

    quantity = int(data.get("quantity", 1))
    if quantity < 1:
        return jsonify({"error": "quantity must be >= 1"}), 400

    buy_price = data.get("buy_price_eur")
    if buy_price is not None and str(buy_price).strip() != "":
        buy_price = float(buy_price)
        if buy_price < 0:
            return jsonify({"error": "buy_price_eur must be >= 0"}), 400
    else:
        buy_price = None

    item = UserSkin(
        user_id=user.id,
        catalog_skin_id=catalog_skin.id,
        wear=(data.get("wear") or "").strip() or None,
        stattrak=bool(data.get("stattrak", False)),
        quantity=quantity,
        note=(data.get("note") or "").strip() or None,
        buy_price_eur=buy_price,
    )
    db.session.add(item)
    db.session.commit()

    return jsonify(_user_skin_to_dict(item)), 201


@app.put("/skins/<int:skin_id>")
@auth_required
def update_skin(skin_id: int):
    user = g.current_user
    item = UserSkin.query.filter_by(id=skin_id, user_id=user.id).first()
    if not item:
        return jsonify({"error": "skin entry not found"}), 404

    data = request.get_json(silent=True) or {}

    if "wear" in data:
        item.wear = (data.get("wear") or "").strip() or None
    if "stattrak" in data:
        item.stattrak = bool(data.get("stattrak"))
    if "quantity" in data:
        q = int(data.get("quantity"))
        if q < 1:
            return jsonify({"error": "quantity must be >= 1"}), 400
        item.quantity = q
    if "note" in data:
        item.note = (data.get("note") or "").strip() or None
    if "buy_price_eur" in data:
        val = data.get("buy_price_eur")
        if val is None or str(val).strip() == "":
            item.buy_price_eur = None
        else:
            val = float(val)
            if val < 0:
                return jsonify({"error": "buy_price_eur must be >= 0"}), 400
            item.buy_price_eur = val

    db.session.commit()
    return jsonify(_user_skin_to_dict(item))


@app.delete("/skins/<int:skin_id>")
@auth_required
def delete_skin(skin_id: int):
    user = g.current_user
    item = UserSkin.query.filter_by(id=skin_id, user_id=user.id).first()
    if not item:
        return jsonify({"error": "skin entry not found"}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({"deleted": True, "id": skin_id})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
