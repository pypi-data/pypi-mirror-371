import sys

# Import commands normally
from snapkit.utils.modules import jpg_to_png
from snapkit.utils.modules import overlay


available_commands = {
    "jpg_to_png": jpg_to_png.cli,
    "overlay": overlay.cli,
}

def main():
    if len(sys.argv) < 2:
        print("Hello from snapkit!")
        print("Usage: snapkit <command> [--args]\nTry 'snapkit <command> --help'")
        return

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == "--help":
        print("To know usage use snapkit <command> --help")
        print(f"Available commands: {list(available_commands.keys())}")
    elif command in available_commands:
        available_commands[command](args)
    else:
        print(f"Unknown command: {command}")
        print("To know usage use snapkit <command> --help")
        print(f"Available commands: {list(available_commands.keys())}")

if __name__ == "__main__":
    main()
