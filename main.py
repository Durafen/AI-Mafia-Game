import sys
from engine import GameEngine

def main():
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
