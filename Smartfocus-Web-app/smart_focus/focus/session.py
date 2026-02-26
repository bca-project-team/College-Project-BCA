# smart_focus/focus/session.py

import time
from smart_focus.utils.alert import show_distraction_alert
from smart_focus.utils.logger import log_timeline, log_session


class FocusSession:
    """
    Core session manager for Smart Study Focus System.
    Handles time tracking, alerts, scoring, and logging.
    """

    def __init__(self, user_name, goal_hours, mode):
        self.user_name = user_name
        self.goal_hours = float(goal_hours)
        self.mode = mode.lower()   # 🔥 normalize once

        # -----------------------
        # Time tracking
        # -----------------------
        self.start_time = None
        self.last_update_time = None

        self.focused_seconds = 0.0
        self.distracted_seconds = 0.0

        self.current_status = "Not Started"
        self.running = False

        # -----------------------
        # Smart alert config
        # -----------------------
        self.distraction_threshold = 120  # seconds
        self._distracted_streak = 0.0
        self._alert_sent = False

        # 🔑 For clean timeline logging
        self._last_logged_status = None

    # -----------------------
    # Start session
    # -----------------------
    def start(self):
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.current_status = "Distracted"
        self.running = True

        # ✅ Log real initial state
        log_timeline(
            user=self.user_name,
            mode=self.mode,
            status=self.current_status
        )
        self._last_logged_status = self.current_status

    # -----------------------
    # Update focus status
    # -----------------------
    def update_status(self, status):
        if not self.running:
            return

        now = time.time()
        elapsed = now - self.last_update_time

        # ---- Time accounting ----
        if self.current_status == "Focused":
            self.focused_seconds += elapsed
        elif self.current_status == "Distracted":
            self.distracted_seconds += elapsed

        # ---- Update status ----
        self.current_status = status
        self.last_update_time = now

        # ---- Timeline logging (ONLY on change) ----
        if status != self._last_logged_status:
            log_timeline(
                user=self.user_name,
                mode=self.mode,
                status=status
            )
            self._last_logged_status = status

        # ---- Smart Distraction Alert ----
        if status == "Distracted":
            self._distracted_streak += elapsed

            if (
                self._distracted_streak >= self.distraction_threshold
                and not self._alert_sent
            ):
                show_distraction_alert(
                    self.user_name,
                    int(self._distracted_streak)
                )
                self._alert_sent = True
        else:
            self._distracted_streak = 0.0
            self._alert_sent = False

    # -----------------------
    # Calculate focus score
    # -----------------------
    def calculate_score(self):
        total = self.focused_seconds + self.distracted_seconds
        if total == 0:
            return 0
        return int((self.focused_seconds / total) * 100)

    # -----------------------
    # Stop session
    # -----------------------
    def stop(self):
        if not self.running:
            return

        # 🔥 Freeze time first
        self.running = False
        self.update_status(self.current_status)

        log_session(self.summary())

    # -----------------------
    # Session summary
    # -----------------------
    def summary(self):
        total = self.focused_seconds + self.distracted_seconds

        return {
            "user": self.user_name,
            "mode": self.mode,
            "goal_hours": self.goal_hours,
            "focused_seconds": int(self.focused_seconds),
            "distracted_seconds": int(self.distracted_seconds),
            "focused_minutes": int(self.focused_seconds / 60),
            "focus_score": self.calculate_score(),
            "goal_achieved": (self.focused_seconds / 3600) >= self.goal_hours,
            "total_seconds": int(total)
        }