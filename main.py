import os
import pickle
import cv2
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import numpy as np
from datetime import datetime

#storing value in database in realtime


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://attendance-system-c19d0-default-rtdb.firebaseio.com/",
    'storageBucket':"attendance-system-c19d0.appspot.com"
})
bucket = storage.bucket()






cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

im_background = cv2.imread('resources/background.png')


#importing the mode images into a list

folder_mode_path = 'resources/Modes'
mode_path = os.listdir(folder_mode_path)
img_mode_list = []
for path in mode_path:
    img_mode_list.append(cv2.imread(os.path.join(folder_mode_path,path)))

#print(len(img_mode_list))

#load the encoding file

print("Loading Encoded File... ")
file = open('EncodeFile.p','rb')
encode_list_known_with_ids = pickle.load(file)
file.close()
encode_list_known,student_ids = encode_list_known_with_ids
print(student_ids)
print("Encoded file Loaded")



modeType = 0
counter = 0
id = -1
imgStudent = []


# for the webcam process

while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0,0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)


    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)


    im_background[162:162+480,55:55+640] = img
    im_background[44:44+633, 808:808+414] = img_mode_list[modeType]
    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encode_list_known, encodeFace)
            FaceDis = face_recognition.face_distance(encode_list_known, encodeFace)
            #print("matches", matches)
            #print("face_dis", FaceDis)

            matchIndex = np.argmin(FaceDis)
            #print("Match Index", matchIndex)

            if matches[matchIndex]:
                # print("Known Faces Detected")
                # print(student_ids[matchIndex])
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55+x1 , 162+y1, x2-x1, y2-y1
                im_background = cvzone.cornerRect(im_background,bbox,rt=0)
                id = student_ids[matchIndex]
                if counter == 0:
                    cvzone.putTextRect(im_background,"Loading",(227,400))
                    cv2.imshow("face Attendance", im_background)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1
        if counter != 0:

            if counter == 1 :
                # Get the Data
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)
                # Get the Image from the storage
                blob = bucket.get_blob(f'images/{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array,cv2.COLOR_BGRA2BGR)
                #update data of attendance
                datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],
                                                  "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now()-datetimeObject).total_seconds()
                print(secondsElapsed)
                if secondsElapsed > 30:



                    ref = db.reference(f'Students/{id}')
                    studentInfo['Total_attendance'] += 1
                    ref.child('Total_attendance').set(studentInfo['Total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    im_background[44:44 + 633, 808:808 + 414] = img_mode_list[modeType]


            if modeType != 3:
                if 10<counter<20:
                   modeType = 2
                im_background[44:44 + 633, 808:808 + 414] = img_mode_list[modeType]

                if counter <= 10:

                    cv2.putText(im_background,str(studentInfo['Total_attendance']),(861,125),
                                cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)
                    cv2.putText(im_background, str(studentInfo['Major']), (1006, 550),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(im_background, str(id), (1006, 493),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(im_background, str(studentInfo['Standing']), (910, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (20, 20, 20), 1)
                    cv2.putText(im_background, str(studentInfo['Year']), (1025, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (20, 20, 20), 1)
                    cv2.putText(im_background, str(studentInfo['Starting_year']), (1125, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (20, 20, 20), 1)


                    (w, h), _ = cv2.getTextSize(studentInfo['Name'],cv2.FONT_HERSHEY_COMPLEX,1,1)
                    offset = (414 -w)//2
                    cv2.putText(im_background, str(studentInfo['Name']), (808+offset, 445),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (20, 20, 20), 1)

                    im_background[175:175+216,909:909+216] = imgStudent


                counter += 1

                if counter>= 20 :
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = []
                    im_background[44:44 + 633, 808:808 + 414] = img_mode_list[modeType]
    else:
        modeType=0
        counter = 0


    #cv2.imshow("web_cam", img)
    cv2.imshow("face Attendance",im_background)
    cv2.waitKey(1)