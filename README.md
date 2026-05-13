# 📋 Attendance Monitoring & Performance Analysis System

A web-based college attendance management system built with **Python Flask** and **SQLite**. It allows teachers to mark daily attendance, track student performance, and analyse trends through charts and reports.

---

## ✨ Features

| Module | Description |
|--------|-------------|
| **Dashboard** | At-a-glance stats — total students, subjects, today's presence count, overall attendance %, and a 7-day trend chart |
| **Students** | Add, view, and delete students (name, roll number, branch, semester) |
| **Subjects** | Add, view, and delete subjects with subject codes |
| **Mark Attendance** | Select a subject and date, then mark each student as Present or Absent with bulk "All Present / All Absent" shortcuts |
| **Performance Analysis** | Per-subject or overall report with attendance %, A+–F grades, Safe / Warning / Critical status, and a distribution doughnut chart |

---

## 🗂️ Project Structure

```
attendence_monitoring_system/
├── app.py               # Flask application & all routes
├── database.py          # SQLite initialisation, seed data & DB helper
├── requirements.txt     # Python dependencies
├── attendance.db        # SQLite database (auto-created on first run)
├── templates/
│   ├── base.html        # Shared sidebar layout (Bootstrap 5)
│   ├── index.html       # Dashboard
│   ├── students.html    # Student management
│   ├── subjects.html    # Subject management
│   ├── attendance.html  # Mark attendance
│   └── performance.html # Performance analysis
└── static/
    ├── css/style.css    # Custom styles
    └── js/main.js       # Sidebar toggle & alert auto-dismiss
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher

### Installation

1. **Clone / download the project**
   ```bash
   git clone <repo-url>
   cd attendence_monitoring_system
   ```

2. **Install dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python3 -m flask run
   ```

4. **Open in browser**
   ```
   http://127.0.0.1:5000
   ```

The SQLite database (`attendance.db`) is created automatically on first run and seeded with **5 sample students** and **5 subjects**.

---

## 📊 Performance Grading

| Attendance % | Grade | Status |
|---|---|---|
| ≥ 90% | A+ | ✅ Safe |
| 80 – 89% | A | ✅ Safe |
| 75 – 79% | B | ✅ Safe |
| 70 – 74% | B | ⚠️ Warning |
| 60 – 69% | C | ⚠️ Warning |
| 50 – 59% | D | 🔴 Critical |
| < 50% | F | 🔴 Critical |

> Students below **75%** are flagged as Warning or Critical as per standard college attendance policies.

---

## 🛠️ Tech Stack

- **Backend** — Python 3, Flask, SQLite3
- **Frontend** — Bootstrap 5, Bootstrap Icons, Chart.js
- **Database** — SQLite (file-based, zero configuration)

---

## 📸 Pages Overview

- **`/`** — Dashboard with summary cards and attendance trend graph
- **`/students`** — Manage student records
- **`/subjects`** — Manage subjects
- **`/attendance`** — Mark attendance for a subject on a specific date
- **`/performance`** — View detailed performance report with charts

---

## 📝 License

This project is developed as a college academic project and is free to use for educational purposes.
