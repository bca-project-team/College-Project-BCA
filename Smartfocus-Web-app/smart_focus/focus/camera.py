# smart_focus/focus/camera.py

import cv2
import time
import math
import mediapipe as mp

from smart_focus.focus.session import FocusSession


# ---------------------------------------------------
# Helper function: Decide Focus using MediaPipe
# ---------------------------------------------------
def is_focused_mediapipe(face_landmarks):
    """
    Returns True if user is focused, else False
    Logic:
    - Eye Aspect Ratio (EAR) for blink / closed eyes
    - Head direction using eye horizontal distance
    """

    # Eye landmark indices (MediaPipe)
    top = face_landmarks.landmark[159]
    bottom = face_landmarks.landmark[145]
    left = face_landmarks.landmark[33]
    right = face_landmarks.landmark[133]

    def euclidean(p1, p2):
        return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

    # Eye Aspect Ratio (EAR)
    vertical = euclidean(top, bottom)
    horizontal = euclidean(left, right)

    if horizontal == 0:
        return False

    EAR = vertical / horizontal

    # ---- Blink / Eyes closed ----
    if EAR < 0.22:
        return False

    # ---- Head direction check ----
    left_eye_x = face_landmarks.landmark[33].x
    right_eye_x = face_landmarks.landmark[263].x
    horizontal_diff = abs(left_eye_x - right_eye_x)

    if horizontal_diff < 0.13:
        return False

    return True


# ---------------------------------------------------
# Camera Focus Tracker Class
# ---------------------------------------------------
class CameraFocusTracker:
    """
    Camera-based focus tracker using MediaPipe.
    Updates FocusSession with Focused / Distracted states.
    """

    def __init__(self, user_name, goal_hours):
        self.session = FocusSession(
            user_name=user_name,
            goal_hours=goal_hours,
            mode="Camera"
        )

        # MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(refine_landmarks=True)

        # OpenCV camera
        self.cap = cv2.VideoCapture(0)
        self.running = False

    def start(self):
        print("📷 Camera Focus Session Started (press 'q' to quit)")
        self.session.start()
        self.running = True

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print("❌ Camera not detected")
                break

            # Mirror view
            frame = cv2.flip(frame, 1)

            # Convert to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)

            focused = False

            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]
                focused = is_focused_mediapipe(face_landmarks)

            # ---- Update session status ----
            if focused:
                self.session.update_status("Focused")
                status_text = "Focused"
                color = (0, 255, 0)
            else:
                self.session.update_status("Distracted")
                status_text = "Distracted"
                color = (0, 0, 255)

            # ---- Display on screen ----
            cv2.putText(
                frame,
                f"Status: {status_text}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                color,
                2
            )

            cv2.imshow("Smart Focus - Camera Mode", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.stop()
        return self.session.summary()

    def stop(self):
        self.running = False
        self.session.stop()
        self.cap.release()
        cv2.destroyAllWindows()