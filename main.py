import sys
import os
from engine import GameEngine

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        os.makedirs("logs", exist_ok=True)
        self.log = open("logs/full_game_log.txt", "w", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush() # Ensure it writes immediately

    def flush(self):
        # Current implementation of flush to satisfy stream interface
        self.terminal.flush()
        self.log.flush()

    def isatty(self):
        return self.terminal.isatty()

    def fileno(self):
        return self.terminal.fileno()

def main():
    # Redirect stdout to capture all output
    sys.stdout = Logger()
    print("Welcome to AI Mafia! Starting game engine...")
    engine = GameEngine()
    try:
        engine.run()
    except KeyboardInterrupt:
        print("\nGame Terminated by User.")
        sys.exit(0)
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
