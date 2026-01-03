import os
import csv
import datetime
import subprocess
import sys

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def log_session(name, goal_hours, mode):
    """Log session start in focus_report.csv"""
    file_exists = os.path.isfile("focus_report.csv")
    with open("focus_report.csv", "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Date", "User", "Goal (hrs)", "Mode", "Status"])
        writer.writerow([datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                         name, goal_hours, mode, "Started"])

def main():
    clear_screen()
    print("Welcome to SmartFocus: Smart Study Focus System\n")

    name = input("Enter your name: ").strip()
    goal_hours = input("Enter your daily focus goal (in hours): ").strip()

    clear_screen()
    print(f"Welcome, {name}! \n")
    print("Choose Mode:\n")
    print("1: Camera Focus Mode (Track eye and head movements & attention)")
    print("2: No-Camera Focus Mode (For phone distraction tracking)\n")

    mode_choice = input("Enter your choice (1 or 2): ").strip()

    if mode_choice == "1":
        log_session(name, goal_hours, "Camera Mode")
        print("\nLaunching Camera Focus Mode...")
        subprocess.run([sys.executable, r"C:\Users\Acer\Desktop\college-project\focus_system\s6focus_cam.py"])
    elif mode_choice == "2":
        log_session(name, goal_hours, "No-Camera Mode")
        print("\nLaunching No-Camera Focus Mode...")
        subprocess.run([sys.executable, "s7focus_nocam.py"])
    else:
        print("Invalid choice! Please restart.")

if __name__ == "__main__":
    main()
