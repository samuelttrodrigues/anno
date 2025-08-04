import os
import json
import re
import zipfile
from datetime import datetime

# --- Configuration ---
# Define the primary locations for annotations and configuration files.
# These are placed in standard user directories for Linux systems.
ANNOTATIONS_FILE = os.path.expanduser("~/.local/share/annotations.json")
CONFIG_DIR = os.path.expanduser("~/.config/anno")
BACKUP_DIR = os.path.join(CONFIG_DIR, "backups")

# --- Helper Functions ---

def parse_note_content(content):
    """Extracts the title from the full content of a note."""
    # The title is always the first line of the note.
    lines = content.split('\n', 1)
    return lines[0] if lines else "Untitled"

def sanitize_filename(name):
    """Removes characters from a string that are invalid for use in filenames."""
    # Remove characters that are commonly disallowed in filesystems.
    name = re.sub(r'[\\/*?"<>|]', "", name)
    # Replace whitespace with underscores for better command-line compatibility.
    name = re.sub(r'\s+', '_', name)
    # Truncate to a reasonable length to avoid issues with filesystem limits.
    return name[:100]

# --- Core Data Management Functions ---

def export_notes(target_dir):
    """Exports all notes to individual .txt files in a specified directory."""
    if not os.path.exists(ANNOTATIONS_FILE):
        print("Error: Annotations file not found.")
        return False

    os.makedirs(target_dir, exist_ok=True)
    
    try:
        with open(ANNOTATIONS_FILE, "r") as f:
            notes = json.load(f)
    except json.JSONDecodeError:
        print("Error: Could not read or parse the annotations file.")
        return False

    count = 0
    for note in notes:
        content = note.get("content", "")
        timestamp_str = note.get("timestamp")
        dt = datetime.fromisoformat(timestamp_str)
        
        title = parse_note_content(content)
        sanitized_title = sanitize_filename(title)
        
        # Create a unique, descriptive filename for each note.
        filename = f"{dt.strftime('%Y-%m-%d_%H-%M-%S')}_{sanitized_title}.txt"
        filepath = os.path.join(target_dir, filename)
        
        with open(filepath, "w") as f_out:
            f_out.write(content)
        count += 1

    print(f"Successfully exported {count} notes to {target_dir}")
    return True

def backup_notes():
    """Creates a timestamped .zip backup of the annotations.json file."""
    if not os.path.exists(ANNOTATIONS_FILE):
        print("Error: Annotations file not found. Nothing to back up.")
        return None

    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_filename = f"anno_backup_{timestamp}.zip"
    backup_filepath = os.path.join(BACKUP_DIR, backup_filename)
    
    try:
        # Use a zip archive to save space and keep the backup self-contained.
        with zipfile.ZipFile(backup_filepath, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(ANNOTATIONS_FILE, os.path.basename(ANNOTATIONS_FILE))
        print(f"Successfully created backup: {backup_filepath}")
        return backup_filepath
    except Exception as e:
        print(f"Error creating backup: {e}")
        return None

def list_backups():
    """Returns a sorted list of available backup files, newest first."""
    if not os.path.exists(BACKUP_DIR):
        return []
    
    backups = [f for f in os.listdir(BACKUP_DIR) if f.endswith('.zip') and f.startswith('anno_backup_')]
    return sorted(backups, reverse=True)

def restore_notes(backup_filename):
    """Restores the annotations.json file from a specified backup zip file."""
    backup_filepath = os.path.join(BACKUP_DIR, backup_filename)
    if not os.path.exists(backup_filepath):
        print(f"Error: Backup file not found: {backup_filename}")
        return False

    # As a safety measure, create one last backup of the current state before overwriting.
    print("Creating a pre-restore backup of the current notes...")
    backup_notes()

    try:
        with zipfile.ZipFile(backup_filepath, 'r') as zf:
            # Extract the annotations file into its parent directory, overwriting the original.
            zf.extract(os.path.basename(ANNOTATIONS_FILE), os.path.dirname(ANNOTATIONS_FILE))
        
        # Ensure the restored file has the correct name.
        extracted_path = os.path.join(os.path.dirname(ANNOTATIONS_FILE), os.path.basename(ANNOTATIONS_FILE))
        if os.path.exists(ANNOTATIONS_FILE):
             os.remove(ANNOTATIONS_FILE)
        os.rename(extracted_path, ANNOTATIONS_FILE)

        print(f"Successfully restored notes from {backup_filename}")
        return True
    except Exception as e:
        print(f"Error restoring from backup: {e}")
        return False