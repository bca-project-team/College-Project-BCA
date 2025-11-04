import time
import csv
import datetime
import os
from pynput import keyboard,mouse

idle_limit=10 #seconds after which we mark as distracted
is_idle=False
last_activity = time.time()
stop_requested = False

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def on_activity(_):
    global last_activity,is_idle
    last_activity=time.time()
    if is_idle:
        print("\n Back to Focus Mode !")
        is_idle=False

def on_key_press(key):
    global stop_requested
    try:
        if key.char and key.char.lower() == 'q':
            print("\n[q] detected — stopping session...")
            stop_requested = True
    except AttributeError:
        pass

#Keyboard and mouse listeners
keyboard_listener=keyboard.Listener(on_press=on_activity)
mouse_listener=mouse.Listener(on_move=on_activity,on_click=on_activity,on_scroll=on_activity)
keyboard_listener.start()
mouse_listener.start()
quit_listener = keyboard.Listener(on_press=on_key_press)
quit_listener.start()


def log_session(duration_sec,idle_time):
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
            display_time,
            f"Idle: {idle_time//60} m {idle_time%60} sec"
        ])
    print(f"\nSession saved: {display_time}")

def main():
    global last_activity, is_idle,stop_requested
    clear_screen()
    print("Off-Camera Focus Mode")
    print("-----------------------------")
    print("Press ENTER when you start focusing.")
    input()
    clear_screen()
    print("Focus session started! (Press q to stop)\n")

    start_time = time.time()
    idle_time = 0
    focused_time = 0 
    last_activity = time.time()
    while not stop_requested:
        time.sleep(1)
        now=time.time()
        inactive_for=now-last_activity

        if inactive_for > idle_limit:
            if not is_idle:
                print(f"\nDistraction Detected!")
                is_idle = True
            idle_time += 1

        
        elif is_idle:
            print("\n Back to Focus Mode !")
            is_idle = False         
             
        focused_time = time.time() - start_time - idle_time
        h = int(focused_time // 3600)
        m = int((focused_time % 3600) // 60)
        s = int(focused_time % 60)
        status = "IDLE" if is_idle else "FOCUSED"
        print(f"\rCurrent Focus Time: {h}h {m}m {s}s | Status: {status}", end="")


    print("\n\nSession ended by user.")
    focused_time = (time.time() - start_time) - idle_time
    log_session(focused_time,idle_time)
main()