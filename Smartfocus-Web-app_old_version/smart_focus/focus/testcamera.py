from smart_focus.focus.camera import CameraFocusTracker

tracker = CameraFocusTracker("TestUser", 0.01)
result = tracker.start()

print("\nSESSION SUMMARY")
print(result)