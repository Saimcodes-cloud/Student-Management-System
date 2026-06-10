# 🎓 Student Management System
> A command-line based Student Management System built in **C++** for managing student records, courses, marks, and GPA/CGPA calculations.

---

## 📋 Table of Contents
- [About the Project](#about-the-project)
- [Features](#features)
- [Project Structure](#project-structure)
- [Classes Overview](#classes-overview)
- [Getting Started](#getting-started)
- [Usage / Commands](#usage--commands)
- [Data File Formats](#data-file-formats)
- [GPA & CGPA Calculation](#gpa--cgpa-calculation)
- [Grading System](#grading-system)
- [Design Patterns Used](#design-patterns-used)
- [Technologies Used](#technologies-used)

---

## 📖 About the Project

This is a **C++ command-line application** that serves as a backend engine for a Student Management System. It reads and writes data from plain text files and exposes a set of commands that can be called from the terminal (or from a Python frontend via `subprocess`).

It was built as a semester project for **BSc Computer Engineering 2025**.

---

## ✨ Features

- ✅ Add, Update, and Delete student records
- ✅ Store and update marks for multiple courses and semesters
- ✅ Auto-calculate grades based on marks
- ✅ Calculate **GPA** per semester and **CGPA** overall
- ✅ View full result card for any student
- ✅ View overall statistics (top student, average CGPA, pass rate)
- ✅ Persistent data storage via text files
- ✅ Designed with **OOP principles** and **Design Patterns**

---

## 📁 Project Structure

```
├── main.cpp              # Main source file (all logic)
├── data/
│   ├── students.txt      # Student records
│   ├── courses.txt       # Course information
│   └── marks.txt         # Student marks
└── README.md
```

---

## 🏗️ Classes Overview

| Class | Purpose |
|---|---|
| `Student` | Stores student info (roll, name, gender, CNIC, contact, father) |
| `Course` | Stores course info (semester, code, name, credits, teacher) |
| `Marks` | Stores marks and calculates total, percentage, grade, grade points |
| `GradeCalculator` | Abstract base class for GPA calculators |
| `GpaCalculator` | Calculates GPA for a single semester |
| `CgpaCalculator` | Calculates CGPA across all semesters |
| `Command` | Abstract base class for all commands (Command Pattern) |
| `GetStudentsCommand` | Lists all students with CGPA |
| `GetMarksCommand` | Gets marks for a student in a semester |
| `GetGpaCommand` | Gets GPA/CGPA for a student |
| `UpdateMarksCommand` | Adds or updates marks |
| `AddStudentCommand` | Adds a new student |
| `UpdateStudentCommand` | Updates existing student info |
| `DeleteStudentCommand` | Deletes student and their marks |
| `GetStatsCommand` | Shows overall system statistics |
| `GetResultCommand` | Shows full result card for a student |

---

## 🚀 Getting Started

### Prerequisites
- g++ compiler (C++17 or later)
- Linux / macOS / Windows (with MinGW)

### Compilation

```bash
g++ -std=c++17 -o sms main.cpp
```

### Run

```bash
./sms <COMMAND> [arguments...]
```

---

## 💻 Usage / Commands

### Get All Students
```bash
./sms GET_STUDENTS
```
Output: `ROLL|NAME|GENDER|CONTACT|FATHER|CGPA`

---

### Get Marks (for a student in a semester)
```bash
./sms GET_MARKS <ROLL> <SEMESTER>
```
Example:
```bash
./sms GET_MARKS 2025-CE-01 SEM1
```
Output: `COURSE|Q1|Q2|MID|FINAL|ASSIGN|TOTAL|GRADE|PERCENTAGE`

---

### Get GPA / CGPA
```bash
./sms GET_GPA <ROLL>
```
Output: `SEM1_GPA|SEM2_GPA|CGPA`

---

### Update / Add Marks
```bash
./sms UPDATE_MARKS <ROLL> <SEMESTER> <COURSE> <Q1> <Q2> <MID> <FINAL> <ASSIGN>
```
Example:
```bash
./sms UPDATE_MARKS 2025-CE-01 SEM1 CS101 8 9 25 40 10
```

---

### Add Student
```bash
./sms ADD_STUDENT <ROLL> <NAME> <GENDER> <CNIC> <CONTACT> <FATHER>
```
Example:
```bash
./sms ADD_STUDENT 2025-CE-05 "Ali Hassan" M 3520112345678 03001234567 "Hassan Ali"
```

---

### Update Student
```bash
./sms UPDATE_STUDENT <ROLL> <NAME> <GENDER> <CNIC> <CONTACT> <FATHER>
```

---

### Delete Student
```bash
./sms DELETE_STUDENT <ROLL>
```
> ⚠️ This also deletes all marks associated with the student.

---

### Get Statistics
```bash
./sms GET_STATS
```
Output includes: total students, average CGPA, top student, passing count, subject averages.

---

### Get Full Result Card
```bash
./sms GET_RESULT <ROLL>
```
Output includes: student info, semester-wise GPA, all course marks, and CGPA.

---

## 📄 Data File Formats

### `data/students.txt`
```
# Format: ROLL|NAME|GENDER|CNIC|CONTACT|FATHER_NAME
2025-CE-01|Ali Hassan|M|3520112345678|03001234567|Hassan Ali
```

### `data/courses.txt`
```
# Format: SEMESTER|CODE|NAME|TH_CREDITS|LAB_CREDITS|TEACHER
SEM1|CS101|Programming Fundamentals|3|1|Dr. Ahmad
```

### `data/marks.txt`
```
# Format: ROLL|SEMESTER|COURSE|Q1|Q2|MID|FINAL|ASSIGN
2025-CE-01|SEM1|CS101|8|9|25|40|10
```

> Lines starting with `#` are treated as comments and are ignored.

---

## 📊 GPA & CGPA Calculation

```
GPA = Σ(Grade Points × Course Credits) / Σ(Course Credits)
```

**Example:**
| Course | Grade | Points | Credits | Weighted |
|--------|-------|--------|---------|----------|
| CS101  | A+    | 4.0    | 4       | 16.0     |
| MATH101| B+    | 3.5    | 3       | 10.5     |
| **Total** | | | **7** | **26.5** |

**GPA = 26.5 / 7 = 3.79**

**CGPA** is calculated the same way but across **all semesters**.

---

## 🏅 Grading System

| Marks (%) | Grade | Grade Points |
|-----------|-------|--------------|
| 85 – 100  | A+    | 4.0          |
| 80 – 84   | A     | 4.0          |
| 75 – 79   | B+    | 3.5          |
| 70 – 74   | B     | 3.0          |
| 65 – 69   | C+    | 2.5          |
| 60 – 64   | C     | 2.0          |
| 55 – 59   | D+    | 1.5          |
| 50 – 54   | D     | 1.0          |
| Below 50  | F     | 0.0          |

---

## 🧠 Design Patterns Used

### 1. Command Pattern
Each operation (GET_STUDENTS, UPDATE_MARKS, etc.) is encapsulated in its own class that inherits from the abstract `Command` base class. This makes adding new commands easy without modifying existing code.

### 2. Polymorphism (Virtual Functions)
`GradeCalculator` is an abstract class with a pure virtual `calculate()` function. `GpaCalculator` and `CgpaCalculator` each implement it differently.

### 3. RAII with Smart Pointers
Commands are stored as `unique_ptr<Command>` — memory is automatically managed, no manual `delete` needed.

---

## 🛠️ Technologies Used

- **Language:** C++17
- **Paradigm:** Object-Oriented Programming (OOP)
- **File I/O:** `ifstream` / `ofstream`
- **STL Used:** `vector`, `map`, `string`, `algorithm`, `memory`, `sstream`
- **Build:** g++ compiler

---

## 👨‍💻 Author

**Muhammad Junaid Saleem**
**Muhammad Saim Imran**
BSc Computer Engineering – 2025
