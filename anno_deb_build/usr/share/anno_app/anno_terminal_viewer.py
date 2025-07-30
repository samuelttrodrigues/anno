

import json
import os
from datetime import datetime
from collections import defaultdict
import re

# --- Configuration ---
ANNOTATIONS_FILE = os.path.expanduser("~/.local/share/annotations.json")

# --- ANSI Color Codes ---
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

# --- Styling Functions ---
def apply_terminal_styling(text):
    # Highlight: Yellow background, black text
    text = re.sub(r"<h>(.*?)</h>", f"{Colors.BG_YELLOW}{Colors.BLACK}\\1{Colors.RESET}", text, flags=re.DOTALL)
    # Important: Red text, bold
    text = re.sub(r"<i>(.*?)</i>", f"{Colors.BOLD}{Colors.RED}\\1{Colors.RESET}", text, flags=re.DOTALL)
    # Code: Cyan text, bold
    text = re.sub(r"<c>(.*?)</c>", f"{Colors.BOLD}{Colors.CYAN}\\1{Colors.RESET}", text, flags=re.DOTALL)
    return text

# --- Main Logic ---
def view_annotations_terminal():
    if not os.path.exists(ANNOTATIONS_FILE):
        print(f"{Colors.RED}No annotations file found.{Colors.RESET}")
        return

    with open(ANNOTATIONS_FILE, "r") as f:
        try:
            all_notes = json.load(f)
        except json.JSONDecodeError:
            print(f"{Colors.RED}Error: Could not read annotations file. It might be corrupted.{Colors.RESET}")
            return

    if not all_notes:
        print(f"{Colors.YELLOW}No annotations yet. Use 'anno' to create one.{Colors.RESET}")
        return

    all_notes.sort(key=lambda x: x["timestamp"], reverse=True)

    notes_by_date = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for note in all_notes:
        dt = datetime.fromisoformat(note["timestamp"])
        notes_by_date[dt.year][dt.strftime("%B")][dt.day].append(note)

    print(f"{Colors.BOLD}{Colors.GREEN}--- Your Annotations ---{Colors.RESET}\n")

    for year in sorted(notes_by_date.keys(), reverse=True):
        print(f"{Colors.BOLD}{Colors.BLUE}>> {year}{Colors.RESET}")
        for month_name in sorted(notes_by_date[year].keys(), key=lambda m: datetime.strptime(m, "%B").month, reverse=True):
            print(f"  {Colors.BOLD}{Colors.MAGENTA}>> {month_name}{Colors.RESET}")
            for day in sorted(notes_by_date[year][month_name].keys(), reverse=True):
                print(f"    {Colors.BOLD}{Colors.CYAN}>> Day {day}{Colors.RESET}")
                for note in notes_by_date[year][month_name][day]:
                    dt = datetime.fromisoformat(note["timestamp"])
                    formatted_time = dt.strftime("%I:%M %p")
                    content = apply_terminal_styling(note["content"])
                    print(f"      {Colors.WHITE}{formatted_time}: {content}{Colors.RESET}\n")

if __name__ == "__main__":
    view_annotations_terminal()
