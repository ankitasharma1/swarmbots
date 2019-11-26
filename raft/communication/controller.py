import keyboard
from time import time

from bt_server import BT_Server
from KEYBOARD_CONFIG import KEYBOARD_CONFIG_DICT, DEBOUNCE_INTERVAL

def graceful_exit(func):
    def wrapper(*args, **kw_args):
        try:
            return func(*args, **kw_args)
        except KeyboardInterrupt:
            self = args[0]
            self.server.clean_up()
            print("goodbye.")
            return
    return wrapper

class Controller():
    def __init__(self, debug=False):
        # how often should commands be sent
        #   NOTE: these values are in seconds, the debounce_interval should be
        #         roughly equal to RUN_TIME defined in the MotorDriver class
        self.debounce_interval = DEBOUNCE_INTERVAL
        self.last_press = 0.0

        self.debug = debug

        # keyboard_config_dict should be a dictionary with the following keys
        # this decides which keys are listened for and what messages they send
        self.right = KEYBOARD_CONFIG_DICT['RIGHT']
        self.left = KEYBOARD_CONFIG_DICT['LEFT']
        self.forward = KEYBOARD_CONFIG_DICT['FORWARD']
        self.backward = KEYBOARD_CONFIG_DICT['BACKWARD']

        # Run the server. It will be connected to by the leader's client
        controller_addr = BT_CONTROLLER_DICT["CONTROLLER"]["ADDR"]
        controller_port = BT_CONTROLLER_DICT["CONTROLLER"]["PORT"]
        self.server = BT_Server(controller_addr, controller_port, debug=debug)

    @graceful_exit
    def start(self):
        while True:
            if keyboard.is_pressed(self.forward) and not self.debounce():
                if self.debug:
                    print("\nForward press detected")
                self.last_press = time()
                self.server.send('forward')
            if keyboard.is_pressed(self.right) and not self.debounce():
                if self.debug:
                    print("\nRight press detected")
                self.last_press = time()
                self.server.send('right')
            if keyboard.is_pressed(self.left) and not self.debounce():
                if self.debug:
                    print("\nLeft press detected")
                self.last_press = time()
                self.server.send('left')
            if keyboard.is_pressed(self.backward) and not self.debounce():
                if self.debug:
                    print("\nBackward press detected")
                self.last_press = time()
                self.server.send('backward')

    @graceful_exit
    def debounce(self):
        elapsed_time = time() - self.last_press
        if elapsed_time > self.debounce_interval:
            return False
        else:
            return True

if __name__ == '__main__':
    control = Controller()
    control.start(True)
