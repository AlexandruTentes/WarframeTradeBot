import GUI
import threading
import time
import globals
import configs

global_data = globals.Globals()
gui = GUI.GUI()
config = configs.Configs()

def cmd():
    while global_data.program_running:
        command = input(">> ")

        command.strip()
        msg_data = command.split()

        if len(msg_data) == 1:
            if msg_data[0] in ("stop", "exit", "close"):
                global_data.program_running = False

# Read config file at runtime thread
config_thread = threading.Thread(target = config.read_config_runtime, args=(global_data.config_path,))
config_thread.daemon = True
config_thread.start()

# Refresh item frames real-time
items_thread = threading.Thread(target = gui.search_items_priority, args=())
items_thread.daemon = True
items_thread.start()

if config.config["toggleCMD"] == "on":
    # Command line thread
    thr = threading.Thread(target=cmd, args=())
    thr.daemon = True
    thr.start()

gui.window()
config.update_config(global_data.config_path + ".txt")
