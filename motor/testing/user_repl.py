import keyboard
from time import time

from KEYBOARD_CONFIG import FORWARD, RIGHT, LEFT, BACKWARD

debounce_interval = 0.2 # ms
last_press = 0.0

keyboard.block_key(FORWARD)
keyboard.block_key(RIGHT)
keyboard.block_key(LEFT)
keyboard.block_key(BACKWARD)

def elapsed_time(start):
    return time() - start

while True:
    if keyboard.is_pressed(FORWARD) and elapsed_time(last_press) > debounce_interval:
        print("\nForward press detected")
        last_press = time()
    if keyboard.is_pressed(RIGHT) and elapsed_time(last_press) > debounce_interval:
        print("\nRight press detected")
        last_press = time()
    if keyboard.is_pressed(LEFT) and elapsed_time(last_press) > debounce_interval:
        print("\nLeft press detected")
        last_press = time()
    if keyboard.is_pressed(BACKWARD) and elapsed_time(last_press) > debounce_interval:
        print("\nBackward press detected")
        last_press = time()

