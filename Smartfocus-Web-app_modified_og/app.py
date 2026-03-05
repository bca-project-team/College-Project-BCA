from flask import Flask, render_template, request, jsonify, redirect, session,current_app
import threading
import traceback
import pandas as pd
import os
import csv
import subprocess
import sys
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime,timedelta

from smart_focus.focus.no_camera import NoCameraFocusTracker
from smart_focus.focus.camera import CameraFocusTracker
from smart_focus.utils.logger import init_logger
from smart_focus.analytics.graphs import build_focus_graph
from smart_focus.analytics.reports import get_weekly_report, get_monthly_report
from smart_focus.utils.distraction_detector import DistractionDetector
from smart_focus.analytics.reports import get_focus_heatmap

def format_time(seconds):
    seconds=int(seconds)
    hours=seconds//3600
    minutes=(seconds%3600)//60
    secs=seconds%60
    if hours:
        return f'{hours} hr {minutes} min'
    if minutes:
        return f'{minutes} min {secs} sec'
    return f'{secs} sec'
 
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
    return redirect("/hub")

# ---------------------------
# REGISTER (ONE TIME)
# ---------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = request.form["user"].strip().lower().replace(" ", "")
        email=request.form.get('email',"")
        password=request.form["password"]
        
        confirm_password=request.form["confirm_password"]
        if password != confirm_password:
            return "Passwords do not match"
        hashed_password=generate_password_hash(password)

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
                    "email",
                    "password"
                ])
            writer.writerow([
                user,
                email,
                hashed_password
                
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
        password=request.form['password']
        if not os.path.exists(USERS_FILE):
            return redirect("/register")

        with open(USERS_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['user']==user and check_password_hash(row['password'],password):
                    session['user']=user
                    return redirect("/hub")

        return "Invalid username or password"

    return render_template("login.html")

@app.route("/hub")
def hub():
    if "user" not in session:
        return redirect("/login")

    user = session["user"]
    sessions_file = os.path.join(DATA_DIR, "sessions.csv")

    today_focus = 0
    weekly_avg = 0
    last_score = 0
    streak = 0

    if os.path.exists(sessions_file):
        df = pd.read_csv(sessions_file)
        user_df = df[df["user"] == user]

        if not user_df.empty:

            last_score = int(user_df.iloc[-1]["focus_score"])

            user_df["date"] = pd.to_datetime(user_df["timestamp"]).dt.date

            today = datetime.now().date()
            today_df = user_df[user_df["date"] == today]

            if not today_df.empty:
                today_focus = format_time(int(today_df["focused_seconds"].sum()))

            last7 = user_df.tail(7)
            weekly_avg = format_time(int(last7["focused_seconds"].mean()))

            user_df = user_df.sort_values("date", ascending=False)
            dates = user_df["date"].unique()

            current = today
            for d in dates:
                if d == current:
                    streak += 1
                    current = current - timedelta(days=1)
                else:
                    break

    return render_template(
        "hub.html",
        today_focus=today_focus,
        weekly_avg=weekly_avg,
        last_score=last_score,
        streak=streak
    )

@app.route("/analytics")
def analytics_dashboard():
    if "user" not in session:
        return redirect("/login")

    graph_data = build_focus_graph(DATA_DIR, session["user"])
    weekly = get_weekly_report(DATA_DIR, session["user"])
    monthly = get_monthly_report(DATA_DIR, session["user"])
    heatmap=get_focus_heatmap(DATA_DIR,session['user'])

    records = []
    sessions_file = os.path.join(DATA_DIR, "sessions.csv")
    if os.path.exists(sessions_file):
        df = pd.read_csv(sessions_file)
        records = df[df["user"] == session["user"]].to_dict(orient="records")

    return render_template(
        "analytics.html",
        graph_data=graph_data,
        weekly=weekly,
        monthly=monthly,
        heatmap=heatmap,
        records=records
    )

# ---------------------------
# DASHBOARD (MAIN APP)
# ---------------------------
@app.route("/focus")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    activity=request.args.get("activity","")
    return render_template(
        "focus.html",
        user=session["user"],
        activity=activity
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
    global tracker, session_result, session_thread,detector
    if tracker is not None:
        return jsonify({"status":"already_running"})
    try:
        if "user" not in session:
            return jsonify({"status": "not_logged_in"}), 401

        data = request.get_json(force=True)
        user = session["user"]
        goal_seconds = int(data.get("goal_seconds", 0))
        goal_hours = goal_seconds / 3600
        mode = data.get("mode", "").strip().lower()
        activity=data.get("activity","general")
        topic=data.get('topic','').lower()

        session_result = None
        print(f"▶ Starting session | user={user}, goal={goal_seconds}, mode={mode}")

        if mode == "camera":
            tracker = CameraFocusTracker(user, goal_hours,activity=activity,topic=topic)
        else:
            tracker = NoCameraFocusTracker(
                user,
                goal_seconds,
                alert_sound="alert2.wav",
                warning_sound="alert1.wav",
                activity=activity,
                topic=topic
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
                tracker.start()
    except Exception:
        traceback.print_exc()

# ---------------------------
# STOP SESSION
# ---------------------------
@app.route("/stop", methods=["POST"])
def stop():
    global tracker, session_result
    print("Stop route hit ")
    if tracker:
        print('tracker exists')
        session_result = tracker.stop()
        print('session result:')
        tracker = None
    return jsonify({"status": "stopped", "result": session_result})

@app.route("/live-stats")
def live_stats():
    global tracker

    if not tracker:
        return jsonify({"status": "no_session","auto_stopped":False})

    session_obj = tracker.session

    response= {
        "focused_seconds": int(session_obj.focused_seconds),
        "distracted_seconds": int(session_obj.distracted_seconds),
        "focus_score": session_obj.calculate_score(),
        "auto_stopped":getattr(tracker,"auto_stopped",False)
    }
    if getattr(tracker,"auto_stopped",False):
        response['result']=getattr(tracker,"last_summary",None)
    return jsonify(response)

# ---------------------------
# RESULT
# ---------------------------
@app.route("/result")
def result():
    global tracker,session_result
    result_data=None
    alert_message=None
    if session_result:
        result_data=session_result
    elif tracker and hasattr(tracker,"last_summary"):
        result_data=tracker.last_summary
    if result_data and result_data.get('auto_stopped'):
        alert_message="Session Auto-stopped Due to Continuous Distraction. Goal Not Achieved!!"
    return render_template("result.html", result=session_result,alert_message=alert_message)

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

import json
from datetime import datetime

@app.route("/save-note", methods=["POST"])
def save_note():
    if "user" not in session:
        return jsonify({"status": "not_logged_in"}), 401

    user = session["user"]
    data = request.get_json()
    content = data.get("content", "").strip()

    if not content:
        return jsonify({"status": "empty"}), 400

    file_path = os.path.join(DATA_DIR, f"notes_{user}.json")

    notes = []

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            notes = json.load(f)

    note = {
        "id": len(notes) + 1,
        "content": content,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    notes.append(note)

    with open(file_path, "w") as f:
        json.dump(notes, f, indent=4)

    return jsonify({"status": "saved"})


@app.route("/get-notes")
def get_notes():
    if "user" not in session:
        return jsonify([])

    user = session["user"]
    file_path = os.path.join(DATA_DIR, f"notes_{user}.json")

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return jsonify(json.load(f))

    return jsonify([])


@app.route("/delete-note/<int:note_id>", methods=["POST"])
def delete_note(note_id):
    if "user" not in session:
        return jsonify({"status": "not_logged_in"}), 401

    user = session["user"]
    file_path = os.path.join(DATA_DIR, f"notes_{user}.json")

    if not os.path.exists(file_path):
        return jsonify({"status": "not_found"}), 404

    with open(file_path, "r") as f:
        notes = json.load(f)

    notes = [n for n in notes if n["id"] != note_id]

    with open(file_path, "w") as f:
        json.dump(notes, f, indent=4)

    return jsonify({"status": "deleted"})

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