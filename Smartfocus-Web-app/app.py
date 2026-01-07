from flask import Flask, render_template, request, redirect, url_for
import threading

from smart_focus.focus.no_camera import NoCameraFocusTracker
from smart_focus.focus.camera import CameraFocusTracker
from smart_focus.analytics.graphs import plot_focus_progress

app = Flask(__name__)

tracker = None
session_result = None
session_thread = None


# ---------------------------
# Home page
# ---------------------------
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


# ---------------------------
# Start focus session
# ---------------------------
@app.route("/start", methods=["POST"])
def start():
    global tracker, session_result, session_thread

    user = request.form.get("user")
    goal = float(request.form.get("goal"))
    mode = request.form.get("mode")

    session_result = None  # reset old result

    # Initialize tracker
    if mode == "camera":
        tracker = CameraFocusTracker(user, goal)
    else:
        tracker = NoCameraFocusTracker(
            user,
            goal,
            alert_sound="alert2.wav",    # optional sound paths
            warning_sound="alert1.wav"
        )

    # Run tracker in a separate daemon thread
    def run_session():
        global session_result
        session_result = tracker.start()  # returns FocusSession.summary()

    session_thread = threading.Thread(target=run_session, daemon=True)
    session_thread.start()

    return redirect(url_for("result"))


# ---------------------------
# Stop focus session
# ---------------------------
@app.route("/stop")
def stop():
    global tracker, session_result
    if tracker:
        tracker.stop()                             # ✅ stop tracker immediately
        session_result = tracker.session.summary() # ✅ update session_result
        tracker = None                             # ✅ prevent multiple stops
    return redirect(url_for("result"))


# ---------------------------
# Result page
# ---------------------------
@app.route("/result", methods=["GET"])
def result():
    return render_template("result.html", result=session_result)


# ---------------------------
# Graph page
# ---------------------------
@app.route("/graph")
def graph():
    user = request.args.get("user")
    plot_focus_progress(user)
    return "Graph opened in new window."


# ---------------------------
# Run Flask
# ---------------------------
if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)
