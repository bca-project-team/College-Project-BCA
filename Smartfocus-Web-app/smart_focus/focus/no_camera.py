import time
import os
import threading
from pynput import keyboard, mouse
import pygame
from plyer import notification

from smart_focus.focus.session import FocusSession


class NoCameraFocusTracker:
    """
    No-Camera Focus Tracker
    Uses keyboard + mouse activity to detect focus.
    """

    def __init__(
        self,
        user_name,
        goal_hours,
        idle_limit=20,
        idle_warning_time=10,
        alert_sound=None,
        warning_sound=None,
    ):
        # 🔑 IMPORTANT: mode MUST be lowercase & consistent
        self.session = FocusSession(
            user_name=user_name,
            goal_hours=goal_hours,
            mode="no_camera"
        )

        pygame.mixer.init()

        self.idle_limit = idle_limit
        self.idle_warning_time = idle_warning_time
        self.alert_sound = alert_sound
        self.warning_sound = warning_sound

        self.last_activity_time = time.time()
        self.is_idle = False
        self.warning_given = False

        self.keyboard_listener = None
        self.mouse_listener = None

        self.stop_event = threading.Event()

        # 🔑 prevents repeated identical log entries
        self.last_status = None


    # ---------------------------
    # Utility: sound
    # ---------------------------
    def _play_sound(self, sound_path):
        if not sound_path or not os.path.exists(sound_path):
            return

        def _play():
            try:
                pygame.mixer.music.load(sound_path)
                pygame.mixer.music.play()
            except Exception as e:
                print(f"(Sound error: {e})")

        threading.Thread(target=_play, daemon=True).start()


    # ---------------------------
    # Utility: notification
    # ---------------------------
    def _notify(self, title, message, sound=None):
        if self.stop_event.is_set():
            return

        try:
            if sound:
                self._play_sound(sound)

            notification.notify(
                title=title,
                message=message,
                timeout=3
            )
        except Exception as e:
            print(f"(Notification error: {e})")


    # ---------------------------
    # Activity callback
    # ---------------------------
    def on_activity(self, *args):
        if self.stop_event.is_set():
            return

        self.last_activity_time = time.time()

        if self.is_idle:
            self._notify("Focus Restored", "Good job! You're back on track.")
            self.is_idle = False
            self.warning_given = False

        self._set_status("Focused")


    # ---------------------------
    # Safe status updater
    # ---------------------------
    def _set_status(self, status):
        status = status.strip().capitalize()  # Focused / Distracted

        if status != self.last_status:
            self.session.update_status(status)
            self.last_status = status


    # ---------------------------
    # Start session
    # ---------------------------
    def start(self):
        print("🧠 No-Camera Focus Session Started")

        self.session.start()
        self.stop_event.clear()
        self.last_activity_time = time.time()
        self.last_status = None

        # Start input listeners
        self.keyboard_listener = keyboard.Listener(on_press=self.on_activity)
        self.mouse_listener = mouse.Listener(
            on_move=self.on_activity,
            on_click=self.on_activity,
            on_scroll=self.on_activity
        )

        self.keyboard_listener.start()
        self.mouse_listener.start()

        try:
            # 🔑 HEARTBEAT LOOP (THIS CREATES TIMELINE DATA)
            while not self.stop_event.is_set():
                time.sleep(1)
                self._update_state()
        finally:
            self._cleanup()

        return self.session.summary()


    # ---------------------------
    # Stop session (called by Flask)
    # ---------------------------
    def stop(self):
        self.stop_event.set()
        return self.session.summary()


    # ---------------------------
    # Cleanup
    # ---------------------------
    def _cleanup(self):
        for listener in [self.keyboard_listener, self.mouse_listener]:
            if listener:
                listener.stop()

        self.session.stop()
        print("✅ No-Camera session ended cleanly")


    # ---------------------------
    # Core logic
    # ---------------------------
    def _update_state(self):
        if self.stop_event.is_set():
            return

        inactive_for = time.time() - self.last_activity_time

        if inactive_for > self.idle_limit:
            if not self.is_idle:
                self._notify(
                    "Distraction Alert!",
                    "You've been idle. Please refocus!",
                    self.alert_sound
                )
                self.is_idle = True
                self.warning_given = False

            self._set_status("Distracted")

        elif inactive_for > self.idle_warning_time and not self.warning_given:
            self._notify(
                "Still focusing?",
                "Move mouse or press key to stay focused.",
                self.warning_sound
            )
            self.warning_given = True

        else:
            self._set_status("Focused")