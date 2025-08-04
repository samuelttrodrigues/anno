import json
import os
import sys
import argparse
from datetime import datetime
import re

# --- Configuration ---
# The primary data file for the application.
ANNOTATIONS_FILE = os.path.expanduser("~/.local/share/annotations.json")

# --- ANSI Color Codes for Terminal Styling ---
# Provides a simple way to add color and emphasis to terminal output.
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    BG_YELLOW = "\033[43m"
    BLACK = "\033[30m"

# --- Note Parsing and Styling ---

def parse_note_content(content):
    """Parses the raw text of a note to separate title, tags, and body."""
    lines = content.split('\n', 2)
    title = lines[0] if lines else "Untitled"
    tags = []
    body_start_index = 1
    
    # Tags are expected on the second line in the format: [#tag1, #tag2]
    if len(lines) > 1:
        tags_match = re.match(r'^\s*\[(.*)\]\s*$', lines[1])
        if tags_match:
            tags_str = tags_match.group(1)
            tags = [tag.strip().lstrip('#') for tag in tags_str.split(',') if tag.strip()]
            body_start_index = 2
            
    body = '\n'.join(lines[body_start_index:]) if len(lines) > body_start_index else ''
    return title, tags, body

def apply_terminal_styling(text):
    """Applies ANSI escape codes to the note body for terminal display."""
    # Use functions for substitution to handle special characters and add clarity.
    def replace_checklist_done(m): return f"{Colors.GREEN}✔ {m.group(1).lstrip()}{Colors.RESET}"
    def replace_checklist_pending(m): return f"{Colors.RED}☐ {m.group(1).lstrip()}{Colors.RESET}"
    def replace_list(m): return f"{Colors.YELLOW}• {m.group(1).lstrip()}{Colors.RESET}"

    # Apply styling for checklists and lists.
    text = re.sub(r'^\s*\[x\](.*)$' , replace_checklist_done, text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\[ \](.*)$' , replace_checklist_pending, text, flags=re.MULTILINE)
    text = re.sub(r'^\s*[\*\-](.*)$'   , replace_list, text, flags=re.MULTILINE)
    text = re.sub(r'^(\s*\d+\.)\s*(.*)$' , replace_list, text, flags=re.MULTILINE)
    
    # Apply styling for custom inline tags like <h>, <i>, and <c>.
    text = re.sub(r"<h>(.*?)</h>", f"{Colors.BG_YELLOW}{Colors.BLACK}\1{Colors.RESET}", text, flags=re.DOTALL)
    text = re.sub(r"<i>(.*?)</i>", f"{Colors.BOLD}{Colors.RED}\1{Colors.RESET}", text, flags=re.DOTALL)
    text = re.sub(r"<c>(.*?)</c>", f"{Colors.BOLD}{Colors.CYAN}\1{Colors.RESET}", text, flags=re.DOTALL)
    return text

# --- Core Application Logic ---

def eprint(*args, **kwargs):
    """Prints to stderr to avoid interfering with stdout for inter-process communication."""
    print(*args, file=sys.stderr, **kwargs)

def get_all_notes():
    """Loads all notes from the JSON file and sorts them by timestamp."""
    if not os.path.exists(ANNOTATIONS_FILE):
        eprint(f"{Colors.RED}No annotations file found at {ANNOTATIONS_FILE}{Colors.RESET}")
        return []
    try:
        with open(ANNOTATIONS_FILE, "r") as f:
            notes = json.load(f)
            # Sort notes reverse-chronologically.
            notes.sort(key=lambda x: x["timestamp"], reverse=True)
            return notes
    except json.JSONDecodeError:
        eprint(f"{Colors.RED}Error: Could not read or parse the annotations file.{Colors.RESET}")
        return []

def search_and_display_notes(search_term):
    """Filters and displays notes that match a given search tag."""
    all_notes = get_all_notes()
    if not all_notes: return

    if search_term.startswith('#'): search_term = search_term[1:]
    search_term = search_term.lower()

    found_notes = False
    for note_data in all_notes:
        title, tags, body = parse_note_content(note_data.get('content', ''))
        if any(search_term == tag.lower() for tag in tags):
            if not found_notes:
                eprint(f"{Colors.BOLD}{Colors.GREEN}--- Search Results for tag: '{search_term}' ---{Colors.RESET}\n")
                found_notes = True
            dt = datetime.fromisoformat(note_data["timestamp"])
            formatted_date = dt.strftime("%Y-%m-%d %I:%M %p")
            eprint(f"{Colors.CYAN}{formatted_date}{Colors.RESET} - {Colors.BOLD}{title}{Colors.RESET}")
            if tags:
                eprint(f"{Colors.YELLOW}Tags: {json.dumps(tags)}{Colors.RESET}")
            eprint(apply_terminal_styling(body) + "\n---")
    
    if not found_notes: eprint(f"{Colors.YELLOW}No notes found with the tag '{search_term}'.{Colors.RESET}")

def read_note(index):
    """Displays the full, formatted content of a single note."""
    all_notes = get_all_notes()
    if not 1 <= index + 1 <= len(all_notes):
        eprint(f"{Colors.RED}Invalid note number.{Colors.RESET}")
        return
    
    note_data = all_notes[index]
    title, tags, body = parse_note_content(note_data.get('content', ''))
    dt = datetime.fromisoformat(note_data["timestamp"])
    formatted_date = dt.strftime("%Y-%m-%d %I:%M %p")

    eprint(f"\n{Colors.BOLD}{Colors.GREEN}--- Viewing Note #{index + 1} ---{Colors.RESET}")
    eprint(f"{Colors.CYAN}{formatted_date}{Colors.RESET} - {Colors.BOLD}{title}{Colors.RESET}")
    if tags:
        eprint(f"{Colors.YELLOW}Tags: {json.dumps(tags)}{Colors.RESET}")
    eprint("---")
    eprint(apply_terminal_styling(body))
    eprint(f"\n{Colors.BOLD}{Colors.GREEN}--- End of Note ---{Colors.RESET}")

def interactive_view():
    """The main interactive loop for viewing, editing, and deleting notes."""
    all_notes = get_all_notes()
    if not all_notes:
        eprint(f"{Colors.YELLOW}No annotations yet. Use 'anno' to create one.{Colors.RESET}")
        return

    eprint(f"{Colors.BOLD}{Colors.GREEN}--- Your Annotations ---{Colors.RESET}\n")
    for i, note in enumerate(all_notes):
        title, _, _ = parse_note_content(note.get('content',''))
        dt = datetime.fromisoformat(note["timestamp"])
        formatted_date = dt.strftime("%Y-%m-%d %I:%M %p")
        eprint(f"{Colors.YELLOW}{i + 1}:{Colors.RESET} {Colors.CYAN}{formatted_date}{Colors.RESET} - {title}")

    while True:
        eprint(f"\n{Colors.BOLD}Commands: Enter number to READ || Enter number + e to EDIT || Enter num. + d to DELETE || Type /quit to QUIT.{Colors.RESET}")
        try:
            eprint("Enter command: ", end="")
            choice = input().lower().strip()
        except (EOFError, KeyboardInterrupt):
            eprint("\nExiting.")
            break

        if choice == 'quit' or choice == '/quit': break

        # Use regex to parse the user's command (e.g., '1d' for delete, '2e' for edit, '3' for read)
        action, num_str = (None, None)
        match_edit = re.match(r'^(\d+)e$', choice)
        match_delete = re.match(r'^(\d+)d$', choice)
        match_read = re.match(r'^(\d+)$' , choice)

        if match_edit:
            action, num_str = "EDIT", match_edit.group(1)
        elif match_delete:
            action, num_str = "DELETE", match_delete.group(1)
        elif match_read:
            action, num_str = "READ", match_read.group(1)

        if action and num_str:
            try:
                num = int(num_str)
                if 1 <= num <= len(all_notes):
                    if action == "READ":
                        read_note(num - 1)
                        continue # Go back to the command prompt
                    else:
                        # For Edit/Delete, send the command to the parent shell script.
                        # This is the primary method of inter-process communication.
                        print(f"ACTION:{action}:{num - 1}")
                        sys.exit(0)
                else:
                    eprint(f"{Colors.RED}Invalid note number: {num}{Colors.RESET}")
            except ValueError:
                eprint(f"{Colors.RED}Invalid command format.{Colors.RESET}")
        else:
            eprint(f"{Colors.RED}Invalid command. Please try again.{Colors.RESET}")

# --- Script Entry Point ---
if __name__ == "__main__":
    # Set up command-line argument parsing.
    parser = argparse.ArgumentParser(description="Terminal viewer for Anno notes.")
    parser.add_argument("-s", "--search", help="Search for notes by a specific tag.")
    args = parser.parse_args()

    # Launch the appropriate view based on arguments.
    if args.search:
        search_and_display_notes(args.search)
    else:
        interactive_view()