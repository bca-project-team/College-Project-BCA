from flask import Flask, render_template, request, jsonify, redirect, session
import threading
import traceback
import pandas as pd
import os
import csv

from smart_focus.focus.no_camera import NoCameraFocusTracker
from smart_focus.focus.camera import CameraFocusTracker
from smart_focus.utils.logger import init_logger
from smart_focus.analytics.graphs import build_focus_graph
from smart_focus.analytics.reports import get_weekly_report, get_monthly_report
from smart_focus.analytics.parents import get_parent_email
from smart_focus.utils.emailer import send_email

# ---------------------------
# App setup
# ---------------------------
app = Flask(__name__)
app.secret_key = "smartfocus-secret-key"

DATA_DIR = os.path.join(app.root_path, "data")
os.makedirs(DATA_DIR, exist_ok=True)

init_logger(DATA_DIR)

tracker = None
session_result = None
session_thread = None

USERS_FILE = os.path.join(DATA_DIR, "users.csv")

# ---------------------------
# ROOT → redirect based on auth
# ---------------------------
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    return redirect("/dashboard")

# ---------------------------
# REGISTER (ONE TIME)
# ---------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = request.form["user"].strip().lower().replace(" ", "")
        grade = request.form["grade"]
        student_phone = request.form["student_phone"]
        parent_name = request.form["parent_name"]
        parent_email = request.form["parent_email"]
        parent_phone = request.form["parent_phone"]

        # Create file with header if not exists
        file_exists = os.path.exists(USERS_FILE)
        if file_exists:
            with open(USERS_FILE, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["user"] == user:
                        return "User already exists"

        with open(USERS_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow([
                    "user",
                    "grade",
                    "student_phone",
                    "parent_name",
                    "parent_email",
                    "parent_phone"
                ])
            writer.writerow([
                user,
                grade,
                student_phone,
                parent_name,
                parent_email,
                parent_phone
            ])

        return redirect("/login")

    return render_template("register.html")

# ---------------------------
# LOGIN (SIMPLE)
# ---------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["user"].strip().lower().replace(" ", "")

        if not os.path.exists(USERS_FILE):
            return redirect("/register")

        with open(USERS_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["user"] == user:
                    session["user"] = user
                    return redirect("/dashboard")

        return "User not registered"

    return render_template("login.html")

# ---------------------------
# DASHBOARD (MAIN APP)
# ---------------------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        user=session["user"]
    )

# ---------------------------
# LOGOUT
# ---------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------------------
# START SESSION
# ---------------------------
@app.route("/start", methods=["POST"])
def start():
    global tracker, session_result, session_thread

    try:
        if "user" not in session:
            return jsonify({"status": "not_logged_in"}), 401

        data = request.get_json(force=True)
        user = session["user"]
        goal_seconds = int(data.get("goal_seconds", 0))
        goal_hours = goal_seconds / 3600
        mode = data.get("mode", "").strip().lower()

        session_result = None
        print(f"▶ Starting session | user={user}, goal={goal_hours}, mode={mode}")

        if mode == "camera":
            tracker = CameraFocusTracker(user, goal_hours)
        else:
            tracker = NoCameraFocusTracker(
                user,
                goal_hours,
                alert_sound="alert2.wav",
                warning_sound="alert1.wav"
            )
            session_thread = threading.Thread(
                target=run_session,
                daemon=True
            )
            session_thread.start()

        return jsonify({"status": "started"})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

def run_session():
    global session_result, tracker
    try:
        with app.app_context():
            if tracker and not isinstance(tracker, CameraFocusTracker):
                session_result = tracker.start()
    except Exception:
        traceback.print_exc()

# ---------------------------
# STOP SESSION
# ---------------------------
@app.route("/stop", methods=["POST"])
def stop():
    global tracker, session_result

    if tracker:
        session_result = tracker.stop()
        tracker = None

    return jsonify({"status": "stopped", "result": session_result})

# ---------------------------
# RESULT
# ---------------------------
@app.route("/result")
def result():
    return render_template("result.html", result=session_result)

# ---------------------------
# GRAPH
# ---------------------------
@app.route("/graph")
def graph():
    if "user" not in session:
        return redirect("/login")

    graph_data = build_focus_graph(DATA_DIR, session["user"])
    return render_template("graph.html", graph_data=graph_data)

# ---------------------------
# HISTORY
# ---------------------------
@app.route("/history")
def history():
    if not os.path.exists(os.path.join(DATA_DIR, "sessions.csv")):
        return render_template("history.html", records=[])

    df = pd.read_csv(os.path.join(DATA_DIR, "sessions.csv"))
    return render_template("history.html", records=df.to_dict(orient="records"))

# ---------------------------
# CAMERA FRAME
# ---------------------------
@app.route("/frame", methods=["POST"])
def receive_frame():
    if not tracker or not isinstance(tracker, CameraFocusTracker):
        return jsonify({"status": "no camera session"})

    data = request.get_json()
    frame = data.get("frame")
    if not frame:
        return jsonify({"status": "no frame"})

    return jsonify(tracker.process_frame(frame))

# ---------------------------
# WEEKLY REPORT
# ---------------------------
@app.route("/weekly-report")
def weekly_report():
    if "user" not in session:
        return redirect("/login")

    report = get_weekly_report(DATA_DIR, session["user"])
    return render_template("weekly.html", report=report)

# ---------------------------
# MONTHLY REPORT
# ---------------------------
@app.route("/monthly-report")
def monthly_report():
    if "user" not in session:
        return redirect("/login")

    report = get_monthly_report(DATA_DIR, session["user"])
    return render_template("monthly.html", report=report)

# ---------------------------
# SEND REPORT TO PARENT
# ---------------------------
@app.route("/send-weekly-parent-report")
def send_weekly_parent_report():
    if "user" not in session:
        return redirect("/login")

    user = session["user"]
    report = get_weekly_report(DATA_DIR, user)
    parent_email = get_parent_email(DATA_DIR, user)

    if not parent_email:
        return "Parent email not found", 404

    body = f"""
Weekly Focus Report for {user}

Total Focus Time: {report['total_focus_minutes']} minutes
Average Daily Focus: {report['average_daily_minutes']} minutes
Days Tracked: {report['days_tracked']}
Goal Achieved Days: {report['goal_days']}

– SmartFocus System
"""

    sent = send_email(parent_email, "Weekly Focus Report", body)
    return "Email sent successfully" if sent else "Email failed"

# ---------------------------
# RUN
# ---------------------------
if __name__ == "__main__":
    print(" SmartFocus Web App Starting...")
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
        use_reloader=False
    )