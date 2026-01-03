import cv2

cap = cv2.VideoCapture(0) #0 means default camera

while True:
    ret,frame = cap.read()
    '''Ye camera se ek single frame (image) capture karta hai. 'ret' ek boolean (True/False) deta hai — agar camera frame mila to True, warna False. 'frame' me image data aata hai (matrix form me).'''
    if not ret:   #if false
        print("Camera not detected!")
        break

    cv2.imshow("Live Feed",frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()