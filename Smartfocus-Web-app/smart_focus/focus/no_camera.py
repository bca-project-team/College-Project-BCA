import time 
import os
import threading
from pynput import keyboard, mouse
import pygame
from plyer import notification

from smart_focus.focus.session import FocusSession


class NoCameraFocusTracker:
    """
    No-Camera Focus Tracker (Web-Friendly)
    - Keyboard & mouse inactivity
    - Alerts / notifications
    - Stop safely via tracker.stop()
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
        self.session = FocusSession(
            user_name=user_name,
            goal_hours=goal_hours,
            mode="No-Camera"
        )

        pygame.mixer.init()

        # --- Config ---
        self.idle_limit = idle_limit
        self.idle_warning_time = idle_warning_time
        self.alert_sound = alert_sound
        self.warning_sound = warning_sound

        # --- State ---
        self.last_activity_time = time.time()
        self.is_idle = False
        self.warning_given = False
        self.idle_time = 0
        self.start_time = None

        # --- Listeners ---
        self.keyboard_listener = None
        self.mouse_listener = None

        # --- Thread-safe stop ---
        self.stop_event = threading.Event()

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
            except Exception as e:
                print(f"(Sound error: {e})")
        threading.Thread(target=_play, daemon=True).start()

    def _notify(self, title, message, sound=None):
        if self.stop_event.is_set():  # ⛔ Stop guard
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
            print("\n✔ Focus Restored")
            self._notify("Focus Restored", "Good job! You're back on track.")
            time.sleep(1)
        self.is_idle = False
        self.warning_given = False

    # ---------------------------
    # Start / Stop
    # ---------------------------
    def start(self):
        print("🧠 No-Camera Focus Session Started")
        print("Tracking keyboard & mouse activity…")

        self.session.start()
        self.start_time = time.time()
        self.last_activity_time = time.time()
        self.stop_event.clear()

        # Start listeners
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
        except KeyboardInterrupt:
            print("\nSession interrupted manually.")

        self._cleanup()
        return self.session.summary()
    
    def stop(self):
        """Stop tracker immediately."""
        self.stop_event.set()   # ✅ stops loop
        self.session.stop()     # ✅ stops FocusSession

    def _cleanup(self):
        """Stop listeners cleanly."""
        for listener in [self.keyboard_listener, self.mouse_listener]:
            if listener:
                listener.stop()
        print("\n✅ Focus session ended cleanly.")

    # ---------------------------
    # Core focus logic
    # ---------------------------
    def _update_state(self):
        if self.stop_event.is_set():  # ⛔ Stop guard
            return

        now = time.time()
        inactive_for = now - self.last_activity_time

        if inactive_for > self.idle_limit:
            if not self.is_idle:
                print("\n⚠ Distraction Detected!")
                self._notify(
                    "Distraction Alert!",
                    "You've been idle for a while. Refocus!",
                    self.alert_sound
                )
                self.is_idle = True
                self.warning_given = False
            self.session.update_status("Distracted")
            self.idle_time += 1

        elif inactive_for > self.idle_warning_time and not self.warning_given:
            print("\n⏳ Are you still there?")
            self._notify(
                "Still focusing?",
                "Move your mouse or press any key to stay focused.",
                self.warning_sound
            )
            self.warning_given = True

        else:
            self.session.update_status("Focused")
