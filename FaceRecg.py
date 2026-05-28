import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
from datetime import datetime
import requests

# =========================
# SUPABASE
# =========================

from supabase import create_client

from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

# =========================
# WEBCAM
# =========================

cap = cv2.VideoCapture(0)

cap.set(3, 640)
cap.set(4, 480)

# =========================
# BACKGROUND IMAGE
# =========================

imgBackground = cv2.imread('Resources/background.png')

# =========================
# LOAD MODE IMAGES
# =========================

folderModePath = 'Resources/Modes'

modePathList = os.listdir(folderModePath)

imgModeList = []

for path in modePathList:
    imgModeList.append(
        cv2.imread(os.path.join(folderModePath, path))
    )

# =========================
# LOAD ENCODE FILE
# =========================

print("Loading Encode File ...")

file = open('EnodeFile.p', 'rb')

encodeListKnownWithIds = pickle.load(file)

file.close()

encodeListKnown, studentIds = encodeListKnownWithIds

print("Encode File Loaded")

# =========================
# VARIABLES
# =========================

modeType = 0
counter = 0
id = -1
imgStudent = []
studentInfo = []

# Confidence threshold
THRESHOLD = 0.45

# =========================
# MAIN LOOP
# =========================

while True:

    success, img = cap.read()

    # Small image for faster processing
    imgS = cv2.resize(
        img,
        (0, 0),
        None,
        0.25,
        0.25
    )

    imgS = cv2.cvtColor(
        imgS,
        cv2.COLOR_BGR2RGB
    )

    # Detect faces
    faceCurFrame = face_recognition.face_locations(imgS)

    # Encode faces
    encodeCurFrame = face_recognition.face_encodings(
        imgS,
        faceCurFrame
    )

    # Place webcam feed
    imgBackground[
        162:162 + 480,
        55:55 + 640
    ] = img

    # Place mode image
    imgBackground[
        44:44 + 633,
        808:808 + 414
    ] = imgModeList[modeType]

    # =========================
    # FACE DETECTED
    # =========================

    if faceCurFrame:

        for encodeFace, faceLoc in zip(
                encodeCurFrame,
                faceCurFrame):

            matches = face_recognition.compare_faces(
                encodeListKnown,
                encodeFace
            )

            faceDis = face_recognition.face_distance(
                encodeListKnown,
                encodeFace
            )

            matchIndex = np.argmin(faceDis)

            # Debug distance
            print(faceDis[matchIndex])

            # =========================
            # STRONG MATCH ONLY
            # =========================

            if matches[matchIndex] and faceDis[matchIndex] < THRESHOLD:

                y1, x2, y2, x1 = faceLoc

                y1, x2, y2, x1 = (
                    y1 * 4,
                    x2 * 4,
                    y2 * 4,
                    x1 * 4
                )

                bbox = (
                    55 + x1,
                    162 + y1,
                    x2 - x1,
                    y2 - y1
                )

                imgBackground = cvzone.cornerRect(
                    imgBackground,
                    bbox,
                    rt=0
                )

                id = studentIds[matchIndex]

                if counter == 0:

                    cvzone.putTextRect(
                        imgBackground,
                        "Loading",
                        (275, 400)
                    )

                    cv2.imshow(
                        "Face Attendance",
                        imgBackground
                    )

                    cv2.waitKey(1)

                    counter = 1
                    modeType = 1

        # =========================
        # LOAD STUDENT DATA
        # =========================

        if counter != 0:

            if counter == 1:

                # Get student info
                response = supabase.table(
                    "RealTimeAttendance"
                ).select("*").eq(
                    "student_id",
                    id
                ).execute()

                studentInfo = response.data[0]

                print(studentInfo)

                # =========================
                # GET IMAGE
                # =========================

                image_url = supabase.storage.from_(
                    "student-images"
                ).get_public_url(
                    f"{id}.png"
                )

                img_response = requests.get(image_url)

                array = np.asarray(
                    bytearray(img_response.content),
                    dtype=np.uint8
                )

                imgStudent = cv2.imdecode(
                    array,
                    cv2.IMREAD_COLOR
                )

                # =========================
                # AUTO FACE CROP
                # =========================

                if imgStudent is not None:

                    imgRGB = cv2.cvtColor(
                        imgStudent,
                        cv2.COLOR_BGR2RGB
                    )

                    faces = face_recognition.face_locations(
                        imgRGB
                    )

                    if faces:

                        top, right, bottom, left = faces[0]

                        padding = 50

                        top = max(0, top - padding)

                        left = max(0, left - padding)

                        bottom = min(
                            imgStudent.shape[0],
                            bottom + padding
                        )

                        right = min(
                            imgStudent.shape[1],
                            right + padding
                        )

                        imgStudent = imgStudent[
                            top:bottom,
                            left:right
                        ]

                    imgStudent = cv2.resize(
                        imgStudent,
                        (216, 216)
                    )

                else:
                    print("Image not loaded")

                # =========================
                # ATTENDANCE UPDATE
                # =========================

                datetimeObject = datetime.strptime(
                    studentInfo['last_attendance_time'],
                    "%Y-%m-%dT%H:%M:%S"
                )

                secondsElapsed = (
                    datetime.now() - datetimeObject
                ).total_seconds()

                print(secondsElapsed)

                if secondsElapsed > 30:

                    new_attendance = (
                        studentInfo['total_attendance'] + 1
                    )

                    supabase.table(
                        "RealTimeAttendance"
                    ).update({

                        "total_attendance":
                            new_attendance,

                        "last_attendance_time":
                            datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"
                            )

                    }).eq(
                        "student_id",
                        id
                    ).execute()

                    studentInfo['total_attendance'] = (
                        new_attendance
                    )

                else:

                    modeType = 3
                    counter = 0

                    imgBackground[
                        44:44 + 633,
                        808:808 + 414
                    ] = imgModeList[modeType]

            # =========================
            # DISPLAY INFO
            # =========================

            if modeType != 3:

                if 10 < counter < 20:
                    modeType = 2

                imgBackground[
                    44:44 + 633,
                    808:808 + 414
                ] = imgModeList[modeType]

                if counter <= 10:

                    cv2.putText(
                        imgBackground,
                        str(studentInfo['total_attendance']),
                        (861, 125),
                        cv2.FONT_HERSHEY_COMPLEX,
                        1,
                        (255, 255, 255),
                        1
                    )

                    cv2.putText(
                        imgBackground,
                        str(studentInfo['major']),
                        (1006, 550),
                        cv2.FONT_HERSHEY_COMPLEX,
                        0.5,
                        (255, 255, 255),
                        1
                    )

                    cv2.putText(
                        imgBackground,
                        str(id),
                        (1006, 493),
                        cv2.FONT_HERSHEY_COMPLEX,
                        0.5,
                        (255, 255, 255),
                        1
                    )

                    cv2.putText(
                        imgBackground,
                        str(studentInfo['standing']),
                        (910, 625),
                        cv2.FONT_HERSHEY_COMPLEX,
                        0.6,
                        (100, 100, 100),
                        1
                    )

                    cv2.putText(
                        imgBackground,
                        str(studentInfo['year']),
                        (1025, 625),
                        cv2.FONT_HERSHEY_COMPLEX,
                        0.6,
                        (100, 100, 100),
                        1
                    )

                    cv2.putText(
                        imgBackground,
                        str(studentInfo['starting_year']),
                        (1125, 625),
                        cv2.FONT_HERSHEY_COMPLEX,
                        0.6,
                        (100, 100, 100),
                        1
                    )

                    # Center student name
                    (w, h), _ = cv2.getTextSize(
                        studentInfo['name'],
                        cv2.FONT_HERSHEY_COMPLEX,
                        1,
                        1
                    )

                    offset = (414 - w) // 2

                    cv2.putText(
                        imgBackground,
                        str(studentInfo['name']),
                        (808 + offset, 445),
                        cv2.FONT_HERSHEY_COMPLEX,
                        1,
                        (50, 50, 50),
                        1
                    )

                    # Place student image
                    imgBackground[
                        175:175 + 216,
                        909:909 + 216
                    ] = imgStudent

                counter += 1

                # Reset
                if counter >= 20:

                    counter = 0

                    modeType = 0

                    studentInfo = []

                    imgStudent = []

                    imgBackground[
                        44:44 + 633,
                        808:808 + 414
                    ] = imgModeList[modeType]

    # =========================
    # NO FACE
    # =========================

    else:

        modeType = 0
        counter = 0

    # =========================
    # SHOW WINDOW
    # =========================

    cv2.imshow(
        "Face Attendance",
        imgBackground
    )

    cv2.waitKey(1)


print("URL:", url)
print("KEY:", key)
