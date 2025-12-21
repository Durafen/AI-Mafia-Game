# input_listener.py - Non-blocking keyboard input handler

import sys
import termios
import tty
import select


class InputListener:
    """Handles non-blocking keyboard input"""
    def __init__(self):
        self.old_settings = None

    def __enter__(self):
        self.old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        return self

    def __exit__(self, type, value, traceback):
        if self.old_settings:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

    def is_data(self):
        return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

    def check_for_space(self):
        if self.is_data():
            c = sys.stdin.read(1)
            if c == ' ':
                return True
        return False

    def pause_for_input(self):
        """Restore normal terminal mode for blocking input()"""
        if self.old_settings:
            # Use TCSAFLUSH to discard any buffered input and restore settings
            termios.tcsetattr(sys.stdin, termios.TCSAFLUSH, self.old_settings)

    def resume_cbreak(self):
        """Re-enable cbreak mode after input"""
        tty.setcbreak(sys.stdin.fileno())
