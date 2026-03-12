# Face Recognition Attendance System

An automated attendance management system that identifies students using
facial recognition and records attendance automatically.

The system captures faces using a camera, detects and recognizes
multiple students simultaneously, and updates attendance records in real
time. The platform also includes an administrative dashboard, attendance
analytics, and automated reporting.

------------------------------------------------------------------------

# Features

-   Student face capture using browser webcam
-   Automatic attendance marking using facial recognition
-   Multi-face recognition (detects several students in a single frame)
-   Admin dashboard for managing students, departments, subjects, and
    timetables
-   Student portal for viewing attendance records
-   Real-time updates using WebSockets
-   Automated attendance report generation
-   Centralized attendance database

------------------------------------------------------------------------

# System Architecture

![System Architecture](images/system_architecture.png)

### Interface Layer

**Student Portal** - Allows students to view attendance history and
statistics

**Admin Portal** - Manage students - Manage subjects - Manage
departments - Manage timetables - Generate attendance reports

------------------------------------------------------------------------

### Recognition System

The recognition system processes camera input and identifies students.

Components:

-   **Camera System**
    -   Captures classroom images
-   **Recognition Module**
    -   Uses the `face_recognition` library with dlib embeddings
-   **Image Processing Unit**
    -   Detects faces and compares them with stored encodings

Recognized students are automatically marked present.

------------------------------------------------------------------------

### Data Storage

**Attendance Database**

Stores:

-   Student details
-   Facial encodings
-   Attendance records
-   Subject and timetable data

------------------------------------------------------------------------

### Reporting Module

Generates:

-   Student attendance summaries
-   Subject-wise attendance reports
-   Historical attendance logs

------------------------------------------------------------------------

# System Workflow

1.  A student appears in front of the classroom camera.
2.  The camera captures a frame.
3.  Face detection identifies all faces in the frame.
4.  Facial embeddings are generated.
5.  Encodings are matched with the database.
6.  Recognized students are marked present.
7.  Attendance records are stored.
8.  Dashboards are updated.

------------------------------------------------------------------------

# Demo

## Real-Time Face Recognition

![Demo](images/attendance_demo.png)

### Detection Indicators

-   Green boxes → Recognized students
-   Red boxes → Unknown faces

Each recognized face is labeled with the student roll number.

------------------------------------------------------------------------

# Example Execution Output

    Today is Thursday, current time: 09:36:39
    Found 6 classes scheduled for today
    Checking class 301B from 09:30 to 10:30
    Starting webcam to capture frames...
    Marked Present: 2451-23-748-301
    Marked Present: 2451-23-748-303

------------------------------------------------------------------------

# Classroom-Scale Design

The system was designed to scan an entire classroom at once and mark
attendance automatically.

Due to prototype hardware limitations it currently uses a webcam, but it
can still detect and recognize multiple faces in a single frame.

Future setups can use:

-   Wide-angle classroom cameras
-   Multiple camera feeds
-   Distributed recognition nodes

------------------------------------------------------------------------

# Project Impact

-   Reduces manual attendance time by 80--90%
-   Saves 6--9 minutes per class
-   Eliminates paper registers
-   Provides centralized digital attendance records

------------------------------------------------------------------------

# Setup

## 1. Create Virtual Environment

``` bash
python -m venv venv
venv\Scripts\activate
```

## 2. Install Dependencies

``` bash
pip install -r requirements.txt
```

## 3. Apply Migrations

``` bash
python manage.py migrate
```

## 4. Create Admin User

``` bash
python manage.py createsuperuser
```

## 5. Run Server

``` bash
python manage.py runserver
```

------------------------------------------------------------------------

# Future Improvements

-   Multi-camera classroom support
-   Mobile application integration
-   Cloud deployment
-   Advanced attendance analytics

------------------------------------------------------------------------

# License

MIT License
