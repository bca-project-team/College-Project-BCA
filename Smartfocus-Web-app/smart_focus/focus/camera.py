import base64
import cv2
import mediapipe as mp
import numpy as np
import time
import math
import threading

from smart_focus.focus.session import FocusSession


# ----------------------------
# Thresholds (same as your file)
# ----------------------------
EAR_THRESHOLD = 0.22
BLINK_MIN = 0.08
BLINK_MAX = 0.5
CLOSED_MIN = 1.0
OPEN_DEBOUNCE = 0.25
HORIZONTAL_THRESH = 0.13


def euclidean(p1, p2):
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)


class CameraFocusTracker:
    """
    Web Camera Focus Tracker (Blink + Debounce + Time-correct)
    """

    def __init__(self, user_name, goal_hours):
        self.session = FocusSession(
            user_name=user_name,
            goal_hours=goal_hours,
            mode="Camera"
        )

        self.face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

        # ---- State machine vars ----
        self.state = "no_face"
        self.focus_status = "Distracted"

        self.blink_start = None
        self.blink_counted = False
        self.open_start = None

        self.current_status = "Distracted"
        self.running = True

        self.session.start()

        # background time ticker (CRITICAL)
        self.timer_thread = threading.Thread(
            target=self._tick_time,
            daemon=True
        )
        self.timer_thread.start()

    # ----------------------------
    # Time ticker
    # ----------------------------
    def _tick_time(self):
        while self.running:
            time.sleep(1)
            self.session.update_status(self.current_status)

    # ----------------------------
    # Frame processing
    # ----------------------------
    def process_frame(self, frame_base64):
        if not self.running:
            return {"status": "stopped"}

        img_bytes = base64.b64decode(frame_base64.split(",")[1])
        img_array = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        now = time.time()

        # ----------------------------
        # No face detected
        # ----------------------------
        if not results.multi_face_landmarks:
            self.state = "no_face"
            self.focus_status = "Distracted"
            self.blink_start = None
            self.blink_counted = False
            self.open_start = None

        else:
            face = results.multi_face_landmarks[0]

            top = face.landmark[159]
            bottom = face.landmark[145]
            left = face.landmark[33]
            right = face.landmark[133]

            ver = euclidean(top, bottom)
            hor = euclidean(left, right)
            EAR = ver / hor if hor != 0 else 0
            eyes_open = EAR > EAR_THRESHOLD

            # ----------------------------
            # Eyes closed logic
            # ----------------------------
            if not eyes_open:
                self.open_start = None
                if self.blink_start is None:
                    self.blink_start = now
                    self.blink_counted = False

                closed_duration = now - self.blink_start

                if closed_duration > CLOSED_MIN:
                    self.state = "closed"
                    self.focus_status = "Distracted"

                elif BLINK_MIN < closed_duration <= BLINK_MAX:
                    self.state = "blink"
                    self.focus_status = "Focused"  # blink ≠ distracted
                    self.blink_counted = True

                else:
                    self.focus_status = "Focused"

            # ----------------------------
            # Eyes open logic
            # ----------------------------
            else:
                if self.open_start is None:
                    self.open_start = now

                open_duration = now - self.open_start

                if self.state in ("blink", "closed", "recovering"):
                    if open_duration >= OPEN_DEBOUNCE:
                        self.state = "focused"
                        self.focus_status = "Focused"
                        self.blink_start = None
                        self.blink_counted = False
                        self.open_start = None
                    else:
                        self.state = "recovering"
                        self.focus_status = "Distracted"
                else:
                    self.state = "focused"
                    self.focus_status = "Focused"
                    self.blink_start = None
                    self.blink_counted = False

            # ----------------------------
            # Head direction check
            # ----------------------------
            if self.state == "focused":
                left_eye_x = face.landmark[33].x
                right_eye_x = face.landmark[263].x
                if abs(left_eye_x - right_eye_x) < HORIZONTAL_THRESH:
                    self.focus_status = "Distracted"

        # ----------------------------
        # Update session status
        # ----------------------------
        self.current_status = "Focused" if self.focus_status == "Focused" else "Distracted"

        return {
            "status": self.current_status,
            "focused_seconds": int(self.session.focused_seconds),
            "distracted_seconds": int(self.session.distracted_seconds),
            "focus_score": self.session.calculate_score()
        }

    # ----------------------------
    # Stop session
    # ----------------------------
    def stop(self):
        self.running = False
        self.session.stop()
        return self.session.summary()