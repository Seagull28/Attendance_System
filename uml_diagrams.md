# UML Diagrams for Face Recognition Attendance System

## 1. Use Case Diagram

```
+---------------------------------------------+
|                                             |
|        Face Recognition Attendance System   |
|                                             |
+---------------------------------------------+
                    |
        +-----------+-----------+
        |                       |
    +---+----+             +----+---+
    | Student |             |  Admin  |
    +---+----+             +----+---+
        |                       |
        |                       |
+-------+-------+      +--------+--------+
|               |      |                 |
| - View        |      | - Capture Face  |
|   Dashboard   |      |                 |
| - View        |      | - Manage        |
|   Attendance  |      |   Students      |
|   Report      |      |                 |
| - View        |      | - Manage        |
|   Profile     |      |   Subjects      |
|               |      |                 |
| - View        |      | - Manage        |
|   Timetable   |      |   Departments   |
|               |      |                 |
| - Change      |      | - Manage        |
|   Password    |      |   Sections      |
|               |      |                 |
|               |      | - Scan          |
|               |      |   Attendance    |
|               |      |                 |
|               |      | - Generate      |
|               |      |   Reports       |
|               |      |                 |
+---------------+      +-----------------+
```

## 2. Class Diagram

```
+-------------------+       +-------------------+       +-------------------+
|     Department    |       |      Section      |       |      Student      |
+-------------------+       +-------------------+       +-------------------+
| - code: int       |       | - name: char      |       | - user: User      |
| - name: char      |<----->| - department: FK  |<----->| - name: char      |
| - description: text|       | - capacity: int   |       | - roll_number: char|
+-------------------+       | - year: int       |       | - department: FK  |
                            +-------------------+       | - year: int       |
                                                        | - section: FK     |
                                                        | - face_encoding: bin|
                                                        +-------------------+
                                                                |
                                                                |
                                                                v
+-------------------+       +-------------------+       +-------------------+
|      Subject      |       |    Attendance     |       | AttendanceReport  |
+-------------------+       +-------------------+       +-------------------+
| - name: char      |       | - student: FK     |       | - student: FK     |
| - code: char      |<----->| - subject: FK     |<----->| - subject: FK     |
| - department: FK  |       | - date: date      |       | - total_classes: int|
| - year: int       |       | - time: time      |       | - classes_attended: int|
| - section: FK     |       | - present: bool   |       | - month: int      |
+-------------------+       +-------------------+       | - year: int       |
        |                                               +-------------------+
        |
        v
+-------------------+
|     TimeTable     |
+-------------------+
| - subject: FK     |
| - day_of_week: int|
| - start_time: time|
| - end_time: time  |
+-------------------+
```

## 3. Activity Diagram - Attendance Marking Process

```
        +---------------------+
        |     Start System    |
        +----------+----------+
                   |
                   v
        +---------------------+
        |  Check TimeTable    |
        |  for Current Day    |
        +----------+----------+
                   |
                   v
        +---------------------+
        | Is Class Scheduled? |
        +----------+----------+
                   |
          +--------+--------+
          |                 |
          v                 v
+-------------------+ +-------------------+
|       No          | |       Yes         |
|  Class Today      | |                   |
+-------------------+ +--------+----------+
                               |
                               v
                    +-------------------+
                    | Is Current Time   |
                    | Within 10-min     |
                    | Window?           |
                    +--------+----------+
                              |
                    +---------+---------+
                    |                   |
                    v                   v
          +-------------------+ +-------------------+
          |        No         | |       Yes         |
          |                   | |                   |
          +-------------------+ +--------+----------+
                                         |
                                         v
                                +-------------------+
                                | Start Webcam and  |
                                | Capture Frames    |
                                +--------+----------+
                                         |
                                         v
                                +-------------------+
                                | Detect Faces in   |
                                | Frame             |
                                +--------+----------+
                                         |
                                         v
                                +-------------------+
                                | Compare with      |
                                | Known Encodings   |
                                +--------+----------+
                                         |
                                         v
                                +-------------------+
                                | Student Found?    |
                                +--------+----------+
                                         |
                              +----------+-----------+
                              |                      |
                              v                      v
                +-------------------+     +-------------------+
                |        No         |     |       Yes         |
                |                   |     |                   |
                +-------------------+     +--------+----------+
                                                    |
                                                    v
                                           +-------------------+
                                           | Mark Attendance   |
                                           | as Present        |
                                           +--------+----------+
                                                    |
                                                    v
                                           +-------------------+
                                           | Update Attendance |
                                           | Report            |
                                           +--------+----------+
                                                    |
                                                    v
                                           +-------------------+
                                           | Continue for 60s  |
                                           | or Until Stopped  |
                                           +--------+----------+
                                                    |
                                                    v
                                           +-------------------+
                                           | Mark Remaining    |
                                           | Students Absent   |
                                           +--------+----------+
                                                    |
                                                    v
                                           +-------------------+
                                           |    End Process    |
                                           +-------------------+
```

## 4. State Diagram - Attendance Record

```
                    +-------------------+
                    |     Initialized   |
                    |   (No Attendance) |
                    +--------+----------+
                             |
                             | [Class Scheduled]
                             v
                    +-------------------+
                    |    Pending        |
                    | (Waiting for      |
                    |  Attendance)      |
                    +--------+----------+
                             |
              +--------------|---------------+
              |              |               |
              v              v               v
+-------------------+ +----------------+ +-------------------+
|     Present       | |    Absent     | |    Not Marked     |
| (Face Recognized) | | (Not Present  | | (Outside Window)  |
|                   | |  in Window)   | |                   |
+--------+----------+ +--------+------+ +-------------------+
         |                     |
         +----------+---------+
                    |
                    v
         +-------------------+
         |     Recorded      |
         | (In Database)     |
         +--------+----------+
                  |
                  | [Month End]
                  v
         +-------------------+
         |     Reported      |
         | (In Monthly       |
         |  Report)          |
         +-------------------+
```

## 5. Component Diagram

```
+---------------------------------------------------------------------+
|                      Face Recognition Attendance System              |
+---------------------------------------------------------------------+
|                                                                     |
|  +----------------+      +----------------+     +----------------+   |
|  |                |      |                |     |                |   |
|  |  Authentication|<---->|  Web Interface |<--->| Face Recognition|  |
|  |  Component     |      |  Component     |     | Component      |   |
|  |                |      |                |     |                |   |
|  +-------+--------+      +-------+--------     +-------+--------+   |
|          ^                       ^                     ^            |
|          |                       |                     |            |
|          v                       v                     v            |
|  +-------+--------+      +-------+--------+    +-------+--------+   |
|  |                |      |                |    |                |   |
|  | User Management|<---->|  Attendance    |<-->| Report Generation|  |
|  | Component      |      |  Component     |    | Component       |   |
|  |                |      |                |    |                |   |
|  +-------+--------+      +-------+--------+    +----------------+   |
|          ^                       ^                                  |
|          |                       |                                  |
|          v                       v                                  |
|  +-------+--------+      +-------+--------+                         |
|  |                |      |                |                         |
|  |  Department &  |<---->|   Timetable    |                         |
|  |  Section Mgmt  |      |   Component    |                         |
|  |                |      |                |                         |
|  +----------------+      +----------------+                         |
|                                                                     |
+---------------------------------------------------------------------+
```

## 6. Deployment Diagram

```
+-------------------+                  +-------------------+
|   Client Device   |                  |   Web Server      |
+-------------------+                  +-------------------+
| - Web Browser     |<---------------->| - Django App      |
|                   |    HTTPS         | - Channels        |
+-------------------+                  | - ASGI            |
                                       +--------+----------+
                                                |
                                                |
                                                v
                                       +-------------------+
                                       |   Database Server |
                                       +-------------------+
                                       | - PostgreSQL/     |
                                       |   SQLite          |
                                       | - Student Data    |
                                       | - Attendance Data |
                                       +--------+----------+
                                                |
                                                |
                                                v
                                       +-------------------+
                                       |  Webcam Device    |
                                       +-------------------+
                                       | - Camera          |
                                       | - Face Recognition|
                                       |   Processing      |
                                       +-------------------+
```