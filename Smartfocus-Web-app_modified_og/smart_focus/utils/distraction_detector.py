import threading
import time
import pygetwindow as gw


#  Always Blocked Platforms
SOCIAL_KEYWORDS = [
    "facebook",
    "instagram",
    "twitter",
    "tiktok"
]

# ⏱ Auto stop after 30 sec continuous distraction
DISTRACTION_THRESHOLD = 30


class DistractionDetector:

    def __init__(self, tracker):
        self.tracker = tracker
        self.running = False
        self.distraction_time = 0
        self.started_at=None
        self.GRACE_PERIOD=5

    def start(self):
        if self.running:
            return
        self.running=True
        self.distraction_time=0
        self.started_at=time.time()
        thread = threading.Thread(target=self._monitor, daemon=True)
        thread.start()
        
    def stop(self):
        self.running = False

    def _monitor(self):
        while self.running and self.tracker.running:
            print("Distraction time : ",self.distraction_time)
            time.sleep(2)
            if time.time()-self.started_at<self.GRACE_PERIOD:
                continue

            try:
                window = gw.getActiveWindow()
                if not window:
                    continue

                title = window.title.lower()
                print('Title:',title)

                # 🔥 Safely get activity & topic
                activity = getattr(self.tracker, "activity", "").lower()
                topic = getattr(self.tracker, "topic", "").lower()

                distracted = False

                # ==================================================
                # 🚫 SOCIAL MEDIA (Always Blocked)
                # ==================================================
                if any(word in title for word in SOCIAL_KEYWORDS):
                    distracted = True

                # ==================================================
                # 🎥 YOUTUBE SMART LOGIC
                # ==================================================
                elif "youtube" in title:
                    title=title.lower()
                    topic_words=topic.lower().split()
                    if "shorts" in title:
                        distracted=True
                    # If activity is NOT youtube study → block
                    elif "youtube" not in activity:
                        distracted = True
                        # If topic words not found in title → block
                    elif any(word in title for word in topic_words):
                        distracted = False

                    else:
                        distracted=True

                # ==================================================
                # ✅ UPDATE STATUS
                # ==================================================
                if distracted:
                    self.distraction_time += 2
                    self.tracker.session.update_status("Distracted")
                else:
                    self.distraction_time = 0
                    self.tracker.session.update_status("Focused")

                # ==================================================
                # 🚨 AUTO STOP SESSION
                # ==================================================
                if self.distraction_time >= DISTRACTION_THRESHOLD and not getattr(self.tracker,"auto_stopped",False):
                    print("⚠ Auto-stopping session due to distraction")

                    self.tracker.auto_stopped = True
                    result=self.tracker.stop()
                    from flask import current_app 
                    current_app.config["SESSION_RESULT"]=result

                    self.running = False
                    break

            except Exception:
                pass