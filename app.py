from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import subprocess
from datetime import datetime
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:KARTHIK@2004@localhost/vulnscanner'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class ScanResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target_url = db.Column(db.String(255))
    result = db.Column(db.Text)
    summary = db.Column(db.Text)
    scan_date = db.Column(db.DateTime, default=datetime.utcnow)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/scan", methods=["POST"])
def scan():
    url = request.form["target_url"]

    # Nikto
    nikto_cmd = ["nikto", "-h", url]
    nikto_output = subprocess.getoutput(" ".join(nikto_cmd))

    # Bandit on a sample file
    bandit_cmd = ["bandit", "-r", "sample.py"]
    bandit_output = subprocess.getoutput(" ".join(bandit_cmd))

    combined_output = f"Nikto:\n{nikto_output}\n\nBandit:\n{bandit_output}"

    # Summarize with DeepSeek through Ollama
    try:
        response = requests.post(
            "http://127.0.0.1:11434/api/chat",
            json={
                "model": "deepseek-coder",
                "messages": [
                    {"role": "user", "content": combined_output}
                ]
            }
        )
        summary_text = response.json()['message']['content']
    except Exception as e:
        summary_text = "AI summary unavailable."

    result = ScanResult(
        target_url=url,
        result=combined_output,
        summary=summary_text,
    )
    db.session.add(result)
    db.session.commit()

    return redirect("/results")

@app.route("/results")
def results():
    all_scans = ScanResult.query.order_by(ScanResult.scan_date.desc()).all()
    return render_template("results.html", scans=all_scans)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
