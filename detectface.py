import cv2
faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
filename='4.mp4'
video_capture = cv2.VideoCapture(filename)
print video_capture.get(cv2.cv.CV_CAP_PROP_FPS)
i=0
while True:
	# Capture frame-by-frame
    i+=1
    print "d"
    ret, frame = video_capture.read()
    #ret is true if success
    print "f"
    if frame is None: break
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(
        frame,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.cv.CV_HAAR_SCALE_IMAGE
    )
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    cv2.imshow('Video', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):#press q to quit
        break
    print i
    #raw_input("Press Enter to continue...")'''
video_capture.release()
cv2.destroyAllWindows()

