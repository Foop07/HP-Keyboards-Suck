import threading
import time
import keyboard
import os
import sys
import logging
import pystray
from pystray import MenuItem as item, Icon
from PIL import Image, ImageDraw

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s')

running = True
force_release_keys = ['/', 's']  # Press '/' or 'S' to release 'W'
restart_flag = True  # Ensures program does not restart when quitting manually

def force_release_w():
    while running:
        time.sleep(0.1)

def restart_program():
    global running, restart_flag
    if not restart_flag:
        return  # Prevent restart if quitting manually
    
    logging.debug("Restarting program...")
    running = False  # Ensure all threads exit cleanly
    time.sleep(2)  # Allow time for cleanup
    python = sys.executable
    os.execl(python, python, *sys.argv)

def restart_threads():
    global running
    while running:
        logging.debug("Starting force release thread...")
        thread = threading.Thread(target=force_release_w)
        thread.daemon = True
        thread.start()
        
        time.sleep(180)  # Restart every 3 minutes
        if not restart_flag:
            break  # If quitting manually, break loop
        
        logging.debug("Restarting threads...")
        running = False
        thread.join()
        running = True
        restart_program()

def on_key_press(event):
    global running, restart_flag
    if event.name in force_release_keys:
        logging.debug("Force-releasing W key.")
        keyboard.release('w')
        time.sleep(0.01)  # Small delay to allow re-registration
    elif event.name == 'q':  # Press 'Q' to quit
        running = False
        restart_flag = False  # Prevent further restarts
        logging.debug("Quit signal received. Exiting...")
        icon.stop()
        sys.exit()

def create_icon():
    image = Image.new('RGB', (64, 64), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.rectangle((16, 16, 48, 48), fill=(0, 0, 255))
    return image

def quit_application(icon, item):
    global running, restart_flag
    running = False
    restart_flag = False  # Stop auto-restarting
    icon.stop()
    sys.exit()

def setup_tray():
    menu = (item('Quit', quit_application),)
    global icon
    icon = Icon("Auto W Key Fix", create_icon(), menu=menu)
    icon.run()

keyboard.on_press(on_key_press)

# Start background threads
restart_thread = threading.Thread(target=restart_threads, daemon=True)
restart_thread.start()

# Run system tray icon
setup_tray()

logging.debug("Program exited after pressing 'Q'.")