
import json
import os
import sys
from datetime import datetime
import re

# --- Configuration ---
ANNOTATIONS_FILE = os.path.expanduser("~/.local/share/annotations.json")

# --- ANSI Color Codes ---
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BG_YELLOW = "\033[43m"
    BLACK = "\033[30m"

# --- Styling Functions ---
def apply_terminal_styling(text):
    text = re.sub(r"<h>(.*?)</h>", f"{Colors.BG_YELLOW}{Colors.BLACK}\\1{Colors.RESET}", text, flags=re.DOTALL)
    text = re.sub(r"<i>(.*?)</i>", f"{Colors.BOLD}{Colors.RED}\\1{Colors.RESET}", text, flags=re.DOTALL)
    text = re.sub(r"<c>(.*?)</c>", f"{Colors.BOLD}{Colors.CYAN}\\1{Colors.RESET}", text, flags=re.DOTALL)
    return text

# --- Main Logic ---
def view_and_select_note():
    def eprint(*args, **kwargs):
        print(*args, file=sys.stderr, **kwargs)

    if not os.path.exists(ANNOTATIONS_FILE):
        eprint(f"{Colors.RED}No annotations file found.{Colors.RESET}")
        return

    try:
        with open(ANNOTATIONS_FILE, "r") as f:
            all_notes = json.load(f)
    except json.JSONDecodeError:
        eprint(f"{Colors.RED}Error: Could not read annotations file.{Colors.RESET}")
        return

    if not all_notes:
        eprint(f"{Colors.YELLOW}No annotations yet. Use 'anno' to create one.{Colors.RESET}")
        return

    all_notes.sort(key=lambda x: x["timestamp"], reverse=True)

    eprint(f"{Colors.BOLD}{Colors.GREEN}--- Your Annotations ---{Colors.RESET}\n")
    for i, note in enumerate(all_notes):
        dt = datetime.fromisoformat(note["timestamp"])
        formatted_date = dt.strftime("%Y-%m-%d %I:%M %p")
        content_preview = apply_terminal_styling(note['content'].split('\n')[0])
        eprint(f"{Colors.YELLOW}{i + 1}:{Colors.RESET} {Colors.CYAN}{formatted_date}{Colors.RESET} - {content_preview}")

    while True:
        eprint(f"\n{Colors.BOLD}Enter a note number to edit, 'd<number>' to delete, or '/quit' to exit.{Colors.RESET}")
        try:
            # Print the prompt to stderr, so it doesn't go into the action file
            eprint("Enter command: ", end="")
            # Read the user's choice from stdin
            choice = input().lower().strip()
        except (EOFError, KeyboardInterrupt):
            eprint("\nExiting.")
            break

        if choice == '/quit':
            break

        action = None
        target_num_str = None

        if choice.isdigit():
            action = "EDIT"
            target_num_str = choice
        elif choice.startswith('d') and choice[1:].isdigit():
            action = "DELETE"
            target_num_str = choice[1:]
        
        if action and target_num_str:
            try:
                num = int(target_num_str)
                if 1 <= num <= len(all_notes):
                    # Print command to STDOUT for the shell script to capture
                    print(f"ACTION:{action}:{num - 1}")
                    sys.exit(0)
                else:
                    eprint(f"{Colors.RED}Invalid note number: {num}{Colors.RESET}")
            except ValueError:
                eprint(f"{Colors.RED}Invalid command format.{Colors.RESET}")
        else:
            eprint(f"{Colors.RED}Invalid command. Please try again.{Colors.RESET}")

if __name__ == "__main__":
    view_and_select_note()
