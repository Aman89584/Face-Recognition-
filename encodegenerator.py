import os
import cv2
import face_recognition
import pickle
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://attendance-system-c19d0-default-rtdb.firebaseio.com/",
    'storageBucket':"attendance-system-c19d0.appspot.com"
})
#Importing Student Images



folder_path = 'images'
mode_path = os.listdir(folder_path)
print(mode_path)
img_list = []
student_ids = []

for path in mode_path:
    img_list.append(cv2.imread(os.path.join(folder_path,path)))
    student_ids.append(os.path.splitext(path)[0])
    fileName = f'{folder_path}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)


    #print(os.path.splitext(path)[0])
#print(len(img_list))
print(student_ids)


def find_encoding (image_list):
    encode_list = []

    for img in image_list:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encode_list.append(encode)
    return encode_list

print("Encoding started.... ")
encode_list_known = find_encoding(img_list)
encode_list_known_with_ids = [encode_list_known,student_ids]
#print(encode_list_known)
print("Encoding successfully done")



file = open("EncodeFile.p",'wb')
pickle.dump(encode_list_known_with_ids, file)
file.close

print("Successfully Completed")
