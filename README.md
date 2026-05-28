# Real-Time Face Recognition Attendance System

A real-time Face Recognition Attendance System built using Python, OpenCV, face_recognition, and Supabase. The system detects and recognizes faces through a webcam feed, automatically marks attendance, and displays student information in a visually designed attendance panel created using PNG-based layouts.

## Features

* Real-time face detection and recognition
* Automatic attendance marking
* Duplicate attendance prevention using time threshold
* Supabase database integration
* Supabase Storage integration for student images
* Face encoding generation using `face_recognition`
* Confidence threshold to reduce false matches
* Automatic student image cropping and resizing
* Live webcam feed with attendance visualization
* Dynamic attendance counter updates

## Project Structure

### `FaceRecg.py`

Main recognition system that:

* Captures webcam feed
* Detects and recognizes faces
* Fetches student data from Supabase
* Updates attendance records
* Displays attendance information visually

### `EncodeGenerator.py`

Generates face encodings from student images and uploads images to Supabase Storage.

### `AddDataToDatabase.py`

Uploads student records and attendance-related information to the Supabase database.

## Technologies Used

* Python
* OpenCV
* face_recognition
* cvzone
* NumPy
* Supabase
* Requests
* python-dotenv

## How It Works

1. Student images are encoded and stored locally.
2. Webcam captures real-time video feed.
3. Faces are detected and compared with stored encodings.
4. Student details are fetched from Supabase.
5. Attendance is updated automatically.
6. Student information and image are displayed on the attendance screen.

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

Run the system:

```bash
python FaceRecg.py
```

## Notes

This project does not use a traditional GUI framework. The visual attendance interface is created using PNG-based layouts rendered with OpenCV.

## Future Improvements

* Multi-face attendance support
* Admin dashboard
* Cloud deployment
* Attendance analytics
* Better anti-spoofing detection

## Author

Sawan Kushwah

