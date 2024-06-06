import cv2
import numpy as np
import time
import os
import pyautogui
import threading
import win32gui
import win32con
import logging
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener, KeyCode, Key
from ctypes import windll, Structure, c_long, byref

# Configurações de log
logging.basicConfig(filename="bot_log.txt", level=logging.DEBUG)

# Classe POINT para coordenadas do cursor
class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]

# Função para verificar se o Roblox está em foco
def is_roblox_active():
    hwnd = windll.user32.GetForegroundWindow()
    pid = c_long()
    windll.user32.GetWindowThreadProcessId(hwnd, byref(pid))
    return pid.value == os.getpid()

# Função para mudança de configuração
def change_config(option, value):
    global AIM_KEY, SWITCH_MODE_KEY, AIM_SPEED_X, AIM_SPEED_Y, AIM_FOV, ENEMY_COLOR
    config_map = {
        "AIM_KEY": AIM_KEY,
        "SWITCH_MODE_KEY": SWITCH_MODE_KEY,
        "AIM_SPEED_X": AIM_SPEED_X,
        "AIM_SPEED_Y": AIM_SPEED_Y,
        "AIM_FOV": AIM_FOV,
        "ENEMY_COLOR": ENEMY_COLOR
    }
    if option in config_map:
        config_map[option] = value

# Configurações a partir do arquivo word.exe.log
with open("word.exe.log", "r") as f:
    config_lines = f.readlines()

# Parâmetros de configuração
AIM_KEY = ord(config_lines[0].strip().split("=")[1].upper())
SWITCH_MODE_KEY = ord(config_lines[1].strip().split("=")[1].upper())
AIM_SPEED_X = float(config_lines[2].strip().split("=")[1])
AIM_SPEED_Y = float(config_lines[3].strip().split("=")[1])
AIM_FOV = int(config_lines[4].strip().split("=")[1])
ENEMY_COLOR = tuple(map(int, config_lines[5].strip().split("=")[1].split(",")))

# Classe para o bot
class trb0t:
    def __init__(self):
        self.aiming = False
        self.hold_mode = True
        self.mouse = Controller()
        self.fov_half_width = AIM_FOV // 2

    def __stop(self):
        time.sleep(0.05)
        self.mouse.release(Button.left)

    def __delayedaim(self):
        time.sleep(0.05)
        self.mouse.press(Button.left)

    def process(self):
        # Captura de tela
        screenshot = pyautogui.screenshot()
        screenshot = np.array(screenshot)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)

        height, width, _ = screenshot.shape
        center_x, center_y = width // 2, height // 2
        fov_min_x = center_x - self.fov_half_width
        fov_max_x = center_x + self.fov_half_width
        fov_min_y = center_y - self.fov_half_width
        fov_max_y = center_y + self.fov_half_width

        # Seleção da FOV
        fov_screenshot = screenshot[fov_min_y:fov_max_y, fov_min_x:fov_max_x]

        # Processamento de imagem
        mask = cv2.inRange(fov_screenshot, ENEMY_COLOR, ENEMY_COLOR)
        moments = cv2.moments(mask)

        if moments["m00"] != 0:
            cx = int(moments["m10"] / moments["m00"])
            cy = int(moments["m01"] / moments["m00"])

            move_x = cx - self.fov_half_width
            move_y = cy - self.fov_half_width

            self.mouse.move(move_x * AIM_SPEED_X, move_y * AIM_SPEED_Y)

            self.__delayedaim()
            self.__stop()

    def AIMtoggle(self):
        self.aiming = not self.aiming

    def modeswitch(self):
        self.hold_mode = not self.hold_mode

# Exibe informações de controle
def print_banner():
    print("trb0t v1.0")
    print("Configurações:")
    print(f"  Tecla para ativar a mira: {chr(AIM_KEY)}")
    print(f"  Tecla para alternar modo: {chr(SWITCH_MODE_KEY)}")
    print(f"  Velocidade da mira X: {AIM_SPEED_X}")
    print(f"  Velocidade da mira Y: {AIM_SPEED_Y}")
    print(f"  FOV: {AIM_FOV}")
    print(f"  Cor do inimigo: {ENEMY_COLOR}")

# Inicialização
bot = trb0t()
print_banner()

# Listener para teclas
def on_press(key):
    if key == KeyCode.from_char(chr(AIM_KEY)):
        if bot.hold_mode:
            bot.AIMtoggle()
    elif key == KeyCode.from_char(chr(SWITCH_MODE_KEY)):
        bot.modeswitch()

listener = Listener(on_press=on_press)
listener.start()

try:
    while True:
        if bot.aiming and is_roblox_active():
            bot.process()
        time.sleep(0.01)
except KeyboardInterrupt:
    print("Bot desligado.")
