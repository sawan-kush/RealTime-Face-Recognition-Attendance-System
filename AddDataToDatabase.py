import os

from supabase import create_client
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

# 🔌 Create connection
supabase = create_client(url, key)

# 📦 Data to insert
data =[{
    "student_id": "0808CL23",
    "name": "Shraddha Khapra",
    "major": "CSE-AIML",
    "starting_year": 2023,
    "total_attendance": 6,
    "standing": "G",
    "year": 3,
    "last_attendance_time": "2023-12-11 00:54:34"
},
{
    "student_id": "0808CL24",
    "name": "Sawan Kushwah",
    "major": "CSE-AIML",
    "starting_year": 2023,
    "total_attendance": 9,
    "standing": "E",
    "year": 3,
    "last_attendance_time": "2023-10-11 00:54:34"
},
{
    "student_id": "0808CL54",
    "name": "Yashwardhan Rathore",
    "major": "CSE-AIML",
    "starting_year": 2023,
    "total_attendance": 12,
    "standing": "A+",
    "year": 3,
    "last_attendance_time": "2023-9-11 00:54:34"
}]

# 📤 Insert into database
response = supabase.table("RealTimeAttendance").insert(data).execute()

# 🖨️ Print response
print(response)