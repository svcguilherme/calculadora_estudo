import csv
import os
import threading
from datetime import datetime, timedelta
from flask import Flask, request, jsonify

app = Flask(__name__)

CSV_FILE = "estudos.csv"
CSV_FIELDS = ["assunto", "data_inicio", "data_fim", "duracao_minutos"]
SECONDS_PER_MINUTE = 60

# In-memory state for the current active session (protected by a lock)
sessao_ativa = {}
_lock = threading.Lock()


def _ensure_csv():
    """Create the CSV file with headers if it does not exist."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writeheader()


def _append_session(assunto: str, data_inicio: datetime, data_fim: datetime):
    """Append a completed session to the CSV file."""
    _ensure_csv()
    duracao = (data_fim - data_inicio).total_seconds() / SECONDS_PER_MINUTE
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writerow(
            {
                "assunto": assunto,
                "data_inicio": data_inicio.strftime("%Y-%m-%d %H:%M:%S"),
                "data_fim": data_fim.strftime("%Y-%m-%d %H:%M:%S"),
                "duracao_minutos": round(duracao, 2),
            }
        )


def _read_sessions():
    """Return all sessions from the CSV as a list of dicts."""
    _ensure_csv()
    sessions = []
    with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sessions.append(row)
    return sessions


@app.route("/iniciar", methods=["POST"])
def iniciar():
    """Start a study session.

    Request body (JSON):
        {"assunto": "<subject>"}

    Returns:
        JSON with confirmation message and start timestamp.
    """
    global sessao_ativa

    data = request.get_json(silent=True) or {}
    assunto = data.get("assunto", "").strip()
    if not assunto:
        return jsonify({"erro": "O campo 'assunto' é obrigatório."}), 400

    with _lock:
        if sessao_ativa:
            return (
                jsonify(
                    {
                        "erro": "Já existe uma sessão ativa.",
                        "assunto": sessao_ativa.get("assunto"),
                        "inicio": sessao_ativa["inicio"].strftime("%Y-%m-%d %H:%M:%S"),
                    }
                ),
                409,
            )

        sessao_ativa = {"assunto": assunto, "inicio": datetime.now()}
        inicio_str = sessao_ativa["inicio"].strftime("%Y-%m-%d %H:%M:%S")

    return (
        jsonify(
            {
                "mensagem": "Sessão iniciada.",
                "assunto": assunto,
                "inicio": inicio_str,
            }
        ),
        200,
    )


@app.route("/finalizar", methods=["POST"])
def finalizar():
    """Stop the active study session and record it.

    Returns:
        JSON with session summary (subject, duration in minutes).
    """
    global sessao_ativa

    with _lock:
        if not sessao_ativa:
            return jsonify({"erro": "Nenhuma sessão ativa no momento."}), 400

        fim = datetime.now()
        assunto = sessao_ativa["assunto"]
        inicio = sessao_ativa["inicio"]
        sessao_ativa = {}

    _append_session(assunto, inicio, fim)

    duracao = round((fim - inicio).total_seconds() / SECONDS_PER_MINUTE, 2)

    return jsonify(
        {
            "mensagem": "Sessão finalizada e registrada.",
            "assunto": assunto,
            "inicio": inicio.strftime("%Y-%m-%d %H:%M:%S"),
            "fim": fim.strftime("%Y-%m-%d %H:%M:%S"),
            "duracao_minutos": duracao,
        }
    )


@app.route("/sessoes", methods=["GET"])
def sessoes():
    """List all recorded study sessions.

    Returns:
        JSON array of all sessions stored in the CSV.
    """
    return jsonify(_read_sessions())


@app.route("/resumo_semanal", methods=["GET"])
def resumo_semanal():
    """Return a summary of study time for the current week (Mon–Sun).

    Returns:
        JSON with total minutes per subject for the current week.
    """
    hoje = datetime.now().date()
    inicio_semana = hoje - timedelta(days=hoje.weekday())  # Monday
    fim_semana = inicio_semana + timedelta(days=6)  # Sunday

    sessions = _read_sessions()
    resumo = {}
    total_geral = 0.0

    for s in sessions:
        try:
            data_inicio = datetime.strptime(s["data_inicio"], "%Y-%m-%d %H:%M:%S").date()
        except ValueError:
            continue

        if inicio_semana <= data_inicio <= fim_semana:
            assunto = s["assunto"]
            try:
                minutos = float(s["duracao_minutos"])
            except ValueError:
                continue
            resumo[assunto] = round(resumo.get(assunto, 0.0) + minutos, 2)
            total_geral = round(total_geral + minutos, 2)

    return jsonify(
        {
            "semana": f"{inicio_semana} a {fim_semana}",
            "resumo_por_assunto": resumo,
            "total_minutos": total_geral,
        }
    )


if __name__ == "__main__":
    _ensure_csv()
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode, port=5000)
