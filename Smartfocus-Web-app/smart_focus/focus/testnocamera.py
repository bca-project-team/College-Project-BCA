from smart_focus.focus.no_camera import NoCameraFocusTracker

tracker = NoCameraFocusTracker("TestUser", 0.01)
result = tracker.start()

print("\nSESSION SUMMARY")
print(result)