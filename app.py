import os
import sys
import csv
import threading
import webbrowser
from datetime import datetime

from flask import Flask, request, jsonify, render_template


def get_base_dir() -> str:
    # When running as a packaged executable, use the executable directory.
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = get_base_dir()
SESSIONS_DIR = os.path.join(BASE_DIR, "sessions")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")


def ensure_runtime_directories() -> None:
    for path in (SESSIONS_DIR, TEMPLATES_DIR, STATIC_DIR):
        os.makedirs(path, exist_ok=True)


ensure_runtime_directories()

app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)

current_session = None


def format_duration(seconds: int) -> str:
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def safe_filename(text: str) -> str:
    return "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in text)


@app.route("/")
def index():
    return render_template("index.html")


@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/start", methods=["POST"])
def start():
    global current_session
    ensure_runtime_directories()
    data = request.get_json()
    subject = (data or {}).get("subject", "").strip()

    if not subject:
        return jsonify({"error": "Informe o assunto antes de iniciar."}), 400

    if current_session:
        return jsonify({"error": "Ja existe uma sessao em andamento."}), 400

    current_session = {
        "subject": subject,
        "start_time": datetime.now(),
    }

    return jsonify({
        "status": "started",
        "subject": subject,
        "start_time": current_session["start_time"].isoformat(),
    })


@app.route("/stop", methods=["POST"])
def stop():
    global current_session

    if not current_session:
        return jsonify({"error": "Nenhuma sessao em andamento."}), 400

    end_time = datetime.now()
    start_time = current_session["start_time"]
    subject = current_session["subject"]

    total_seconds = int((end_time - start_time).total_seconds())
    duration_str = format_duration(total_seconds)

    filename = (
        f"estudo_{start_time.strftime('%Y%m%d_%H%M%S')}_{safe_filename(subject)}.csv"
    )

    ensure_runtime_directories()
    filepath = os.path.join(SESSIONS_DIR, filename)

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["data_hora_inicial", "data_hora_final", "tempo_estudado", "assunto"])
        writer.writerow([
            start_time.strftime("%Y-%m-%d %H:%M:%S"),
            end_time.strftime("%Y-%m-%d %H:%M:%S"),
            duration_str,
            subject,
        ])

    current_session = None

    return jsonify({
        "status": "stopped",
        "filename": filename,
        "duration": duration_str,
        "subject": subject,
        "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
    })


@app.route("/status", methods=["GET"])
def status():
    if current_session:
        elapsed = int((datetime.now() - current_session["start_time"]).total_seconds())
        return jsonify({
            "active": True,
            "subject": current_session["subject"],
            "start_time": current_session["start_time"].isoformat(),
            "elapsed": format_duration(elapsed),
            "elapsed_seconds": elapsed,
        })
    return jsonify({"active": False})


if __name__ == "__main__":
    print("Calculadora de Tempo de Estudo iniciada em http://localhost:5000")
    threading.Timer(1.0, lambda: webbrowser.open("http://localhost:5000")).start()
    app.run(debug=True, use_reloader=True, port=5000)
