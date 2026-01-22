from flask import Flask, render_template, request, jsonify
import threading
import traceback
import pandas as pd
import os

from smart_focus.focus.no_camera import NoCameraFocusTracker
from smart_focus.focus.camera import CameraFocusTracker
from smart_focus.utils.logger import init_logger
from smart_focus.analytics.graphs import build_focus_graph

app = Flask(__name__)

DATA_DIR = os.path.join(app.root_path, "data")
os.makedirs(DATA_DIR, exist_ok=True)

init_logger(DATA_DIR)

tracker = None
session_result = None
session_thread = None


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/start", methods=["POST"])
def start():
    global tracker, session_result, session_thread

    try:
        data = request.get_json(force=True)

        user = data.get("user", "").strip().lower()
        goal = float(data.get("goal"))
        mode = data.get("mode", "").strip().lower()

        session_result = None

        print(f"▶ Starting session | user={user}, goal={goal}, mode={mode}")

        if mode == "camera":
            tracker = CameraFocusTracker(user, goal)
        else:
            tracker = NoCameraFocusTracker(
                user,
                goal,
                alert_sound="alert2.wav",
                warning_sound="alert1.wav"
            )

            # 🔥 ONLY no-camera uses background runner
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
                print("✅ No-camera session finished")
    except Exception:
        traceback.print_exc()


@app.route("/stop", methods=["POST"])
def stop():
    global tracker, session_result

    try:
        if tracker:
            session_result = tracker.stop()
            tracker = None

        return jsonify({"status": "stopped", "result": session_result})

    except Exception:
        traceback.print_exc()
        return jsonify({"status": "error"}), 500


@app.route("/result")
def result():
    return render_template("result.html", result=session_result)


@app.route("/graph")
def graph():
    user = request.args.get("user", "").strip().lower()

    if not user:
        timeline_path = os.path.join(DATA_DIR, "timeline.csv")
        if os.path.exists(timeline_path):
            df = pd.read_csv(timeline_path)
            if not df.empty:
                user = str(df.iloc[-1]["user"]).strip().lower()

    graph_data = build_focus_graph(DATA_DIR, user)
    return render_template("graph.html", graph_data=graph_data)


@app.route("/history")
def history():
    session_path = os.path.join(DATA_DIR, "sessions.csv")

    if not os.path.exists(session_path):
        return render_template("history.html", records=[])

    df = pd.read_csv(session_path)
    return render_template("history.html", records=df.to_dict(orient="records"))

@app.route("/frame", methods=["POST"])
def receive_frame():
    global tracker

    if not tracker or not isinstance(tracker, CameraFocusTracker):
        return jsonify({"status": "no camera session"})

    data = request.get_json()
    frame = data.get("frame")

    if not frame:
        return jsonify({"status": "no frame"})

    return jsonify(tracker.process_frame(frame))

if __name__ == "__main__":
    print(" SmartFocus Web App Starting...")
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
        use_reloader=False
    )