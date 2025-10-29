import cv2
import mediapipe as mp
import time
import math
import csv
from datetime import datetime

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

focused_time = 0.0
last_focus_time = None

blink_count = 0

# timing/state variables
blink_start = None          # when eyes first went below threshold
blink_counted = False       # whether current closure counted as blink
open_start = None           # when eyes returned open (for stable-open debounce)
state = "No Face Detected"  # "focused", "blink", "closed", "recovering", "not_focused", "no_face"

# thresholds (tweak if needed)
EAR_THRESHOLD = 0.22        # below = closed
BLINK_MIN = 0.08            # min closure to consider (s)
BLINK_MAX = 0.5             # max closure for blink (s)
CLOSED_MIN = 1.0            # closed if > this (s)
OPEN_DEBOUNCE = 0.25        # need eyes open continuously for this to accept focused (s)
HORIZONTAL_THRESH = 0.13    # head/eye direction threshold

def euclidean(p1, p2):
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

print("Starting... press 'q' to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    # default if no face
    if not results.multi_face_landmarks:
        state = "no_face"
        focus_status = "No Face Detected !"
        # reset timing so we don't carry old timings into new face detection
        blink_start = None
        blink_counted = False
        open_start = None
    else:
        face = results.multi_face_landmarks[0]
        # landmarks used
        top = face.landmark[159]
        bottom = face.landmark[145]
        left = face.landmark[33]
        right = face.landmark[133]

        # EAR
        ver = euclidean(top, bottom)
        hor = euclidean(left, right)
        EAR = ver / hor if hor != 0 else 0.0
        eyes_open = EAR > EAR_THRESHOLD

        # --- Blink / Eyes Closed / Recovery logic (state machine) ---
        now = time.time()

        if not eyes_open:
            # eyes currently closed
            open_start = None  # reset open tracking
            if blink_start is None:
                blink_start = now
                blink_counted = False
            closed_duration = now - blink_start

            # Long closure -> Eyes Closed state (continuous update)
            if closed_duration > CLOSED_MIN:
                state = "closed"
                focus_status = f"Eyes Closed {closed_duration:.1f}s"

            # Short closure -> Blink (count once)
            elif BLINK_MIN < closed_duration <= BLINK_MAX:
                if not blink_counted:
                    blink_count += 1
                    blink_counted = True
                    state = "blink"
                    focus_status = "Blink Detected"
                else:
                    # already counted this blink; keep showing "Blink Detected" for a tiny time
                    state = "blink"
                    focus_status = "Blink Detected"
            else:
                # very short/no closure yet (initial frames) — keep previous state unless closed/blink
                if state not in ("blink", "closed"):
                    focus_status = "Focused"  # assume focused until proven otherwise
                    state = "focused"

        else:
            # eyes currently open
            # start/continue open debounce
            if open_start is None:
                open_start = now
            open_duration = now - open_start

            # If we were in blink/closed recently, wait for stable open before marking focused
            if state in ("blink", "closed", "recovering"):
                if open_duration >= OPEN_DEBOUNCE:
                    state = "focused"
                    focus_status = "Focused"
                    # reset closure trackers
                    blink_start = None
                    blink_counted = False
                    open_start = None
                else:
                    state = "recovering"
                    focus_status = "Recovering"
            else:
                # normal open -> focused for now (will be adjusted by head-direction)
                state = "focused"
                focus_status = "Focused"
                blink_start = None
                blink_counted = False

        # --- Head direction check (only when fully focused) ---
        left_eye_x = face.landmark[33].x
        right_eye_x = face.landmark[263].x
        horizontal_diff = abs(left_eye_x - right_eye_x)

        if state == "focused":
            if horizontal_diff > HORIZONTAL_THRESH:
                focus_status = "Focused"
            else:
                focus_status = "Not Focused"
        #print(f"EAR={EAR:.3f}, eyes_open={eyes_open}, closed_dur={(time.time()-blink_start) if blink_start else 0:.2f}, state={state}, status={focus_status}")

    # --- Focus time counter: only when final status is Focused ---
    if focus_status == "Focused":
        if last_focus_time is None:
            last_focus_time = time.time()
        else:
            diff = time.time() - last_focus_time
            focused_time += diff
            last_focus_time = time.time()
    else:
        last_focus_time = None

    # Format display time
    hours = int(focused_time // 3600)
    minutes = int((focused_time % 3600) // 60)
    seconds = int(focused_time % 60)
    display_time = f"{hours}h {minutes}m {seconds}s"

    # Overlay on frame
    cv2.putText(frame, f"Status: {focus_status}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
    cv2.putText(frame, f"Focus Time: {display_time}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
    cv2.putText(frame, f"Blinks: {blink_count}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2)
    cv2.imshow('Focus with Blink Tracker', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# write CSV
with open("focus_report.csv","a", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        f"{hours}h {minutes}m {seconds}s",
        f"Blinks: {blink_count}"
    ])

cap.release()
cv2.destroyAllWindows()
print("Session saved to focus_report.csv")
