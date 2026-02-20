from flask import Flask, jsonify, Response
import os

app = Flask(__name__)

APP_NAME = os.getenv("APP_NAME", "counter-orion")
APP_VERSION = os.getenv("APP_VERSION", "dev")


@app.get("/")
def root():
    html = f"""
<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{APP_NAME}</title>
  <style>
    body {{ font-family: Arial, sans-serif; background:#0f172a; color:#e2e8f0; margin:0; }}
    .wrap {{ max-width: 680px; margin: 10vh auto; padding: 24px; background:#1e293b; border-radius:12px; border:1px solid #334155; }}
    .row {{ margin-top: 12px; }}
    button {{ margin-top: 14px; padding: 8px 14px; border:0; border-radius:8px; background:#38bdf8; color:#082f49; font-weight:700; cursor:pointer; }}
  </style>
</head>
<body>
  <main class=\"wrap\">
    <h1>Orion Sample Browser App</h1>
    <p id=\"msg\">Loading...</p>
    <div class=\"row\">Service: <strong>{APP_NAME}</strong></div>
    <div class=\"row\">Version: <strong id=\"version\">{APP_VERSION}</strong></div>
    <div class=\"row\">Health: <strong id=\"health\">checking...</strong></div>
    <button id=\"refresh\">Refresh</button>
  </main>
  <script>
    async function refresh() {{
      const healthEl = document.getElementById('health');
      const msgEl = document.getElementById('msg');
      const verEl = document.getElementById('version');
      try {{
        const [healthRes, versionRes, msgRes] = await Promise.all([
          fetch('/health'),
          fetch('/version'),
          fetch('/api/message')
        ]);
        const health = await healthRes.json();
        const version = await versionRes.json();
        const msg = await msgRes.json();
        healthEl.textContent = health.status;
        verEl.textContent = version.version;
        msgEl.textContent = msg.message;
      }} catch (e) {{
        healthEl.textContent = 'error';
        msgEl.textContent = 'Failed to load data';
      }}
    }}
    document.getElementById('refresh').addEventListener('click', refresh);
    refresh();
  </script>
</body>
</html>
"""
    return Response(html, mimetype="text/html")


@app.get("/health")
def health():
    return jsonify({"status": "healthy"})


@app.get("/version")
def version():
    return jsonify({"app": APP_NAME, "version": APP_VERSION})


@app.get("/api/message")
def message():
    return jsonify({"message": "Hello from Counter-Orion 🚀"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
