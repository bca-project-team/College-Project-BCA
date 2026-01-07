import cv2
import mediapipe as mp #Google’s ML library for face/hand/body landmarks. We use face_mesh (468 landmarks).
import time

#importing mediapipe components
mp_face_mesh=mp.solutions.face_mesh
mp_drawing= mp.solutions.drawing_utils

#face mesh model initialize
face_mesh=mp_face_mesh.FaceMesh(refine_landmarks=True) #refine->useful for eye detection and blink detection later.
cap=cv2.VideoCapture(0)

focused_time=0
last_focus_time=None

while True:
    ret,frame=cap.read()
    if not ret:
        break

    #mirror view(natural camera look)
    frame=cv2.flip(frame,1) #Mirrors the frame horizontally so movement feels natural (like mirror). Optional.
    rgb_frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB) #OpenCV reads images in BGR order. Mediapipe expects RGB order. So we convert.

    #process the frame using mediapipe
    results = face_mesh.process(rgb_frame)

    focus_status='No Face Detected'

    #If face landmarks are found
    '''Draws the face contour landmarks on frame (visual aid). Two drawing specs passed:
       First is drawing spec for the landmarks (color green in code).
       Second is drawing spec for connections (color red).'''
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                face_landmarks,
                mp_face_mesh.FACEMESH_CONTOURS,
                mp_drawing.DrawingSpec(color=(0,255,0),thickness=1,circle_radius=1),
                mp_drawing.DrawingSpec(color=(0,0,255),thickness=1)
            )

            #eye landmark points
            '''Mediapipe uses fixed indices for facial points. Some commonly used:
             33 ≈ left eye outer corner
             263 ≈ right eye outer corner
             (Later we can use iris indices like 468..)
             Important: landmark.x is normalized in range [0.0, 1.0] relative to image width. Same for .y relative to image height.
             Example: left_eye_x = 0.35 means left eye is at 35% of the image width from the left.'''
            left_eye_x= face_landmarks.landmark[33].x
            right_eye_x= face_landmarks.landmark[263].x
            
            #focus logic(agar dono aankhon k beech distance normal range me hai)
            if abs(left_eye_x-right_eye_x)>0.35:
                '''If left_eye_x = 0.45 and right_eye_x = 0.55 → diff = 0.10 (small) → likely focused.
                   If left_eye_x = 0.20 and right_eye_x = 0.75 → diff = 0.55 (big) → not focused / big head turn.'''
                focus_status='Not focused'
            else:
                focus_status='Focused'

    if focus_status == "Focused":
        if last_focus_time is None:
            last_focus_time = time.time() # start counting
        else:
            diff = time.time() - last_focus_time
            focused_time += diff
            last_focus_time = time.time()
    else:
        last_focus_time = None 

    cv2.putText(frame, f"Status: {focus_status}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
    cv2.putText(frame, f"Focus Time: {int(focused_time)}s", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
    cv2.imshow('MediaPipe Focus Tracker', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()