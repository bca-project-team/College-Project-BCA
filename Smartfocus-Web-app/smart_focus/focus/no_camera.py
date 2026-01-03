# smart_focus/focus/nocamera.py
import time
from smart_focus.focus.session import FocusSession

class NoCameraFocusTracker:
    """
    No-camera focus tracker using user activity simulation.
    Can later be connected to keyboard/mouse or web UI.
    """

    def __init__(self, user_name, goal_hours):
        self.session = FocusSession(
            user_name=user_name,
            goal_hours=goal_hours,
            mode="No-Camera"
        )

    def start(self):
        print("No-Camera Focus Session Started")
        print("Type 'f' for Focused, 'd' for Distracted, 'q' to quit\n")

        self.session.start()

        while True:
            user_input = input("Status (f/d/q): ").strip().lower()

            if user_input == 'f':
                self.session.update_status("Focused")
                print("✔ Focused")

            elif user_input == 'd':
                self.session.update_status("Distracted")
                print("✖ Distracted")

            elif user_input == 'q':
                self.session.stop()
                break

            else:
                print("Invalid input")

        return self.session.summary()