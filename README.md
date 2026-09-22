# Smart Attendance System Using Face Recognition

An intelligent desktop-based attendance management system that automates student attendance using **facial recognition**. The system combines face detection, facial recognition, student management, attendance tracking, database integration, and model evaluation in a user-friendly interface.

## 📌 Overview

The **Smart Attendance System** is designed to reduce manual attendance work and improve the efficiency of attendance management. The system captures student faces through a webcam, identifies registered students, and records their attendance with the date and time.

The project initially uses traditional computer vision techniques such as **Haar Cascade face detection and LBPH face recognition**, with **FaceNet-based deep learning evaluation** included to explore improved recognition performance.

## ✨ Features

* 🔐 Administrator login
* 👨‍🎓 Student registration and management
* 📷 Real-time face detection using webcam
* 🧠 Face recognition using LBPH
* 🤖 FaceNet-based recognition evaluation
* 📝 Automatic attendance recording
* ⏱️ Date and time-based attendance tracking
* 🚫 Duplicate attendance prevention
* 🗄️ MySQL database integration
* 📊 Attendance report generation
* 📄 CSV-based attendance export
* 🔍 Model performance evaluation
* 📈 Confusion matrix and evaluation metrics
* ⚠️ Camera and database error handling
* 🖥️ Windows desktop application

## 🛠️ Technologies Used

| Category                | Technologies        |
| ----------------------- | ------------------- |
| Programming Language    | Python              |
| GUI                     | Tkinter             |
| Computer Vision         | OpenCV              |
| Face Detection          | Haar Cascade        |
| Face Recognition        | LBPH, FaceNet       |
| Database                | MySQL               |
| Data Processing         | NumPy, Pandas       |
| Model Evaluation        | Scikit-learn        |
| Visualization           | Matplotlib, Seaborn |
| Development Environment | VS Code             |
| Version Control         | Git & GitHub        |

## 🏗️ System Modules

The application consists of six major modules:

1. **Student Management** – Add, update, delete, and manage student records.
2. **Face Data Collection** – Capture student facial images through a webcam.
3. **Face Recognition** – Detect and identify registered students.
4. **Attendance Management** – Record attendance with date and time.
5. **Model Training & Evaluation** – Train the recognition model and evaluate its performance.
6. **Reports** – View and export attendance information.

## 🔄 System Workflow

```text
Administrator Login
        ↓
Student Registration
        ↓
Capture Face Images
        ↓
Train Recognition Model
        ↓
Start Face Recognition
        ↓
Identify Student
        ↓
Check Duplicate Attendance
        ↓
Record Attendance
        ↓
Store in MySQL Database
        ↓
Generate Attendance Report
```

## 🧠 Face Recognition Approach

### LBPH

The primary recognition system uses **Local Binary Pattern Histogram (LBPH)**. It is suitable for a lightweight CPU-based attendance application and provides fast face recognition without requiring a GPU.

### FaceNet Evaluation

A FaceNet-based deep learning approach was also evaluated to investigate the use of deep facial embeddings.

A FaceNet forward pass takes approximately **0.2 seconds on the CPU test hardware**. To maintain a responsive live video feed, recognition can be performed periodically rather than on every frame.

This provides a practical trade-off between recognition performance and real-time responsiveness.

## 📊 Model Evaluation

The project includes an evaluation script:

```text
evaluate_model.py
```

The evaluation includes:

* Accuracy
* Precision
* Recall
* F1-score
* Confusion matrix
* Threshold sensitivity analysis

Generated evaluation outputs include:

```text
confusion_matrix.png
metrics_table.csv
threshold_sensitivity.png
```

## 🗄️ Database

The system uses **MySQL** for storing student and attendance information.

Typical student information includes:

```text
Student ID
Roll Number
Name
Department
```

Attendance records include:

```text
Student ID
Name
Date
Time
Subject
```

> **Note:** Database credentials should be stored securely using environment variables or a configuration file when deploying the system in a production environment.

## 💻 Installation

### 1. Clone the repository

```bash
git clone https://github.com/Prathibha2306/Attendance-System-using-Face-Recognition.git
```

### 2. Navigate to the project

```bash
cd Attendance-System-using-Face-Recognition
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment on Windows

```powershell
venv\Scripts\activate
```

### 5. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

## ⚙️ Configuration

Before running the application:

1. Install **MySQL Server**.
2. Create the required database.
3. Create the required tables.
4. Configure the database connection in the application.
5. Connect a working webcam.
6. Ensure the required Haar Cascade file is available.

For security, avoid committing database passwords or other credentials to GitHub.

## ▶️ Running the Application

After activating the virtual environment and configuring MySQL, run:

```powershell
python main.py
```

For model evaluation:

```powershell
python evaluate_model.py
```

## 📁 Project Structure

```text
Attendance-System-using-Face-Recognition/
│
├── main.py
├── login.py
├── register.py
├── student.py
├── attendance.py
├── train.py
├── face_recognition.py
├── databaseTest.py
├── evaluate_model.py
│
├── requirements.txt
├── README.md
├── DEEP_LEARNING_NOTES.md
│
├── haarcascade_frontalface_default.xml
│
├── confusion_matrix.png
├── threshold_sensitivity.png
├── metrics_table.csv
│
└── .gitignore
```

## 🔒 Privacy and Security

This project processes facial data for attendance identification. The repository does **not** include personal face images, generated facial embeddings, or attendance records.

For real-world deployment, additional security and privacy measures should be implemented, including:

* Secure credential management
* Encryption of sensitive data
* Access control
* Secure storage of biometric data
* Data retention policies
* User consent and privacy compliance

## ⚡ Requirements

* Windows OS
* Python 3.x
* Webcam
* MySQL Server
* Minimum 4 GB RAM recommended
* CPU-based execution supported
* No dedicated GPU required for the basic attendance system

## 🚀 Future Enhancements

* FaceNet/ArcFace-based recognition as the primary model
* Liveness detection to prevent photo-based spoofing
* Multi-camera support
* Mobile application for administrators
* Web-based attendance dashboard
* Cloud database integration
* Advanced attendance analytics
* Secure environment-based configuration
* Improved biometric privacy and encryption

## 🎯 Learning Outcomes

This project provided practical experience in:

* Computer vision
* Facial recognition
* Deep learning model evaluation
* Python application development
* Tkinter GUI development
* MySQL database integration
* Machine learning performance evaluation
* Git and GitHub
* Software modularity and maintainability

## 👩‍💻 Author

**Prathibha Naik**

Computer Science and Engineering
Sahyadri College of Engineering & Management, Mangaluru

GitHub: **Prathibha2306**

## 📜 License

This project is developed for **academic and educational purposes**.
