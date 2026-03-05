import time
import os
import threading
from pynput import keyboard, mouse
import pygame
from plyer import notification

from smart_focus.focus.session import FocusSession
from smart_focus.utils.distraction_detector import DistractionDetector



class NoCameraFocusTracker:
    """
    No-Camera Focus Tracker
    Goal-aware presence & distraction logic (NO LOOPS).
    """

    def __init__(
        self,
        user_name,
        goal_seconds,
        alert_sound=None,
        warning_sound=None,
        activity='general',
        topic=''
    ):
        # Convert goal to hours for session logging
        goal_hours = goal_seconds / 3600

        self.session = FocusSession(
            user_name=user_name,
            goal_hours=goal_hours,
            mode="no_camera",
            activity=activity,
            topic=topic.lower()
        )

        pygame.mixer.init()

        # Sounds
        self.alert_sound = alert_sound
        self.warning_sound = warning_sound

        # Activity tracking
        self.last_activity_time = time.time()
        self.is_idle = False

        self.keyboard_listener = None
        self.mouse_listener = None
        self.stop_event = threading.Event()
        self.running=False
        self.last_status = None

        # Goal timing
        self.goal_seconds = int(goal_seconds)
        self.session_start_time = None
        self.activity=activity.lower()
        self.topic=topic.lower()
        self.auto_stopped=False

        # 🔑 STAGE MACHINE
        # 0 = before 50%
        # 1 = 50% presence asked
        # 2 = after first refocus / present
        # 3 = 90% presence asked
        # 4 = finished (no alerts)
        self.stage = 0

        self.distraction_given = False

    # ---------------------------
    # Utilities
    # ---------------------------
    def _play_sound(self, sound_path):
        if not sound_path or not os.path.exists(sound_path):
            return

        def _play():
            try:
                pygame.mixer.music.load(sound_path)
                pygame.mixer.music.play()
            except Exception:
                pass

        threading.Thread(target=_play, daemon=True).start()

    def _notify(self, title, message, sound=None):
        if self.stop_event.is_set():
            return

        if sound:
            self._play_sound(sound)

        notification.notify(
            title=title,
            message=message,
            timeout=3
        )

    # ---------------------------
    # Activity callback
    # ---------------------------
    def on_activity(self, *args):
        if self.stop_event.is_set():
            return

        self.last_activity_time = time.time()

        # Refocus ONLY if distracted stage
        if self.is_idle:
            self._notify("Focus Restored", "Good job! You're back on track.")
            self.is_idle = False
            self.distraction_given = False

            # Move stage forward safely
            if self.stage == 1:
                self.stage = 2
            elif self.stage == 3:
                self.stage = 4

        self._set_status("Focused")

    # ---------------------------
    # Status update
    # ---------------------------
    def _set_status(self, status):
        status = status.strip().capitalize()
        if status != self.last_status:
            self.session.update_status(status)
            self.last_status = status

    # ---------------------------
    # Start / Stop
    # ---------------------------
    def start(self):
        print("🧠 No-Camera Focus Session Started")
        self.running=True
        self.session.start()
        if not hasattr(self,"detector"):
            self.detector=DistractionDetector(self)
            self.detector.start()
        self.session_start_time = time.time()
        self.stop_event.clear()
        self.last_activity_time = time.time()
        self.last_status = None

        self.keyboard_listener = keyboard.Listener(on_press=self.on_activity)
        self.mouse_listener = mouse.Listener(
            on_move=self.on_activity,
            on_click=self.on_activity,
            on_scroll=self.on_activity
        )

        self.keyboard_listener.start()
        self.mouse_listener.start()

        try:
            while not self.stop_event.is_set():
                time.sleep(1)
                self._update_state()
        finally:
            self._cleanup()

        return self.session.summary()

    def stop(self):
        if not self.running:
            return getattr(self,"last_summary",None)
        self.running=False
        self.stop_event.set()
        if hasattr(self,"detector"):
            self.detector.stop()
        self.session.stop()
        summary=self.session.summary()
        summary['auto_stopped']=getattr(self,'auto_stopped',False)
        self.last_summary=summary
        return summary

    def _cleanup(self):
        for listener in (self.keyboard_listener, self.mouse_listener):
            if listener:
                listener.stop()
        print(" No-Camera session ended cleanly")

    # ---------------------------
    # CORE LOGIC (FINAL & STABLE)
    # ---------------------------
    def _update_state(self):
        if self.stop_event.is_set() or self.session_start_time is None:
            return

        now = time.time()
        elapsed = now - self.session_start_time
        inactive = now - self.last_activity_time

        # -------- 50% PRESENCE
        if self.stage == 0 and elapsed >= self.goal_seconds * 0.5:
            self._notify(
                "Presence Check",
                "You're halfway to your goal. Are you still present?",
                self.warning_sound
            )
            self.stage = 1
            self.distraction_given = False
            return

        # -------- MISSED FIRST PRESENCE → ONE DISTRACTION
        if (
            self.stage == 1
            and inactive >= 15
            and not self.distraction_given
        ):
            self._notify(
                "Distraction Alert!",
                "You missed the presence check. Please refocus!",
                self.alert_sound
            )
            self._set_status("Distracted")
            self.is_idle = True
            self.distraction_given = True
            return

        # -------- 90% PRESENCE
        if self.stage == 2 and elapsed >= self.goal_seconds * 0.9:
            self._notify(
                "Final Presence Check",
                "You're almost at your goal. Stay focused!",
                self.warning_sound
            )
            self.stage = 3
            self.distraction_given = False
            return

        # -------- MISSED FINAL PRESENCE → ONE FINAL DISTRACTION
        if (
            self.stage == 3
            and inactive >= 15
            and not self.distraction_given
        ):
            self._notify(
                "Final Distraction Alert!",
                "You missed the final check. Session marked distracted.",
                self.alert_sound
            )
            self._set_status("Distracted")
            self.is_idle = True
            self.distraction_given = True
            self.stage = 4
            return

        # -------- NORMAL FOCUS
        self._set_status("Focused")