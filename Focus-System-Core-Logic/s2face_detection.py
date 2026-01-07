import cv2

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

cap = cv2.VideoCapture(0) #0 means default camera

while True:
    ret,frame = cap.read()
    '''Ye camera se ek single frame (image) capture karta hai. 'ret' ek boolean (True/False) deta hai — agar camera frame mila to True, warna False. 'frame' me image data aata hai (matrix form me).'''
    if not ret:   #if false
        print("Camera not detected!")
        break

    gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

    faces=face_cascade.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5,minSize=(50,50))

    for(x,y,w,h) in faces :
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)

    if len(faces)>0:
        cv2.putText(frame,"Focused",(50,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
    else:
        cv2.putText(frame,"Not Focused",(50,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)


    cv2.imshow("Face Detection",frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    

cap.release()
cv2.destroyAllWindows()


'''
cv2.CascadeClassifier() -Classifier Loader->Ye pre-trained model load karta hai jise OpenCV ne already train kiya hai face detect karne ke liye.
cv2.data.haarcascades-Data Path->Ye batata hai ki OpenCV ke system folder me haarcascade files kahan rakhi hain.
haarcascade_frontalface_default.xml-Haar Cascade Model->Ye XML file ek AI model jaisa hai jise thousands of face images par train kiya gaya hai. Ye face detect karne me help karta hai.
cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)-Convert Color->OpenCV by default images ko BGR format me rakhta hai. Face detection me grayscale fast aur accurate hota hai, isliye convert karte hain.
detectMultiScale() -Detection Function->Ye image ke andar multiple faces detect karta hai. Parameters:
	scaleFactor=1.1->Har frame ko thoda zoom karke detect karta hai — detection ko fine tune karta hai.
	minNeighbors=5-Detection confidence->higher value = less false detections.
	minSize=(50, 50)->Minimum face size — chhoti objects ignore karta hai.
for (x, y, w, h) in faces:	Loop ->	Har detected face ke coordinates milte hain — top-left (x, y) aur size (w, h).
cv2.rectangle()->Draw Rectangle->Frame ke upar green box draw karta hai. Parameters: (image, start_point, end_point, color, thickness)
cv2.waitKey(1)->Keyboard input ke liye 1 millisecond tak wait karta hai.'''