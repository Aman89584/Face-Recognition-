import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://attendance-system-c19d0-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')

data = {
    "00001":
        {
            "Name":"Aman Tiwari",
            "Major":"CSE",
            "Starting_year":2022,
            "Total_attendance":6,
            "Standing":"A",
            "Year":4,
            "last_attendance_time":"2022-07-22 00:25:34"

        },
    "00002":
        {
            "Name":"Elon Musk",
            "Major":"Tesla",
            "Starting_year":2013,
            "Total_attendance":45,
            "Standing":"F",
            "Year":4,
            "last_attendance_time":"2022-07-22 00:25:34"
        },
    "00003":
        {
            "Name":"Mark",
            "Major":"Engineer",
            "Starting_year":2012,
            "Total_attendance":8,
            "Standing":"C",
            "Year":4,
            "last_attendance_time":"2022-07-22 00:25:34"
        },

}

for key,value in data.items():
    ref.child(key).set(value)
