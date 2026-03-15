# Attendance Management System with Webcam

A bulk face-recognition attendance system using Python and MongoDB Atlas.

---

## Features

- Register students by scanning their face live via webcam
- Take bulk attendance — detects multiple faces simultaneously
- View attendance by date
- Export attendance to CSV or Excel
- Full present/absent report per day
- All data stored in MongoDB Atlas (cloud)

---

## Requirements

- Windows 10/11
- Python 3.11 — download from https://www.python.org/downloads/
- A webcam
- Internet connection (for MongoDB Atlas)

---

## Setup (First Time)

### Step 1 — Clone or extract the project
```
git clone <repo-url>
cd Attendance-Management-System-with-Web-Cam
```

### Step 2 — Install dlib (must be done before other packages)
```
pip install https://github.com/z-mahmud22/Dlib_Windows_Python3.x/raw/main/dlib-19.24.1-cp311-cp311-win_amd64.whl
```

### Step 3 — Install all dependencies
```
pip install -r requirements.txt
```

### Step 4 — Configure MongoDB
Create a `.env` file in the project root:
```
MONGO_URI=mongodb+srv://<db_user>:<password>@cluster0.eygg9lq.mongodb.net/attendance_db
```
Replace `<db_user>` and `<password>` with your MongoDB Atlas credentials.

> Make sure your IP address is whitelisted in MongoDB Atlas under Network Access.

### Step 5 — Run
```
python main.py
```

---

## Using the EXE (No Python needed)

If you have the pre-built `AttendanceSystem.exe`:

1. Place the `AttendanceSystem.exe` in a folder
2. Create a `.env` file in the **same folder** as the exe:
```
MONGO_URI=mongodb+srv://<db_user>:<password>@cluster0.eygg9lq.mongodb.net/attendance_db
```
3. Double-click `AttendanceSystem.exe` or run from terminal:
```
AttendanceSystem.exe
```

> The `data/exports/` folder will be created automatically for CSV/Excel exports.

---

## Menu Options

| Option | Description |
|--------|-------------|
| 1 | Register new student via live face scan |
| 2 | Start webcam attendance session |
| 3 | View all registered students |
| 4 | View attendance for any date |
| 5 | Export attendance to CSV or Excel |
| 6 | Full present/absent report for any date |
| 7 | Exit |

---

## How Registration Works

1. Enter student name and ID
2. Webcam opens — look directly at the camera
3. System auto-captures 5 face samples
4. Face encoding is saved to MongoDB Atlas
5. Done — student can now be recognized during attendance

---

## How Attendance Works

1. Start attendance session (Option 2)
2. Students walk in front of the webcam
3. System detects and recognizes faces in real time
4. Each student is marked present once per day
5. Records saved instantly to MongoDB Atlas
6. Press Q to end the session

---

## Project Structure

```
├── main.py           # Main menu
├── register.py       # Student face registration
├── attendance.py     # Live webcam attendance
├── db.py             # MongoDB connection
├── .env              # Your MongoDB credentials (never share this)
├── requirements.txt  # Python dependencies
└── data/
    └── exports/      # Exported CSV and Excel files
```

---

## Sharing with Others

- Share the `.exe` + a `.env` file with the MongoDB credentials
- Or share the full project folder and have them follow the Setup steps above
- Since the database is on MongoDB Atlas, all machines share the same student and attendance data


## OR YOU CAN DOWNLOAD IT FROM HERE

```
https://drive.google.com/file/d/1gqOmxFr03X9HfgF5yeLUkI8kAYxBZA9I/view?usp=sharing
```
