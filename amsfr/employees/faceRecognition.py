import cv2, os, numpy as np, face_recognition, time, datetime
from django.conf import settings
from .models import Attendance
from django.contrib import messages
from .attendance import mark_attendance

cam = 0

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList

def checkIfExist(image):
    image_path = os.path.join(settings.BASE_DIR, "static/registered")
    images = []
    classNames = []
    myList = os.listdir(image_path)
    print(myList)
    
    for cl in myList:
        curImg = cv2.imread(f'{image_path}/{cl}')
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])

    findEncodings(images)

    encodeListKnown = findEncodings(images)
    print('Encoding Complete')

    # while True:
    result = None
    img = cv2.imread(image)
    imgS = cv2.resize(img,(0,0), None, 0.50,0.50)
    imS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        # matchesIndex = np.argmin(faceDis)
        y1, x2, y2, x1 = faceLoc
        # y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
        if len(images) == 0:
            cv2.putText(imgS, "GOOD!", (10, 50), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 3)
            result = False
        
        elif matches[np.argmin(faceDis)] and (faceDis[np.argmin(faceDis)] < 0.5):
            name = classNames[np.argmin(faceDis)].upper()
            cv2.putText(imgS, "NO GOOD!", (10, 50), cv2.FONT_HERSHEY_COMPLEX, 1.5, (0, 0, 255), 3)
            # print(name)
            # cv2.rectangle(imgS,(x1, y1), (x2, y2+50), (0, 255, 0), 2)
            # cv2.rectangle(imgS,(x1, y2), (x2, y2+50), (0, 255, 0), cv2.FILLED)
            # cv2.putText(imgS, name, (x1+6, y2+40), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,255), 2)
            result = True
        else:
            cv2.putText(imgS, "GOOD!", (10, 50), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 3)
            result = False
    winName = "Checking Image"
    cv2.namedWindow(winName)
    cv2.setWindowProperty(winName, cv2.WND_PROP_TOPMOST, 1)
    cv2.imshow(winName, imgS)

    cv2.waitKey(3000)
    # time.sleep(5)

    # if cv2.waitKey(1) & 0xFF == ord('\x1B'):
    #     break
    # if cv2.getWindowProperty('Check Image', cv2.WND_PROP_VISIBLE) <1:
    #     break
    
    cv2.destroyAllWindows()
    return result

def face_recog(option):
    # BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    # image_path = os.path.join(BASE_DIR, "capture\static\images")
    image_path = os.path.join(settings.MEDIA_ROOT, "registered")
    images = []
    classNames = []
    myList = os.listdir(image_path)
    
    for cl in myList:
        curImg = cv2.imread(f'{image_path}/{cl}')
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])

    findEncodings(images)

    encodeListKnown = findEncodings(images)
    print('Encoding Complete')

    cap = cv2.VideoCapture(cam)

    while True:

        if len(images) == 0:
            # print("NO IMAGES YET!")
            
            return False
            break


        success, img = cap.read()
        cv2.putText(img, datetime.datetime.now().time().strftime("%I:%M:%S%p"), (10,120), cv2.FONT_HERSHEY_COMPLEX, 2, (255,255,255), 1)
        
        imgS = cv2.resize(img,(0,0), None, 0.25,0.25)
        imS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        if option == 1 or option == 3:
            cv2.putText(img, "TIME IN", (10,60), cv2.FONT_HERSHEY_COMPLEX, 2, (0,255,0), 3)
        elif option == 2 or option == 4:
            cv2.putText(img, "TIME OUT", (10,60), cv2.FONT_HERSHEY_COMPLEX, 2, (0,255,0), 3)

        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)


        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print(faceDis) #///////////////////
            matchesIndex = np.argmin(faceDis)
            y1, x2, y2, x1 = faceLoc
            # print(faceLoc)q
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

            if matches[matchesIndex] and (faceDis[matchesIndex] < 0.5):
                name = classNames[matchesIndex].upper()
                print(name)
                cv2.rectangle(img,(x1, y1), (x2, y2+50), (0, 255, 0), 2)
                cv2.rectangle(img,(x1, y2), (x2, y2+50), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, name, (x1+6, y2+40), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,255), 2)
                mark_attendance(option, name)

            else:
                cv2.putText(img, "unknown", (x1+6, y2-6), cv2.FONT_HERSHEY_COMPLEX, .5, (255,255,255), 1)

        if option == 1 or option == 2:
            windowName = "Attendance Check (AM)"
        elif option == 3 or option == 4:
            windowName = "Attendance Check (PM)"
            
        cv2.namedWindow(windowName, cv2.WINDOW_FULLSCREEN)
        cv2.resizeWindow(windowName, 1280, 720)
        cv2.imshow(windowName, img)
        # cv2.waitKey(1)
        if cv2.waitKey(1) & 0xFF == ord('\x1B'):
            break

    cap.release()
    cv2.destroyAllWindows()