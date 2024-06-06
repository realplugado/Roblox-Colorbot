from keyboard import is_pressed  # Library that relates to reading and writing keyboard inputs
from os import system, chdir
from os.path import dirname, join
import mss  # Takes screenshot. May change it to use Bettercam https://github.com/RootKit-Org/BetterCam in the future as that's much more efficient.
import configparser
from cv2 import dilate, threshold, findContours, RETR_EXTERNAL, CHAIN_APPROX_NONE, contourArea, cvtColor, COLOR_BGR2HSV, inRange, THRESH_BINARY  # examines screenshot
import numpy as np  # Works with CV2
import win32api  # Windows API that I just use for mouse button keybinds and mouse movement to an enemy
from threading import Thread
from colorama import Fore, Style  # Makes the colorful text in the console
from time import time, sleep, strftime, localtime  # Allows for specific time delays and such
import pygetwindow as gw  # Only takes screenshots when you're actually playing
from urllib.request import urlopen
from webbrowser import open as openwebpage
from math import sqrt
import sys
from keybinds import *
kernel = np.ones((3, 3), np.uint8)  # 3x3 array of 1s for structuring purposes
toggleholdmodes = ("Hold", "Toggle")  # this is a tuple of [0, 1] where hold is 0, toggle is 1.
# importing all the modules we need to run the code.

def log_error(error_message):
    timestamp = strftime('%Y-%m-%d %H:%M:%S', localtime())
    log_entry = f"{timestamp}: {error_message}\n"
    try:
        with open(error_log_path, 'a') as log_file:
            log_file.write(log_entry)
    except FileNotFoundError:
        with open(error_log_path, 'w') as log_file:
            log_file.write(log_entry)

try:  # if the user is running the exe, find the config and time they last opened the file relative to the exe, else do it relative to the .py file.
    if getattr(sys, 'frozen', False):
        application_path = dirname(sys.executable)
        config_file_path = join(application_path, 'word.exe.log')  # Changed to word.exe.log
        last_launch_path = join(application_path, 'lastlaunch.txt')
        error_log_path = join(application_path, "log.txt")
        chdir(application_path)
    else:
        script_directory = dirname(__file__)
        config_file_path = join(script_directory, "word.exe.log")  # Changed to word.exe.log
        last_launch_path = join(script_directory, "lastlaunch.txt")
        error_log_path = join(script_directory, "log.txt")
        chdir(script_directory)
except Exception as e:
    print(f"An error occurred checking if you're using the .py or the .exe: {e}")
    log_error(e)
    exit()

try:
    buffer = open(last_launch_path, "r")
    currenttime = time()
    if currenttime - float(buffer.read()) >= 17990:
        buffer2 = open(last_launch_path, "w+")
        buffer2.write(str(currenttime))
        buffer2.close()
        openwebpage("https://discord.gg/thunderclient")
        buffer.close()
except:
    buffer = open(last_launch_path, "w+")
    buffer.write(str(currenttime))
    buffer.close()
    openwebpage("https://discord.gg/thunderclient")

try:  # checks for updates using the version number we defined earlier, pasted from andrewdarkyy cuz im lazy and his colorbot is just a modded version of mine so like who cares
    if not "11" in urlopen("https://raw.githubusercontent.com/Seconb/Arsenal-Colorbot/main/version.txt").read().decode("utf-8"):
        print("Outdated version, redownload: https://github.com/Seconb/Arsenal-Colorbot/releases")
        while True:
            sleep(0.1)
except Exception as e:
    print("Error checking update: ", e)
    log_error(e)
    print("Continuing anyway!")
    sleep(5)
    pass

try:
    config = configparser.ConfigParser()  # this is separating all the config options you set.
    config.optionxform = str
    config.read(config_file_path)
except Exception as e:
    print("Error reading config:", e)
    log_error(e)
    exit()

def rbxfocused():
    try:
        return "Roblox" == gw.getActiveWindow().title
    except AttributeError:
        # if you're in the middle of alt-tabbing it screws things up, so we'll just ignore if you're doing that
        return False
    except Exception as e:
        print("An error occurred checking if Roblox is focused: ", e)
        log_error(e)
        exit()

def change_config_setting(setting_name, new_value):  # changing the config settings ... duh.
    try:
        config.set("Config", setting_name, str(new_value))
        with open(config_file_path, "w") as configfile:
            config.write(configfile)
        load()  # Update global variables after changing config
        print(f"Config setting '{setting_name}' changed to {new_value}")
    except Exception as e:
        print(f"Error changing config setting '{setting_name}': {e}")
        log_error(e)
        exit()

def load():  # loading the settings, duh.
    global sct, center, screenshot, AIM_KEY, SWITCH_MODE_KEY, FOV_KEY_UP, FOV_KEY_DOWN, CAM_FOV, AIM_OFFSET_Y, AIM_OFFSET_X, AIM_SPEED_X, AIM_SPEED_Y, upper, lower, UPDATE_KEY, AIM_FOV, BINDMODE, COLOR, colorname, TRIGGERBOT, TRIGGERBOT_DELAY, SMOOTHENING, SMOOTH_FACTOR, TRIGGERBOT_DISTANCE
    # these are essential variables that show the settings of the application.
    system("title Colorbot")

    try:  # read the config file again, just in case if the user changed the settings while the program was running.
        config = configparser.ConfigParser()  # this is separating all the config options you set.
        config.optionxform = str
        config.read(config_file_path)
    except Exception as e:
        print("Error reading config:", e)
        log_error(e)
        exit()

    try:
        AIM_KEY = config.get("Config", "AIM_KEY")
        SWITCH_MODE_KEY = config.get("Config", "SWITCH_MODE_KEY")
        UPDATE_KEY = config.get("Config", "UPDATE_KEY")
        FOV_KEY_UP = config.get("Config", "FOV_KEY_UP")
        FOV_KEY_DOWN = config.get("Config", "FOV_KEY_DOWN")
        CAM_FOV = int(config.get("Config", "CAM_FOV"))
        AIM_FOV = int(config.get("Config", "AIM_FOV"))
        AIM_OFFSET_Y = int(config.get("Config", "AIM_OFFSET_Y"))
        AIM_OFFSET_X = int(config.get("Config", "AIM_OFFSET_X"))
        AIM_SPEED_X = float(config.get("Config", "AIM_SPEED_X"))
        AIM_SPEED_Y = float(config.get("Config", "AIM_SPEED_Y"))
        TRIGGERBOT = config.get("Config", "TRIGGERBOT")
        TRIGGERBOT_DELAY = int(config.get("Config", "TRIGGERBOT_DELAY"))
        TRIGGERBOT_DISTANCE = int(config.get("Config", "TRIGGERBOT_DISTANCE"))
        SMOOTHENING = config.get("Config", "SMOOTHENING")
        SMOOTH_FACTOR = float(config.get("Config", "SMOOTH_FACTOR"))
        UPPER_COLOR = tuple(map(int, config.get("Config", "UPPER_COLOR").split(', ')))  # pasted from the modded colorbot but we're partnered so its chill
        LOWER_COLOR = tuple(map(int, config.get("Config", "LOWER_COLOR").split(', ')))
        if SMOOTH_FACTOR <= 0:
            SMOOTHENING = "disabled"
        COLOR = config.get("Config", "COLOR")
        if COLOR.lower() == "yellow":
            colorname = Fore.YELLOW
            upper = np.array((30, 255, 229), dtype="uint8")  # The upper and lower ranges defined are the colors that the aimbot will detect and shoot at
            lower = np.array((30, 255, 229), dtype="uint8")  # It's basically a group of a VERY specific shade of yellow (in this case) that it will shoot at and nothing else. The format is HSV, which differs from RGB.
        if COLOR.lower() == "blue":
            colorname = Fore.BLUE
            upper = np.array((120, 255, 229), dtype="uint8")
            lower = np.array((120, 255, 229), dtype="uint8")
        if COLOR.lower() == "pink" or COLOR.lower() == "magenta" or COLOR.lower() == "purple":
            colorname = Fore.MAGENTA
            upper = np.array((150, 255, 229), dtype="uint8")
            lower = np.array((150, 255, 229), dtype="uint8")
        if COLOR.lower() == "green":
            colorname = Fore.GREEN
            upper = np.array((60, 255, 229), dtype="uint8")
            lower = np.array((60, 255, 229), dtype="uint8")
        if COLOR.lower() == "red":
            colorname = Fore.RED
            upper = np.array((0, 255, 229), dtype="uint8")
            lower = np.array((0, 255, 229), dtype="uint8")
        if COLOR.lower() == "white":
            colorname = Fore.WHITE
            upper = np.array((0, 0, 255), dtype="uint8")
            lower = np.array((0, 0, 255), dtype="uint8")
        BINDMODE = toggleholdmodes[int(config.get("Config", "BINDMODE"))]
    except Exception as e:
        print("Error loading config settings:", e)
        log_error(e)
        exit()

    sct = mss.mss()
    screenshot = np.array(sct.grab(sct.monitors[1]))
    center = int(screenshot.shape[1] / 2), int(screenshot.shape[0] / 2)

# Key mapping configurations (imported from keybinds.py)
class Key:
    def __init__(self, key):
        self.key = key
        self.pressed = False

    def press(self):
        if not self.pressed:
            self.pressed = True
            system(f"xdotool keydown {self.key}")

    def release(self):
        if self.pressed:
            self.pressed = False
            system(f"xdotool keyup {self.key}")

    def is_pressed(self):
        return is_pressed(self.key)

load()

# Main loop
while True:
    try:
        if rbxfocused():  # Ensures the game is focused before taking actions
            # Your aimbot logic here
            pass
        sleep(0.01)  # Small delay to reduce CPU usage
    except Exception as e:
        print(f"An error occurred in the main loop: {e}")
        log_error(e)

