from datetime import datetime, timedelta, timezone
from functools import wraps
import os

import jwt
from flask import Flask, Response, g, jsonify, request
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


with app.app_context():
    # Sprint 1 scaffold fallback: ensure base tables exist even before Alembic workflow is finalized.
    db.create_all()


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
    body { font-family: Arial, sans-serif; background:#0f172a; color:#e2e8f0; margin:0; }
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
    body { font-family: Arial, sans-serif; background:#0f172a; color:#e2e8f0; margin:0; }
    .wrap { max-width: 760px; margin: 8vh auto; padding: 24px; background:#1e293b; border-radius:12px; border:1px solid #334155; }
    button { margin-top: 14px; margin-right: 8px; padding: 8px 14px; border:0; border-radius:8px; background:#38bdf8; color:#082f49; font-weight:700; cursor:pointer; }
    pre { background:#0f172a; border:1px solid #334155; border-radius:8px; padding:10px; overflow:auto; }
  </style>
</head>
<body>
  <main class=\"wrap\">
    <h1>Counter-Orion / Profile</h1>
    <p>Authenticated profile page</p>
    <pre id=\"profile\">loading...</pre>
    <button id=\"refreshBtn\">Refresh profile</button>
    <button id=\"logoutBtn\">Logout</button>
    <button id=\"homeBtn\">Back to /</button>
  </main>
  <script>
    const tokenKey = 'counter_orion_access_token';
    const profileEl = document.getElementById('profile');

    async function loadProfile() {
      const accessToken = localStorage.getItem(tokenKey);
      if (!accessToken) {
        window.location.href = '/';
        return;
      }

      const res = await fetch('/me', {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });

      if (res.status === 401) {
        localStorage.removeItem(tokenKey);
        localStorage.removeItem('counter_orion_refresh_token');
        window.location.href = '/';
        return;
      }

      const data = await res.json();
      profileEl.textContent = JSON.stringify(data, null, 2);
    }

    document.getElementById('refreshBtn').addEventListener('click', loadProfile);
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
