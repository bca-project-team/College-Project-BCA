import os
import csv
import datetime
import subprocess
import re
import time

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

def read_focus_time():
    '''Read the latest focus duration from focus_report.csv'''
    if not os.path.exists("focus_report.csv"):
        return 0
    
    with open("focus_report.csv",'r')as f:
        reader=list(csv.reader(f))
        if len(reader)<2:
            return 0
        
        # Reverse iterate to find latest duration line (e.g. "0h 1m 4s" in column 1)
        for row in reversed(reader):
            # Check all cells in the row for a duration pattern
            for cell in row:
                if isinstance(cell, str) and "h" in cell and "m" in cell and "s" in cell:
                    match = re.search(r'(\d+)h\s*(\d+)m\s*(\d+)s', cell)
                    if match:
                        h, m, s = map(float, match.groups())
                        return h + (m / 60) + (s / 3600)
        return 0

def log_final_report(name,goal_hours,mode,achieved_hours):
    result="Achieved" if (achieved_hours + 0.001) >=float(goal_hours) else "Not Achieved"
    file_exists=os.path.isfile("full_focus_report.csv")
    with open("full_focus_report.csv","a",newline="")as f:
        writer=csv.writer(f)
        if not file_exists:
            writer.writerow(["Date","User","Goal(hrs)","Achieved hours" ,"Mode","Result"])
        writer.writerow([datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),name,goal_hours,round(achieved_hours,4),mode,result])
    
    print("\n Final report saved in full_focus_report.csv ")
    print(f"User : {name}")
    print(f"Mode : {mode}")
    print(f"Goal : {goal_hours} hr")
    print(f"Focused : {round(achieved_hours,4)} hours")
    print(f"Result : {result}")

def main():
    clear_screen()
    print("-"*50)
    print("Welcome to SmartFocus: Smart Study Focus System")
    print("-"*50)

    name = input("Enter your name: ").strip()
    if not name:
        name="Unknown_user"

    print("Enter the focus/study time")
    hr=int(input("Enter hour : "))
    mins=int(input("Enter minutes : "))
    s=int(input("Enter sec : "))
    print(f"Your total study time = {hr}h:{mins}m:{s}s") 
    total_sec = hr*60*60 + mins*60 + s
    time.sleep(3)

    while True:
        try:
            goal_hours = round(total_sec/3600,4)
            break
        except ValueError:
            print("Please enter a valid numbers for hours ! ")

    clear_screen()
    print(f"Welcome, {name}! \n")
    print("Choose Mode:\n")
    print("1: Camera Focus Mode (Track eye and head movements & attention)")
    print("2: No-Camera Focus Mode (For phone distraction tracking)\n")

    mode_choice = input("Enter your choice (1 or 2): ").strip()

    if mode_choice == "1":
        log_session(name, goal_hours, "Camera Mode")
        print("\nLaunching Camera Focus Mode...")
        subprocess.run(["python", r"C:\Users\Acer\Desktop\college-project\focus_system\s6focus_cam_mod.py"])
        achieved=read_focus_time()
        log_final_report(name,goal_hours,"Camera Mode",achieved)

    elif mode_choice == "2":
        log_session(name, goal_hours, "No-Camera Mode")
        print("\nLaunching No-Camera Focus Mode...")
        subprocess.run(["python",r"C:\Users\Acer\Desktop\college-project\focus_system\s7.2focus_nocam.py"])
        achieved=read_focus_time()
        log_final_report(name,goal_hours,"Off-Camera Mode",achieved)

    else:
        print("Invalid choice! Please restart.")

if __name__ == "__main__":
    main()
