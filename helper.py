import sys

# Helper function to flush the buffer whenever we print.
def print_and_flush(text):
    print(text)
    sys.stdout.flush()