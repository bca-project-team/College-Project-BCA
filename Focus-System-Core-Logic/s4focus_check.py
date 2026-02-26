import cv2
import time

# Haar Cascade models load karo
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")

cap = cv2.VideoCapture(0)
focused_time=0
last_focus_time = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Pehle face detect karo
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)
    focus_status = "No Face Detected"

    for (x, y, w, h) in faces:
        roi_gray = gray[y:y+h, x:x+w]      # ROI = Region of Interest
        roi_color = frame[y:y+h, x:x+w]
        eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 10, minSize=(30,30))
        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (255, 0, 0), 2)
        if len(eyes) >= 2:
            focus_status = "Focused"
        else:
            focus_status = "Eyes not visible "
        # Face ke around rectangle
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

     
    # ⏱️ Real-time focus timer logic
    if focus_status == "Focused":
        if last_focus_time is None:
            last_focus_time = time.time() # start counting
        else:
            diff = time.time() - last_focus_time
            focused_time += diff
            last_focus_time = time.time()
    else:
        last_focus_time = None  # reset when not focused

    # Display info
    cv2.putText(frame, f"Status: {focus_status}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
    cv2.putText(frame, f"Focus Time: {int(focused_time)}s", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
    cv2.imshow('Focus Tracker', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
