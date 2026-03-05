# SmartFocus – AI Assisted Study Focus Monitoring System

SmartFocus is an **AI-assisted study focus monitoring system** developed as a **Final Year Major Project** for the **Bachelor of Computer Applications (BCA)** program under the **NEP curriculum**.

The system helps students maintain concentration during study sessions by **monitoring focus behavior in real time**, detecting distractions, and generating analytical reports that help users understand and improve their study habits.

SmartFocus supports **both camera-based and non-camera-based monitoring**, making it flexible, privacy-friendly, and suitable for different learning environments.

---

# Academic Information

**Program:** Bachelor of Computer Applications (BCA)  
**Project Type:** Final Year Major Project  
**Institution:** Institute of Technology and Management  
**Department:** Information Technology  

---

# Team Members

- **Srijan Poudel**
- **Robin Singh Rana**
- **Priyanshu**
- **Priyanshu T. Negi**

---

# Problem Statement

Students frequently struggle to maintain sustained concentration while studying due to distractions such as:

- Social media
- Multitasking
- Mobile phone usage
- Lack of supervision

Most productivity tools only track time and **do not verify whether the user is actually focused**.

SmartFocus addresses this issue by providing:

- Real-time focus monitoring
- Presence verification
- Distraction detection
- Intelligent alert mechanisms
- Detailed focus analytics

This enables students, teachers, and parents to **better understand study behavior and productivity patterns**.

---

# Target Users

SmartFocus is designed primarily for **students and learners who are actively building technical skills through focused practice**.

Typical users include:

- Programming and software development learners
- Students preparing for coding interviews
- Data science and machine learning learners
- Competitive programming practitioners
- Online course learners

These users often spend long hours practicing on platforms such as:

- LeetCode
- HackerRank
- GeeksforGeeks
- Kaggle
- GitHub
- Online learning platforms

SmartFocus helps them maintain discipline by monitoring focus during practice sessions and preventing distractions such as social media or unrelated browsing.

---

# Project Objectives

The primary objectives of SmartFocus are:

- To monitor and analyze student focus behavior in real time
- To support both **camera-based** and **activity-based** focus tracking
- To implement goal-based presence and distraction alerts
- To generate analytical reports for productivity insights
- To assist students and educators in improving study discipline

---

# Key Features

## User Management
- Student registration system
- Secure login and authentication
- Session history tracking

---

# Focus Tracking Modes

## Camera Mode

Camera-based monitoring uses computer vision to determine whether the user is attentive.

Features:

- Live webcam feed processing
- Face detection and tracking
- Eye and head movement monitoring
- Real-time focus status detection

---

## No-Camera Mode

A lightweight and privacy-friendly tracking system.

Features:

- Keyboard activity tracking
- Mouse activity tracking
- Idle detection
- Presence verification

This mode ensures focus monitoring without requiring a webcam.

---

# Goal-Based Focus System

Users define a study goal before starting a session.

Example:

```
Goal Time: 1 Hour
```

SmartFocus dynamically adapts its monitoring logic based on the selected goal duration.

---

# Intelligent Alert System

## Presence Check Alert

Triggered when **50% of the goal duration is completed**.

Purpose:
- Verify that the student is still present and engaged in the study session.

---

## Distraction Alert

Triggered only if:

- The user ignores the presence check
- The system detects prolonged inactivity

This prevents unnecessary interruptions and ensures alerts occur only when required.

---

## Focus Restored Notification

Triggered when the user resumes activity.

The system automatically:

- Clears distraction state
- Resumes focus tracking
- Prevents repeated alerts

---

# Reports and Analytics

SmartFocus generates detailed productivity reports including:

- Session-wise focus logs
- Weekly focus summaries
- Monthly performance analysis
- Focus consistency heatmap
- Visual graphs representing study trends

These analytics help users identify patterns and improve study discipline.

---

# System Workflow

1. User Registration  
2. User Login  
3. Dashboard Access  
4. Set Study Goal  
5. Select Focus Mode (Camera / No-Camera)  
6. Start Focus Session  
7. Presence Check at 50% of Goal  
8. Distraction Alert if Inactive  
9. Focus Restored → Continue Session  
10. Session Ends  
11. Focus Analytics Generated  

---

# Technology Stack

## Backend
- Python
- Flask

## Frontend
- HTML
- CSS
- JavaScript

## Focus Tracking
- OpenCV
- Mediapipe
- pynput

## Data Storage
- CSV based logging system

## Visualization
- Matplotlib

## Notifications
- Plyer

## Audio Alerts
- Pygame

---

# Installation Guide

## 1️⃣ Create Virtual Environment

```
python -m venv venv
```

## 2️⃣ Activate Environment

Windows:

```
venv\Scripts\activate
```

## 3️⃣ Install Dependencies

```
pip install -r requirements.txt
```

## 4️⃣ Run the Application

```
python app.py
```

## 5️⃣ Open in Browser

```
http://127.0.0.1:5000
```

---

# Future Enhancements

Potential improvements include:

- Machine learning based attention prediction
- Mobile application version
- Cloud database integration
- Real-time parental dashboard
- Emotion detection and fatigue monitoring

---

# Conclusion

SmartFocus demonstrates how **real-time monitoring, computer vision, and behavioral analytics** can be integrated to address modern study distraction challenges.

The system provides a scalable and practical solution that promotes disciplined study habits while giving students meaningful insights into their productivity and focus patterns.