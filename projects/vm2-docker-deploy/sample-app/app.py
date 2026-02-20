from flask import Flask, jsonify
import os

app = Flask(__name__)

APP_NAME = os.getenv("APP_NAME", "sample-api")
APP_VERSION = os.getenv("APP_VERSION", "dev")


@app.get("/")
def root():
    return jsonify({"message": "ok", "app": APP_NAME, "version": APP_VERSION})


@app.get("/health")
def health():
    return jsonify({"status": "healthy"})


@app.get("/version")
def version():
    return jsonify({"app": APP_NAME, "version": APP_VERSION})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
