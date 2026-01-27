# SmartFocus – AI Assisted Study Focus Monitoring System

SmartFocus is a real-time study focus monitoring system developed as a Final Year Major Project for the Bachelor of Computer Applications (BCA) program under the NEP curriculum.

The system is designed to help students maintain concentration, track focus behavior, and reduce distractions during study sessions using both camera-based and non-camera-based monitoring techniques.

---

## Academic Details

Program: Bachelor of Computer Applications (BCA)  
Project Type: Final Year Major Project  
Institution: Institute of Technology and Management  
Department: Information Technology  

---

## Team Members

- Srijan Poudel  
- Robin Singh Rana  
- Priyanshu  
- Priyanshu T. Negi  

---

## Problem Statement

Students often struggle to maintain sustained focus while studying due to distractions such as mobile phones, multitasking, and lack of supervision.

Most traditional productivity tools only track time and do not actively monitor user presence or provide real-time feedback.

SmartFocus addresses this problem by:
- Actively monitoring user activity
- Detecting inactivity and absence
- Providing intelligent presence checks and distraction alerts
- Generating performance reports for self-analysis and parental review

---

## Objectives

- To monitor and analyze student focus behavior in real time  
- To support both camera-based and non-camera focus tracking  
- To provide goal-oriented presence and distraction alerts  
- To generate weekly and monthly focus reports  
- To notify parents about student focus performance  

---

## Key Features

### User Management
- Student registration system
- Secure login and logout
- Parent details linked with student accounts

---

## Focus Tracking Modes

### Camera Mode
- Live webcam feed
- Frame-by-frame focus analysis
- Real-time processing via backend

### No-Camera Mode
- Keyboard and mouse activity tracking
- Detects inactivity and distraction
- Lightweight and privacy-friendly

---

## Goal Based Focus System

- User sets goal time in hours and minutes
- Focus tracking adapts dynamically to goal duration
- Intelligent alert system based on progress

### Intelligent Alerts

#### Presence Check Alert
- Triggered once at 50% of the goal time
- Verifies whether the user is still actively present

#### Distraction Alert
- Triggered only if the user remains inactive after the presence check
- Prevents unnecessary alerts

#### Focus Restored Notification
- Displayed once the user resumes activity
- Clears distraction state automatically

The alert logic is carefully designed to avoid notification spam and simulate real-world human supervision.

---

## Reports and Analytics

- Session-wise focus logs
- Weekly focus summary
- Monthly performance report
- Visual graphs representing focus trends

---

## Parent Notification System

- Weekly focus report sent to parent via email
- Report includes:
  - Total focus time
  - Average daily focus
  - Goal achievement statistics

---

## System Workflow

User Registration  
↓  
User Login  
↓  
Dashboard  
↓  
Set Goal Time (Hours and Minutes)  
↓  
Select Mode (Camera or No-Camera)  
↓  
Focus Tracking Begins  
↓  
Presence Check at 50% of Goal  
↓  
If Absent → Distraction Alert  
↓  
If Refocused → Continue Session  
↓  
Session Ends  
↓  
Reports Generated  
↓  
Parent Email Notification  

---

## Focus and Alert Logic (Core Concept)

### Presence Check Logic
- Triggered once at 50% of the goal duration
- Checks whether the user is still actively interacting

### Distraction Detection
Activated only when:
- User ignores the presence check
- User remains inactive beyond the defined threshold

Internal state flags prevent repeated alerts.

### Focus Restoration
- Triggered on keyboard or mouse activity
- Distraction state is cleared
- Focus resumes normally
- No repeated alerts until the next checkpoint

This logic closely simulates real-world human supervision.

---

## Technology Stack

### Backend
- Python
- Flask

### Frontend
- HTML
- CSS
- JavaScript

### Focus Tracking
- OpenCV
- pynput

### Data Storage
- CSV files

### Visualization
- Matplotlib

### Notifications
- Plyer

### Audio Alerts
- Pygame

---

## How to Run the Project

### Step 1: Create Virtual Environment
python -m venv venv
### Step 2: Activate Environment
venv\Scripts\activate
### Step 3: Install Dependencies
pip install -r requirements.txt
### Step 4: Run the Application
python app.py
### Step 5: Open in Browser
http://127.0.0.1:5000

---

# Future Enhancements
- Machine learning based attention scoring
- Mobile application version
- Cloud database integration
- Real-time parent dashboard
- Emotion and eye-movement detection

---

# Conclusion
SmartFocus is a practical, scalable, and academically sound solution to modern study-related distraction problems.
The project successfully demonstrates the integration of real-time monitoring, user interaction tracking, and data-driven analytics into a unified system suitable for academic and real-world use