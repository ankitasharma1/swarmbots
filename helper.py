import sys
import threading

consoleLock = threading.Lock()

# Helper function to flush the buffer whenever we print.
def print_and_flush(text):
    consoleLock.acquire()
    print(text)
    sys.stdout.flush()
    consoleLock.release()