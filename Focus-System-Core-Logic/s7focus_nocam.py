import time
import csv
import datetime
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def log_session(duration_sec):
    """Save session duration to focus_report.csv (for main.py to read)"""
    file_exists = os.path.isfile("focus_report.csv")
    with open("focus_report.csv", "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Date", "Focus Time"])
        
        hours = int(duration_sec // 3600)
        minutes = int((duration_sec % 3600) // 60)
        seconds = int(duration_sec % 60)
        display_time = f"{hours}h {minutes}m {seconds}s"

        writer.writerow([
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            display_time
        ])
    print(f"\n🧾 Session saved: {display_time}")

def main():
    clear_screen()
    print("No-Camera Focus Mode")
    print("-----------------------------")
    print("Press ENTER when you start focusing.")
    input()
    clear_screen()
    print("Focus session started! (Press Ctrl+C to stop)\n")

    start_time = time.time()
    idle_time = 0
    last_activity = time.time()
    while True:
       time.sleep(5)  # check every 5 seconds (simulate distraction check)
    
       user_input = input("Were you focusing? (y/n or q to quit): ").strip().lower()
    
       if user_input == 'q':
         print("\n✅ Session ended by user.")
         break
    
       elif user_input == 'n':
         print("Distraction detected! Refocus yourself.")
         idle_time += 5
    
       elif user_input == 'y':
         last_activity = time.time()
    
       else:
         print("Invalid input! Please enter y, n, or q.")
         continue

       focused_time = time.time() - start_time - idle_time
       h = int(focused_time // 3600)
       m = int((focused_time % 3600) // 60)
       s = int(focused_time % 60)
       print(f"Current Focus Time: {h}h {m}m {s}s\n")
    log_session(focused_time)
main()