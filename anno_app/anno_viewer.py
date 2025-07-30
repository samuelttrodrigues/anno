import tkinter as tk
from tkinter import ttk, font, messagebox, filedialog
import json
from datetime import datetime
import os
from collections import defaultdict
import re

# Import the new utility functions
from anno_app.anno_utils import export_notes, backup_notes, list_backups, restore_notes

# --- Configuration ---
CONFIG_DIR = os.path.expanduser("~/.config/anno")
SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")
ANNOTATIONS_FILE = os.path.expanduser("~/.local/share/annotations.json")
FONT_NAME = "DejaVu Sans"
MONO_FONT_NAME = "DejaVu Sans Mono"

# --- Themes ---
THEMES = {
    "Pastel": {
        "bg": "#B2D8B2", "card": "#F5F5DC", "text_fg": "#3D2B1F",
        "select_bg": "#A0522D", "select_fg": "#FFFFFF",
        "highlight": "#FFFACD", "important": "#FF4500", "code_bg": "#D3D3D3",
        "checklist_done": "#228B22", "checklist_pending": "#DC143C"
    },
    "Dark": {
        "bg": "#2E2E2E", "card": "#3C3C3C", "text_fg": "#E0E0E0",
        "select_bg": "#BB86FC", "select_fg": "#000000",
        "highlight": "#4A4A4A", "important": "#CF6679", "code_bg": "#555555",
        "checklist_done": "#03DAC6", "checklist_pending": "#CF6679"
    },
    "Light": {
        "bg": "#F0F0F0", "card": "#FFFFFF", "text_fg": "#000000",
        "select_bg": "#0078D7", "select_fg": "#FFFFFF",
        "highlight": "#FFFF00", "important": "#D93025", "code_bg": "#E8EAED",
        "checklist_done": "#137333", "checklist_pending": "#A50E0E"
    },
    "Nord": {
        "bg": "#2E3440", "card": "#3B4252", "text_fg": "#D8DEE9",
        "select_bg": "#88C0D0", "select_fg": "#2E3440",
        "highlight": "#5E81AC", "important": "#BF616A", "code_bg": "#4C566A",
        "checklist_done": "#A3BE8C", "checklist_pending": "#BF616A"
    },
    "Solarized Light": {
        "bg": "#fdf6e3", "card": "#eee8d5", "text_fg": "#657b83",
        "select_bg": "#268bd2", "select_fg": "#ffffff",
        "highlight": "#b58900", "important": "#dc322f", "code_bg": "#f5f5f5",
        "checklist_done": "#859900", "checklist_pending": "#dc322f"
    },
    "Gruvbox": {
        "bg": "#282828", "card": "#3c3836", "text_fg": "#ebdbb2",
        "select_bg": "#fe8019", "select_fg": "#282828",
        "highlight": "#fabd2f", "important": "#fb4934", "code_bg": "#504945",
        "checklist_done": "#b8bb26", "checklist_pending": "#fb4934"
    }
}

# --- Settings Manager ---
def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {"theme": "Pastel", "last_note": None}
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"theme": "Pastel", "last_note": None}


def save_settings(settings):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)

# --- Main Application ---
class AnnotationViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Annotations")
        self.geometry("1100x750")

        self.settings = load_settings()
        self.current_theme = tk.StringVar(value=self.settings.get("theme", "Pastel"))

        self.all_notes = []
        self.current_note_id = None

        self.setup_fonts_and_styles()
        self.create_widgets()
        self.apply_theme()
        self.load_annotations()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_fonts_and_styles(self):
        self.text_font = font.Font(family=FONT_NAME, size=12)
        self.tree_font = font.Font(family=FONT_NAME, size=11)
        self.mono_font = font.Font(family=MONO_FONT_NAME, size=11)
        self.list_font = font.Font(family=FONT_NAME, size=12, weight="bold")
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

    def create_widgets(self):
        # --- Menu Bar ---
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Notes...", command=self.gui_export_notes)
        file_menu.add_separator()
        file_menu.add_command(label="Backup Now", command=self.gui_backup_notes)
        file_menu.add_command(label="Restore from Backup...", command=self.gui_restore_notes)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)

        self.main_frame = ttk.Frame(self, padding=15)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        left_pane = ttk.Frame(self.paned_window, style="Card.TFrame")
        left_pane.rowconfigure(0, weight=1)
        left_pane.columnconfigure(0, weight=1)

        tree_card = ttk.Frame(left_pane, style="Card.TFrame", padding=10)
        tree_card.grid(row=0, column=0, sticky="nsew")
        tree_card.rowconfigure(0, weight=1)
        tree_card.columnconfigure(0, weight=1)
        self.tree = ttk.Treeview(tree_card, show="tree", selectmode="browse", style="Card.Treeview")
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        search_card = ttk.Frame(left_pane, style="Card.TFrame", padding=10)
        search_card.grid(row=1, column=0, sticky="ew", pady=(10,0))
        search_card.columnconfigure(1, weight=1)

        ttk.Label(search_card, text="Search Tag:", style="Card.TLabel").grid(row=0, column=0, sticky="w")
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_card, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(5,0))
        
        search_button_frame = ttk.Frame(search_card, style="Card.TFrame")
        search_button_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5,0))
        search_button_frame.columnconfigure(0, weight=1)
        search_button_frame.columnconfigure(1, weight=1)
        self.search_button = ttk.Button(search_button_frame, text="Search", command=self.search_by_tag)
        self.search_button.grid(row=0, column=0, sticky="ew")
        self.clear_button = ttk.Button(search_button_frame, text="Clear", command=self.clear_search)
        self.clear_button.grid(row=0, column=1, sticky="ew", padx=(5,0))

        self.paned_window.add(left_pane, weight=1)

        content_card = ttk.Frame(self.paned_window, style="Card.TFrame", padding=10)
        content_card.grid_rowconfigure(1, weight=1)
        content_card.grid_columnconfigure(0, weight=1)

        top_bar = ttk.Frame(content_card, style="Card.TFrame")
        top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        button_container = ttk.Frame(top_bar, style="Card.TFrame")
        button_container.pack(side=tk.LEFT)

        self.edit_button = ttk.Button(button_container, text="Edit", command=self.enter_edit_mode, state=tk.DISABLED)
        self.edit_button.pack(side=tk.LEFT)
        self.delete_button = ttk.Button(button_container, text="Delete", command=self.delete_note, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=(5,0))

        self.save_button = ttk.Button(button_container, text="Save", command=self.save_note)
        self.cancel_button = ttk.Button(button_container, text="Cancel", command=lambda: self.exit_edit_mode(cancel=True))

        theme_frame = ttk.Frame(top_bar, style="Card.TFrame")
        theme_frame.pack(side=tk.RIGHT)
        self.theme_label = ttk.Label(theme_frame, text="Theme:", style="Card.TLabel")
        self.theme_label.pack(side=tk.LEFT, padx=(0, 5))
        self.theme_menu = ttk.Combobox(theme_frame, textvariable=self.current_theme, values=list(THEMES.keys()), width=12, state="readonly")
        self.theme_menu.pack(side=tk.LEFT)

        self.text_area = tk.Text(content_card, wrap=tk.WORD, font=self.text_font, relief=tk.FLAT, padx=15, pady=15)
        self.text_area.grid(row=1, column=0, sticky="nsew")
        self.text_area.config(state=tk.DISABLED)

        self.style_bar = ttk.Label(content_card, text="Use <h>highlight</h>, <i>important</i>, <c>code</c>, [ ] checklist, * list", anchor="center", style="Card.TLabel")
        self.paned_window.add(content_card, weight=3)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Double-1>", self.on_double_click)
        self.theme_menu.bind("<<ComboboxSelected>>", self.on_theme_change)
        self.search_entry.bind("<Return>", self.search_by_tag)

    def apply_theme(self, theme_name=None):
        if theme_name is None: theme_name = self.current_theme.get()
        theme = THEMES[theme_name]
        self.style.configure("TFrame", background=theme["bg"])
        self.style.configure("TPanedWindow", background=theme["bg"])
        self.style.configure("Card.TFrame", background=theme["card"])
        self.style.configure("Card.TLabel", background=theme["card"], foreground=theme["text_fg"])
        self.style.configure("Card.Treeview", background=theme["card"], foreground=theme["text_fg"], fieldbackground=theme["card"], font=self.tree_font, borderwidth=0, rowheight=self.tree_font.metrics("linespace") + 8)
        self.style.map("Card.Treeview", background=[("selected", theme["select_bg"])], foreground=[("selected", theme["select_fg"])])
        self.text_area.configure(bg=theme["card"], fg=theme["text_fg"], insertbackground=theme["text_fg"])
        
        self.text_area.tag_configure("highlight", background=theme["highlight"])
        self.text_area.tag_configure("important", foreground=theme["important"], font=(FONT_NAME, 12, "bold"))
        self.text_area.tag_configure("code", background=theme["code_bg"], font=self.mono_font)
        self.text_area.tag_configure("hidden", elide=True)
        
        self.text_area.tag_configure("checklist_done", foreground=theme["checklist_done"], font=self.list_font)
        self.text_area.tag_configure("checklist_pending", foreground=theme["checklist_pending"], font=self.list_font)
        self.text_area.tag_configure("list_bullet", foreground=theme.get("text_fg", "#000000"), font=self.list_font)

    def parse_note_content(self, content):
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

    def load_annotations(self):
        if not os.path.exists(ANNOTATIONS_FILE):
            self.text_area.config(state=tk.NORMAL); self.text_area.insert("1.0", "No annotations file found."); self.text_area.config(state=tk.DISABLED)
            return
        with open(ANNOTATIONS_FILE, "r") as f:
            try: self.raw_notes = json.load(f)
            except json.JSONDecodeError: self.raw_notes = []
        
        self.all_notes = []
        for i, note_data in enumerate(self.raw_notes):
            title, tags, body = self.parse_note_content(note_data.get('content', ''))
            self.all_notes.append({
                "id": i,
                "timestamp": note_data["timestamp"],
                "title": title,
                "tags": tags,
                "body": body,
                "original_content": note_data["content"]
            })

        self.all_notes.sort(key=lambda x: x["timestamp"], reverse=True)
        self.clear_search()
        self.load_last_note()

    def load_last_note(self):
        last_note_ts = self.settings.get("last_note")
        if last_note_ts:
            for note in self.all_notes:
                if note["timestamp"] == last_note_ts:
                    self.tree.selection_set(note['id'])
                    self.tree.focus(note['id'])
                    self.tree.see(note['id'])
                    break

    def populate_tree(self, notes_to_display):
        for item in self.tree.get_children(): self.tree.delete(item)
        notes_by_date = defaultdict(lambda: defaultdict(list))
        for note in notes_to_display:
            dt = datetime.fromisoformat(note["timestamp"])
            notes_by_date[str(dt.year)][dt.strftime("%B")].append(note)
        
        for year, months in sorted(notes_by_date.items(), reverse=True):
            year_id = self.tree.insert("", "end", text=year, open=True, iid=f"year_{year}")
            for month, notes in sorted(months.items(), key=lambda item: datetime.strptime(item[0], "%B").month, reverse=True):
                month_id = self.tree.insert(year_id, "end", text=month, open=True, iid=f"month_{year}_{month}")
                for note in notes:
                    self.tree.insert(month_id, "end", iid=note['id'], text=note['title'])

    def on_tree_select(self, event):
        selected_id = self.tree.selection()
        if not selected_id or not str(selected_id[0]).isdigit():
            self.edit_button.config(state=tk.DISABLED)
            self.delete_button.config(state=tk.DISABLED)
            return
        self.current_note_id = int(selected_id[0])
        self.edit_button.config(state=tk.NORMAL)
        self.delete_button.config(state=tk.NORMAL)
        self.display_note()

    def on_double_click(self, event):
        if self.tree.selection(): self.enter_edit_mode()

    def display_note(self):
        if self.current_note_id is None: return
        
        note = next((n for n in self.all_notes if n['id'] == self.current_note_id), None)
        if not note: 
            self.text_area.config(state=tk.NORMAL)
            self.text_area.delete("1.0", tk.END)
            self.text_area.config(state=tk.DISABLED)
            self.current_note_id = None
            self.edit_button.config(state=tk.DISABLED)
            self.delete_button.config(state=tk.DISABLED)
            return

        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", note['original_content'])
        self.apply_styling()
        self.text_area.config(state=tk.DISABLED)

    def apply_styling(self):
        content = self.text_area.get("1.0", tk.END)
        for tag in self.text_area.tag_names(): self.text_area.tag_remove(tag, "1.0", tk.END)

        for tag, pattern in [("h", "highlight"), ("i", "important"), ("c", "code")]:
            for match in re.finditer(f"<{tag}>(.*?)</{tag}>", content, re.DOTALL):
                start_tag, end_tag = match.span(0)
                start_content, end_content = match.span(1)
                self.text_area.tag_add(pattern, f"1.0+{start_content}c", f"1.0+{end_content}c")
                self.text_area.tag_add("hidden", f"1.0+{start_tag}c", f"1.0+{start_content}c")
                self.text_area.tag_add("hidden", f"1.0+{end_content}c", f"1.0+{end_tag}c")
        
        for i, line in enumerate(content.split('\n')):
            line_num = i + 1
            if re.match(r'^\s*\[x\].*$', line):
                self.text_area.tag_add("checklist_done", f"{line_num}.0", f"{line_num}.end")
            elif re.match(r'^\s*\[ \].*$', line):
                self.text_area.tag_add("checklist_pending", f"{line_num}.0", f"{line_num}.end")
            elif re.match(r'^\s*([\*\-]|\d+\.)\s+.*$', line):
                self.text_area.tag_add("list_bullet", f"{line_num}.0", f"{line_num}.end")

    def enter_edit_mode(self):
        if self.current_note_id is None: return
        self.edit_button.pack_forget()
        self.delete_button.pack_forget()
        self.save_button.pack(side=tk.LEFT, padx=(0, 5))
        self.cancel_button.pack(side=tk.LEFT)
        self.style_bar.grid(row=2, column=0, sticky="ew", pady=(5, 0))
        self.text_area.config(state=tk.NORMAL)
        for tag in self.text_area.tag_names(): self.text_area.tag_remove(tag, "1.0", tk.END)

    def exit_edit_mode(self, cancel=False):
        self.save_button.pack_forget()
        self.cancel_button.pack_forget()
        self.edit_button.pack(side=tk.LEFT)
        self.delete_button.pack(side=tk.LEFT, padx=(5,0))
        self.style_bar.grid_forget()
        if cancel:
            self.display_note()

    def save_note(self):
        if self.current_note_id is None: return
        new_content = self.text_area.get("1.0", tk.END).strip()
        
        note_to_update = next((n for n in self.all_notes if n['id'] == self.current_note_id), None)
        if note_to_update:
            original_index = -1
            for i, raw_note in enumerate(self.raw_notes):
                if raw_note['timestamp'] == note_to_update['timestamp']:
                    original_index = i
                    break
            if original_index != -1:
                 self.raw_notes[original_index]['content'] = new_content

        with open(ANNOTATIONS_FILE, "w") as f:
            json.dump(self.raw_notes, f, indent=2)
        
        self.load_annotations()
        self.exit_edit_mode(cancel=True)

    def delete_note(self):
        if self.current_note_id is None: return

        note_to_delete = next((n for n in self.all_notes if n['id'] == self.current_note_id), None)
        if not note_to_delete: return

        if messagebox.askyesno("Delete Note", f"Are you sure you want to delete the note titled: \n'{note_to_delete['title']}'?"):
            self.raw_notes = [n for n in self.raw_notes if n['timestamp'] != note_to_delete['timestamp']]
            with open(ANNOTATIONS_FILE, "w") as f:
                json.dump(self.raw_notes, f, indent=2)
            self.load_annotations()

    def on_theme_change(self, event):
        self.settings["theme"] = self.current_theme.get()
        self.apply_theme()
        if self.current_note_id is not None:
            self.display_note()

    def on_closing(self):
        if self.current_note_id is not None:
            note = next((n for n in self.all_notes if n['id'] == self.current_note_id), None)
            if note:
                self.settings["last_note"] = note["timestamp"]
        save_settings(self.settings)
        self.destroy()

    def search_by_tag(self, event=None):
        search_term = self.search_var.get().strip().lower()
        if not search_term:
            self.populate_tree(self.all_notes)
            return
        
        if search_term.startswith('#'): search_term = search_term[1:]

        filtered_notes = [
            note for note in self.all_notes 
            if any(search_term == tag.lower() for tag in note['tags'])
        ]
        self.populate_tree(filtered_notes)

    def clear_search(self):
        self.search_var.set("")
        self.populate_tree(self.all_notes)
        self.tree.focus_set()

    # --- GUI Wrappers for Utils ---
    def gui_export_notes(self):
        target_dir = filedialog.askdirectory(title="Select Export Directory")
        if target_dir:
            if export_notes(target_dir):
                messagebox.showinfo("Export Successful", f"All notes have been exported to {target_dir}")
            else:
                messagebox.showerror("Export Failed", "Could not export notes. See terminal for details.")

    def gui_backup_notes(self):
        backup_path = backup_notes()
        if backup_path:
            messagebox.showinfo("Backup Successful", f"Backup created at:\n{backup_path}")
        else:
            messagebox.showerror("Backup Failed", "Could not create backup. See terminal for details.")

    def gui_restore_notes(self):
        backups = list_backups()
        if not backups:
            messagebox.showinfo("Restore", "No backups found.")
            return

        # We need a new Toplevel window to ask the user which backup to restore
        win = tk.Toplevel(self)
        win.title("Restore from Backup")
        ttk.Label(win, text="Select a backup to restore:").pack(padx=10, pady=10)
        
        listbox = tk.Listbox(win, width=50, height=15)
        listbox.pack(padx=10, pady=10)
        for b in backups:
            listbox.insert(tk.END, b)

        def on_restore():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a backup file.")
                return
            
            selected_backup = listbox.get(selection[0])
            if messagebox.askyesno("Confirm Restore", f"Are you sure you want to restore from:\n{selected_backup}\n\nThis will overwrite your current notes."):
                if restore_notes(selected_backup):
                    messagebox.showinfo("Restore Successful", "Notes restored. The application will now reload.")
                    win.destroy()
                    self.load_annotations() # Reload notes
                else:
                    messagebox.showerror("Restore Failed", "Could not restore notes. See terminal for details.")
        
        ttk.Button(win, text="Restore", command=on_restore).pack(pady=5)
        ttk.Button(win, text="Cancel", command=win.destroy).pack(pady=5)

if __name__ == "__main__":
    app = AnnotationViewer()
    app.mainloop()