import os
import json
import re
import zipfile
from datetime import datetime

# --- Configuration ---
ANNOTATIONS_FILE = os.path.expanduser("~/.local/share/annotations.json")
CONFIG_DIR = os.path.expanduser("~/.config/anno")
BACKUP_DIR = os.path.join(CONFIG_DIR, "backups")

# --- Helper Functions ---
def parse_note_content(content):
    lines = content.split('\n', 2)
    title = lines[0] if lines else "Untitled"
    return title

def sanitize_filename(name):
    # Remove invalid characters for filenames
    name = re.sub(r'[\\/*?"<>|]', "", name)
    # Replace spaces with underscores
    name = re.sub(r'\s+', '_', name)
    return name[:100] # Limit filename length

# --- Core Functions ---
def export_notes(target_dir):
    """Exports all notes to individual .txt files in a specified directory."""
    if not os.path.exists(ANNOTATIONS_FILE):
        print("Error: Annotations file not found.")
        return False

    os.makedirs(target_dir, exist_ok=True)
    
    with open(ANNOTATIONS_FILE, "r") as f:
        try:
            notes = json.load(f)
        except json.JSONDecodeError:
            print("Error: Could not read annotations file.")
            return False

    count = 0
    for note in notes:
        content = note.get("content", "")
        timestamp_str = note.get("timestamp")
        dt = datetime.fromisoformat(timestamp_str)
        
        title = parse_note_content(content)
        sanitized_title = sanitize_filename(title)
        
        filename = f"{dt.strftime('%Y-%m-%d_%H-%M-%S')}_{sanitized_title}.txt"
        filepath = os.path.join(target_dir, filename)
        
        with open(filepath, "w") as f_out:
            f_out.write(content)
        count += 1

    print(f"Successfully exported {count} notes to {target_dir}")
    return True

def backup_notes():
    """Creates a timestamped zip backup of the annotations.json file."""
    if not os.path.exists(ANNOTATIONS_FILE):
        print("Error: Annotations file not found. Nothing to back up.")
        return None

    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_filename = f"anno_backup_{timestamp}.zip"
    backup_filepath = os.path.join(BACKUP_DIR, backup_filename)
    
    try:
        with zipfile.ZipFile(backup_filepath, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(ANNOTATIONS_FILE, os.path.basename(ANNOTATIONS_FILE))
        print(f"Successfully created backup: {backup_filepath}")
        return backup_filepath
    except Exception as e:
        print(f"Error creating backup: {e}")
        return None

def list_backups():
    """Returns a sorted list of available backup files."""
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

    # First, create a final emergency backup of the current state before overwriting
    print("Creating a pre-restore backup of the current notes...")
    backup_notes()

    try:
        with zipfile.ZipFile(backup_filepath, 'r') as zf:
            # This will extract the file to the root of the zip path, which is ANNOTATIONS_FILE's dir
            zf.extract(os.path.basename(ANNOTATIONS_FILE), os.path.dirname(ANNOTATIONS_FILE))
        # The extract call overwrites the file, so we rename the extracted file to the correct name
        extracted_path = os.path.join(os.path.dirname(ANNOTATIONS_FILE), os.path.basename(ANNOTATIONS_FILE))
        if os.path.exists(ANNOTATIONS_FILE):
             os.remove(ANNOTATIONS_FILE)
        os.rename(extracted_path, ANNOTATIONS_FILE)
        print(f"Successfully restored notes from {backup_filename}")
        return True
    except Exception as e:
        print(f"Error restoring from backup: {e}")
        return False
