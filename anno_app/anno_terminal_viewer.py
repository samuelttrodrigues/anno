

import json
import os
import sys
import argparse
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
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BG_YELLOW = "\033[43m"
    BLACK = "\033[30m"

# --- Styling and Formatting ---
def parse_note_content(content):
    lines = content.split('\n', 2)
    title = lines[0] if lines else "Untitled"
    tags = []
    body_start_index = 1
    if len(lines) > 1:
        tags_match = re.match(r'^\s*\[(.*)\]\s*$', lines[1])
        if tags_match:
            tags_str = tags_match.group(1)
            tags = [tag.strip().lstrip('#') for tag in tags_str.split(',') if tag.strip()]
            body_start_index = 2
    body = '\n'.join(lines[body_start_index:]) if len(lines) > body_start_index else ''
    return title, tags, body

def apply_terminal_styling(text):
    # Use a function for substitution to avoid issues with backslashes
    def replace_checklist_done(m): return f"{Colors.GREEN}✔{Colors.RESET}{m.group(1)}"
    def replace_checklist_pending(m): return f"{Colors.RED}☐{Colors.RESET}{m.group(1)}"
    def replace_list(m): return f"{Colors.YELLOW}•{Colors.RESET}{m.group(1)}"

    # Note: Order matters here. More specific tags should come first.
    text = re.sub(r'^\s*\[x\](.*)$' , replace_checklist_done, text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\[ \](.*)$' , replace_checklist_pending, text, flags=re.MULTILINE)
    text = re.sub(r'^\s*[\*\-](.*)$'   , replace_list, text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.(.*)$' , replace_list, text, flags=re.MULTILINE)
    # Custom tags
    text = re.sub(r"<h>(.*?)</h>", f"{Colors.BG_YELLOW}{Colors.BLACK}\1{Colors.RESET}", text, flags=re.DOTALL)
    text = re.sub(r"<i>(.*?)</i>", f"{Colors.BOLD}{Colors.RED}\1{Colors.RESET}", text, flags=re.DOTALL)
    text = re.sub(r"<c>(.*?)</c>", f"{Colors.BOLD}{Colors.CYAN}\1{Colors.RESET}", text, flags=re.DOTALL)
    return text

# --- Main Logic ---
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def get_all_notes():
    if not os.path.exists(ANNOTATIONS_FILE):
        eprint(f"{Colors.RED}No annotations file found.{Colors.RESET}")
        return []
    try:
        with open(ANNOTATIONS_FILE, "r") as f:
            notes = json.load(f)
            notes.sort(key=lambda x: x["timestamp"], reverse=True)
            return notes
    except json.JSONDecodeError:
        eprint(f"{Colors.RED}Error: Could not read annotations file.{Colors.RESET}")
        return []

def search_and_display_notes(search_term):
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
            eprint(apply_terminal_styling(body) + "\n---")
    
    if not found_notes: eprint(f"{Colors.YELLOW}No notes found with the tag '{search_term}'.{Colors.RESET}")

def read_note(index):
    all_notes = get_all_notes()
    if not 1 <= index + 1 <= len(all_notes):
        eprint(f"{Colors.RED}Invalid note number.{Colors.RESET}")
        return
    
    note_data = all_notes[index]
    title, _, body = parse_note_content(note_data.get('content', ''))
    dt = datetime.fromisoformat(note_data["timestamp"])
    formatted_date = dt.strftime("%Y-%m-%d %I:%M %p")

    eprint(f"\n{Colors.BOLD}{Colors.GREEN}--- Viewing Note ---{Colors.RESET}")
    eprint(f"{Colors.CYAN}{formatted_date}{Colors.RESET} - {Colors.BOLD}{title}{Colors.RESET}")
    eprint("---")
    eprint(apply_terminal_styling(body))
    eprint(f"{Colors.BOLD}{Colors.GREEN}--- End of Note ---{Colors.RESET}")

def interactive_view():
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
        eprint(f"\n{Colors.BOLD}Actions: (r)ead, (e)dit, (d)elete, (q)uit{Colors.RESET}")
        try:
            eprint("Enter command: ", end="")
            choice = input().lower().strip()
        except (EOFError, KeyboardInterrupt):
            eprint("\nExiting.")
            break

        if choice == 'q' or choice == '/quit': break

        action, target_num_str = (None, None)
        if choice.isdigit(): action, target_num_str = "EDIT", choice
        elif choice.startswith('d') and choice[1:].isdigit(): action, target_num_str = "DELETE", choice[1:]
        elif choice.startswith('r') and choice[1:].isdigit(): action, target_num_str = "READ", choice[1:]
        
        if action and target_num_str:
            try:
                num = int(target_num_str)
                if 1 <= num <= len(all_notes):
                    if action == "READ":
                        read_note(num - 1)
                        # After reading, just continue the loop to show the menu again
                        continue
                    else:
                        # For Edit/Delete, we exit and let the shell script handle it
                        print(f"ACTION:{action}:{num - 1}")
                        sys.exit(0)
                else:
                    eprint(f"{Colors.RED}Invalid note number: {num}{Colors.RESET}")
            except ValueError:
                eprint(f"{Colors.RED}Invalid command format.{Colors.RESET}")
        else:
            eprint(f"{Colors.RED}Invalid command. Please try again.{Colors.RESET}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Terminal viewer for Anno notes.")
    parser.add_argument("-s", "--search", help="Search for notes by a specific tag.")
    args = parser.parse_args()

    if args.search:
        search_and_display_notes(args.search)
    else:
        interactive_view()
