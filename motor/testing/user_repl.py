import keyboard

from KEYBOARD_CONFIG import FORWARD, RIGHT, LEFT, BACKWARD

while True:
    if keyboard.is_pressed(FORWARD):
        print("Forward press detected")
    if keyboard.is_pressed(RIGHT):
        print("Up press detected")
    if keyboard.is_pressed(LEFT):
        print("Left press detected")
    if keyboard.is_pressed(BACKWARD):
        print("Backward press detected")
