import cv2
import mediapipe as mp
import time
import math
import csv
from datetime import datetime

mp_face_mesh = mp.solutions.face_mesh
face_mesh=mp_face_mesh.FaceMesh(refine_landmarks=True)
mp_drawing = mp.solutions.drawing_utils

cap=cv2.VideoCapture(0)

focused_time=0.0
last_focus_time=None
blink_count=0
blink_start = None  #jab aankh band hone laga tab ka time (start of closure).
blink_logged=False #ek blink ko ek baar hi count karne ke liye flag (prevent multiple counts while eyes still closed).
focus_status = 'No Face Detected !'

def euclidean(p1,p2):
    return math.sqrt((p1.x-p2.x)**2+(p1.y-p2.y)**2)

while True:
    ret,frame=cap.read()
    if not ret:
        break

    frame=cv2.flip(frame,1)
    rgb_frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        face=results.multi_face_landmarks[0] #first face
        h,w,_=frame.shape

        #left_eye landmarks(mediapipe indexes)
        top=face.landmark[159]
        bottom=face.landmark[145]
        left=face.landmark[33]
        right=face.landmark[133]

        #Compute Eye Aspect Ratio(EAR)
        ver = euclidean(top,bottom)
        hor = euclidean(left,right)
        EAR = ver/hor

        #Determine blink/open eyes
        eyes_open = EAR>0.22

        # --- Blink / Eye Closed Logic ---
        if not eyes_open:
            if blink_start is None:
                blink_start = time.time()
                blink_logged = False
            else:
                closed_duration = time.time() - blink_start

                # Eye fully closed for more than 1.0 sec
                if closed_duration > 1.0:
                    focus_status = f"Eyes Closed {closed_duration:.1f}s"
                    blink_logged = True  # prevent continuous update
                # Blink Detected (short closure)
                elif 0.1 < closed_duration <= 0.4 and not blink_logged:
                    blink_count += 1
                    focus_status = "Blink Detected"
                    blink_logged = True
        else:
            # Eyes Open again
            if blink_start is not None:
                blink_start = None
                blink_logged = False
            if "Eyes Closed" not in focus_status and "Blink" not in focus_status:
                focus_status = "Focused"  
        #print(f"EAR={EAR:.3f}, eyes_open={eyes_open}, blinks={blink_count}, status={focus_status}")
        print(f"EAR={EAR:.3f}, eyes_open={eyes_open}, status={focus_status}")


        #Direction/head facing check (outer-eye diff)

        left_eye_x=face.landmark[33].x
        right_eye_x=face.landmark[263].x
        horizontal_diff=abs(left_eye_x-right_eye_x)
        #print(f"horizontal_diff={horizontal_diff:.3f}")

        
        if eyes_open and "Closed" not in focus_status and "Blink" not in focus_status:
               if horizontal_diff > 0.13:
                    focus_status = "Focused"
               else:
                    focus_status = "Not Focused"

    else:
        focus_status="No Face Detected !"

    if focus_status == "Focused":
        if last_focus_time is None:
            last_focus_time = time.time() # start counting
        else:
            diff = time.time() - last_focus_time
            focused_time += diff
            last_focus_time = time.time()
    else:
        last_focus_time = None 

    hours = int(focused_time // 3600)
    minutes = int((focused_time % 3600) // 60)
    seconds = int(focused_time % 60)

    cv2.putText(frame, f"Status: {focus_status}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
    display_time = f"{hours}h {minutes}m {seconds}s"
    cv2.putText(frame, f"Focus Time: {display_time}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
    # cv2.putText(frame, f"Focus Time: {int(focused_time)}s", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
    #cv2.putText(frame, f"Blinks : {blink_count}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2)
    cv2.imshow('Focus with Blink Tracker', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

with open("focus_report.csv","a",newline="")as f:
    writer = csv.writer(f)
    writer.writerow([
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        f"{hours}h {minutes}m {seconds}s",
        #f" Blinks : {blink_count} "
    ])

cap.release()
cv2.destroyAllWindows()
print("Session saved to focus_report.csv")
