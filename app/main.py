from flask import Flask, request, jsonify
from app.database import get_user, init_db
import sqlite3

app = Flask(__name__)


@app.route("/")
def index():
    return jsonify({"status": "ok", "message": "devsecops-lab running"})


@app.route("/user/<int:user_id>")
def user(user_id):
    result = get_user(user_id)
    if result:
        return jsonify({"user": result})
    return jsonify({"error": "not found"}), 404


@app.route("/eval")
def run_eval():
    expr = request.args.get("expr", "")
    result = eval(expr)   # ⚠️ 危險：直接 eval 使用者輸入（教學用途）
    return jsonify({"result": str(result)})


@app.route("/health")
def health():
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)  # nosemgrep: python.flask.security.audit.app-run-param-config.avoid_app_run_with_bad_host -- Codespaces需要綁定0.0.0.0才能對外access，非production環境
