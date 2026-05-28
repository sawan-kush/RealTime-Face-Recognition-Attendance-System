import cv2
import face_recognition
import pickle
import os

from supabase import create_client

from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

# Importing students images
folderPath = 'Images'
pathList = os.listdir(folderPath)
print(pathList)
imgList = []
studentIds = []
for path in pathList:

    imgList.append(cv2.imread(os.path.join(folderPath,path)))
    studentIds.append(os.path.splitext(path)[0])

    # 📤 Upload image to Supabase Storage
    file_path = os.path.join(folderPath, path)

    with open(file_path, "rb") as f:
        supabase.storage.from_("student-images").upload(path,f) # filename in storage

print(len(imgList))
print(studentIds)


def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList

print("Encoding started...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown,studentIds]
print("Encoding Complete")

file = open("EnodeFile.p","wb")
pickle.dump(encodeListKnownWithIds,file)
file.close()
print("File Saved")

