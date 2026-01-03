# focus/session.py
import time
from smart_focus.utils.logger import log_timeline
from smart_focus.utils.logger import log_session

class FocusSession:
    """
    Core session manager for Smart Study Focus System.
    This class is independent of camera or no-camera logic.
    """

    def __init__(self, user_name, goal_hours, mode):
        self.user_name = user_name
        self.goal_hours = float(goal_hours)
        self.mode = mode

        self.start_time = None
        self.last_update_time = None

        self.focused_seconds = 0.0
        self.distracted_seconds = 0.0

        self.current_status = "Not Started"
        self.running = False

    def start(self):
        """Start the focus session"""
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.current_status = "Focused"
        self.running = True

    def update_status(self, status):
        """
        Update focus status.
        status should be either 'Focused' or 'Distracted'
        """
        if not self.running:
            return

        now = time.time()
        elapsed = now - self.last_update_time

        if self.current_status == "Focused":
            self.focused_seconds += elapsed
        else:
            self.distracted_seconds += elapsed

        self.current_status = status
        self.last_update_time = now
        log_timeline(user=self.user_name,
        mode=self.mode,
        status=status
        )

    def stop(self):
        """Stop the session and finalize time"""
        if not self.running:
            return

        self.update_status(self.current_status)
        self.running = False
        log_session(self.summary())

    def summary(self):
        """Return session summary (used by web app & graphs)"""
        total_seconds = self.focused_seconds + self.distracted_seconds

        return {
            "user": self.user_name,
            "mode": self.mode,
            "goal_hours": self.goal_hours,
            "focused_seconds": int(self.focused_seconds),
            "distracted_seconds": int(self.distracted_seconds),
            "focused_minutes": int(self.focused_seconds / 60),
            "goal_achieved": (self.focused_seconds / 3600) >= self.goal_hours,
            "total_seconds": int(total_seconds)
        }
