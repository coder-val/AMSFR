import cv2
import face_recognition
from django.conf import settings
from .faceRecognition import findEncodings
import os, numpy as np
from .attendance import mark_attendance
from .models import Schedule
import time

class VideoCamera(object):
    def __init__(self):
        time.sleep(5)
        self.video = cv2.VideoCapture(settings.CAMERA, cv2.CAP_DSHOW)
        # self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        # self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    def __del__(self):
        self.video.release()
    
    def get_frame(self, encodeListKnown, classNames):
        success, image = self.video.read()
        image = cv2.flip(image, 1)

        # print(encodeListKnown)

        if not len(encodeListKnown) == 0 and not Schedule.objects.filter(is_active=True).count() == 0:
            imgS = cv2.resize(image,(0,0), None, 0.25,0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
            facesCurFrame = face_recognition.face_locations(imgS)
            encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

            for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace, 0.7)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

                matchesIndex = np.argmin(faceDis)
                y1, x2, y2, x1 = faceLoc
                print(faceLoc)
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

                if matches[matchesIndex] and (faceDis[matchesIndex] < 0.4):
                    # name = classNames[matchesIndex].upper()
                    name = classNames[matchesIndex]
                    # print(name)
                    # cv2.rectangle(image,(x1, y1), (x2, y2+50), (0, 255, 0), 2)
                    # cv2.rectangle(image,(x1, y2), (x2, y2+50), (0, 255, 0), cv2.FILLED)
                    # cv2.putText(image, name[7:len(name)], (x1+6, y2+60), cv2.FONT_HERSHEY_COMPLEX, 1.5, (0,255,0), 3)
                    #cv2.putText(image, name.split('-')[2].upper(), (x1+6, y2+60), cv2.FONT_HERSHEY_COMPLEX, 1.2, (0,255,0), 3)
                    cv2.putText(image, name.split('_')[1].upper(), (x1+6, y2+60), cv2.FONT_HERSHEY_COMPLEX, 1.2, (0,255,0), 3)
                    # mark_attendance(option, name)
                    mark_attendance(name.split('_')[0])

                else:
                    cv2.putText(image, "unknown".upper(), (x1+6, y2+60), cv2.FONT_HERSHEY_COMPLEX, 1.5, (255,255,255), 3)

        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()


def gen(camera):
    image_path = os.path.join(settings.MEDIA_ROOT, "registered")
    images = []
    classNames = []
    if not os.path.exists(image_path):
        os.mkdir(image_path)
    myList = os.listdir(image_path)
    
    for cl in myList:
        curImg = cv2.imread(f'{image_path}/{cl}')
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])

    findEncodings(images)

    encodeListKnown = findEncodings(images)
    print('Encoding Complete')
    while True:
        frame = camera.get_frame(encodeListKnown, classNames)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
