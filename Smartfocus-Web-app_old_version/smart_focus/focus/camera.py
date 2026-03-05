import base64
import cv2
import mediapipe as mp
import numpy as np
import time
import math
import threading

from smart_focus.focus.session import FocusSession


EAR_THRESHOLD = 0.22
BLINK_MIN = 0.08
BLINK_MAX = 0.5
CLOSED_MIN = 1.0
OPEN_DEBOUNCE = 0.25
HEAD_TURN_THRESHOLD=0.12


def euclidean(p1, p2):
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)


class CameraFocusTracker:
    """
    FINAL CORRECT VERSION

    - Camera decides ONLY Focused / Distracted
    - Session updates time ONCE PER SECOND
    - Timing is NOT dependent on frame rate
    """

    def __init__(self, user_name, goal_hours):
        self.session = FocusSession(
            user_name=user_name,
            goal_hours=goal_hours,
            mode="camera"
        )

        self.face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

        self.state = "no_face"
        self.current_status = "Distracted"
        self.running = True

        self.blink_start = None
        self.blink_counted = False
        self.open_start = None
        self.blink_count = 0

        # Start session timing
        self.session.start()

        # 🔥 HARD 1-SECOND TIMER (SOURCE OF TRUTH)
        self.timer_thread = threading.Thread(
            target=self._time_loop,
            daemon=True
        )
        self.timer_thread.start()

    # =========================
    # 1-SECOND TIME LOOP
    # =========================
    def _time_loop(self):
        while self.running:
            time.sleep(1)
            self.session.update_status(self.current_status)

    # =========================
    # FRAME PROCESSING
    # =========================
    def process_frame(self, frame_base64):
        if not self.running:
            return {"status": "stopped"}

        img_bytes = base64.b64decode(frame_base64.split(",")[1])
        img_array = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        now = time.time()
        focus_status = "Distracted"

        if not results.multi_face_landmarks:
            self.state = "no_face"

        else:
            face = results.multi_face_landmarks[0]

            top = face.landmark[159]
            bottom = face.landmark[145]
            left = face.landmark[33]
            right = face.landmark[133]

            ver = euclidean(top, bottom)
            hor = euclidean(left, right)
            EAR = ver / hor if hor else 0
            eyes_open = EAR > EAR_THRESHOLD

            if not eyes_open:
                if self.blink_start is None:
                    self.blink_start = now
                    self.blink_counted = False

                closed_duration = now - self.blink_start

                if closed_duration > CLOSED_MIN:
                    self.state = "closed"
                elif BLINK_MIN < closed_duration <= BLINK_MAX:
                    if not self.blink_counted:
                        self.blink_count += 1
                        self.blink_counted = True
                    self.state = "blink"
                else:
                    self.state = "focused"
                    focus_status = "Focused"

            else:
                self.blink_start = None
                self.blink_counted = False
                self.state = "focused"
                focus_status = "Focused"

            nose_x = face.landmark[1].x
            eye_center_x = (face.landmark[33].x + face.landmark[263].x) / 2
            print(abs(nose_x-eye_center_x))
            if abs(nose_x - eye_center_x) > HEAD_TURN_THRESHOLD:
                focus_status = "Distracted"

        #  THIS is what timer reads
        self.current_status = focus_status
        print("Status : ",self.current_status)

        return {
            "status": self.current_status,
            "state": self.state,
            "blinks": self.blink_count,
            "focused_seconds": int(self.session.focused_seconds),
            "distracted_seconds": int(self.session.distracted_seconds),
            "focus_score": self.session.calculate_score()
        }

    # =========================
    # STOP SESSION
    # =========================
    def stop(self):
        self.running = False
        self.session.stop()
        return self.session.summary()