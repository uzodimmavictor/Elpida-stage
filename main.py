from context import Context
import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <config.json> [--start]")
        return None

    configFile = sys.argv[1]
    context = Context()
    context.loadConfiguration(configFile)

    print(f"Loaded {len(context.listComponents)} component(s) from {configFile}")
    if "--start" in sys.argv[2:]:
        try:
            context.start()
        finally:
            context.stop()


if __name__ == "__main__":
    main()
