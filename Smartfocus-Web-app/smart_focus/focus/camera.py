import base64
import math
import cv2
import numpy as np
import mediapipe as mp

from smart_focus.focus.session import FocusSession


# ---------------------------------------------------
# Helper: Decide focus using MediaPipe
# ---------------------------------------------------
def is_focused_mediapipe(face_landmarks):
    top = face_landmarks.landmark[159]
    bottom = face_landmarks.landmark[145]
    left = face_landmarks.landmark[33]
    right = face_landmarks.landmark[133]

    def euclidean(p1, p2):
        return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

    vertical = euclidean(top, bottom)
    horizontal = euclidean(left, right)

    if horizontal == 0:
        return False

    EAR = vertical / horizontal

    # Blink / closed eyes
    if EAR < 0.22:
        return False

    # Head direction
    left_eye_x = face_landmarks.landmark[33].x
    right_eye_x = face_landmarks.landmark[263].x

    if abs(left_eye_x - right_eye_x) < 0.13:
        return False

    return True


# ---------------------------------------------------
# Web Camera Focus Tracker
# ---------------------------------------------------
class CameraFocusTracker:
    """
    Web-based camera focus tracker.
    Receives frames from browser (base64),
    processes them using MediaPipe.
    """

    def __init__(self, user_name, goal_hours):
        self.session = FocusSession(
            user_name=user_name,
            goal_hours=goal_hours,
            mode="Camera"
        )

        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            refine_landmarks=True
        )

        self.running = True
        self.session.start()

    # ------------------------------------------------
    # Process ONE frame from browser
    # ------------------------------------------------
    def process_frame(self, frame_base64):
        if not self.running:
            return {"status": "stopped"}

        # Decode base64 image
        img_bytes = base64.b64decode(frame_base64.split(",")[1])
        img_array = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)

        focused = False

        if results.multi_face_landmarks:
            focused = is_focused_mediapipe(
                results.multi_face_landmarks[0]
            )

        # Update session + CSV timeline
        if focused:
            self.session.update_status("Focused")
        else:
            self.session.update_status("Distracted")

        return {
            "status": "Focused" if focused else "Distracted",
            "focused_seconds": int(self.session.focused_seconds),
            "distracted_seconds": int(self.session.distracted_seconds)
        }

    # ------------------------------------------------
    # Live data for UI
    # ------------------------------------------------
    def get_live_data(self):
        summary = self.session.summary()
        return {
            "status": self.session.current_status,
            "focused_seconds": summary["focused_seconds"],
            "distracted_seconds": summary["distracted_seconds"],
            "focus_score": summary["focus_score"]
        }

    # ------------------------------------------------
    # Stop session cleanly
    # ------------------------------------------------
    def stop(self):
        self.running = False
        self.session.stop()
        return self.session.summary()