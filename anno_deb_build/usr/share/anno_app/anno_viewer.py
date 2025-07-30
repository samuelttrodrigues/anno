import tkinter as tk
from tkinter import ttk, font
import json
from datetime import datetime
import os
from collections import defaultdict
import re

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
        "highlight": "#FFFACD", "important": "#FF4500", "code_bg": "#D3D3D3"
    },
    "Dark": {
        "bg": "#2E2E2E", "card": "#3C3C3C", "text_fg": "#E0E0E0",
        "select_bg": "#BB86FC", "select_fg": "#000000",
        "highlight": "#4A4A4A", "important": "#CF6679", "code_bg": "#555555"
    },
    "Light": {
        "bg": "#F0F0F0", "card": "#FFFFFF", "text_fg": "#000000",
        "select_bg": "#0078D7", "select_fg": "#FFFFFF",
        "highlight": "#FFFF00", "important": "#D93025", "code_bg": "#E8EAED"
    },
    "Nord": {
        "bg": "#2E3440", "card": "#3B4252", "text_fg": "#D8DEE9",
        "select_bg": "#88C0D0", "select_fg": "#2E3440",
        "highlight": "#5E81AC", "important": "#BF616A", "code_bg": "#4C566A"
    },
    "Solarized Light": {
        "bg": "#fdf6e3", "card": "#eee8d5", "text_fg": "#657b83",
        "select_bg": "#268bd2", "select_fg": "#ffffff",
        "highlight": "#b58900", "important": "#dc322f", "code_bg": "#f5f5f5"
    },
    "Gruvbox": {
        "bg": "#282828", "card": "#3c3836", "text_fg": "#ebdbb2",
        "select_bg": "#fe8019", "select_fg": "#282828",
        "highlight": "#fabd2f", "important": "#fb4934", "code_bg": "#504945"
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
        self.current_note_index = None

        self.setup_fonts_and_styles()
        self.create_widgets()
        self.apply_theme()
        self.load_annotations()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_fonts_and_styles(self):
        self.text_font = font.Font(family=FONT_NAME, size=12)
        self.tree_font = font.Font(family=FONT_NAME, size=11)
        self.mono_font = font.Font(family=MONO_FONT_NAME, size=11)
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

    def create_widgets(self):
        self.main_frame = ttk.Frame(self, padding=15)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        tree_card = ttk.Frame(self.paned_window, style="Card.TFrame", padding=10)
        self.tree = ttk.Treeview(tree_card, show="tree", selectmode="browse", style="Card.Treeview")
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.paned_window.add(tree_card, weight=1)

        content_card = ttk.Frame(self.paned_window, style="Card.TFrame", padding=10)
        content_card.grid_rowconfigure(1, weight=1)
        content_card.grid_columnconfigure(0, weight=1)

        top_bar = ttk.Frame(content_card, style="Card.TFrame")
        top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.edit_button = ttk.Button(top_bar, text="Edit", command=self.enter_edit_mode, state=tk.DISABLED)
        self.edit_button.pack(side=tk.LEFT)
        self.save_button = ttk.Button(top_bar, text="Save", command=self.save_note)
        self.cancel_button = ttk.Button(top_bar, text="Cancel", command=lambda: self.exit_edit_mode(cancel=True))

        theme_frame = ttk.Frame(top_bar, style="Card.TFrame")
        theme_frame.pack(side=tk.RIGHT)
        self.theme_label = ttk.Label(theme_frame, text="Theme:", style="Card.TLabel")
        self.theme_label.pack(side=tk.LEFT, padx=(0, 5))
        self.theme_menu = ttk.Combobox(theme_frame, textvariable=self.current_theme, values=list(THEMES.keys()), width=12, state="readonly")
        self.theme_menu.pack(side=tk.LEFT)

        self.text_area = tk.Text(content_card, wrap=tk.WORD, font=self.text_font, relief=tk.FLAT, padx=15, pady=15)
        self.text_area.grid(row=1, column=0, sticky="nsew")
        self.text_area.config(state=tk.DISABLED)

        self.style_bar = ttk.Label(content_card, text="Use <h>highlight</h>, <i>important</i>, <c>code</c>", anchor="center", style="Card.TLabel")
        self.paned_window.add(content_card, weight=3)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.theme_menu.bind("<<ComboboxSelected>>", self.on_theme_change)

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

    def load_annotations(self):
        if not os.path.exists(ANNOTATIONS_FILE):
            self.text_area.config(state=tk.NORMAL); self.text_area.insert("1.0", "No annotations file found."); self.text_area.config(state=tk.DISABLED)
            return
        with open(ANNOTATIONS_FILE, "r") as f:
            try: self.all_notes = json.load(f)
            except json.JSONDecodeError: self.all_notes = []
        self.all_notes.sort(key=lambda x: x["timestamp"], reverse=True)
        self.populate_tree()
        self.load_last_note()

    def load_last_note(self):
        last_note_ts = self.settings.get("last_note")
        if last_note_ts:
            for i, note in enumerate(self.all_notes):
                if note["timestamp"] == last_note_ts:
                    self.tree.selection_set(i)
                    self.tree.focus(i)
                    self.tree.see(i)
                    break

    def populate_tree(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        notes_by_date = defaultdict(lambda: defaultdict(list))
        for i, note in enumerate(self.all_notes):
            dt = datetime.fromisoformat(note["timestamp"])
            notes_by_date[str(dt.year)][dt.strftime("%B")].append((i, note))
        for year, months in sorted(notes_by_date.items(), reverse=True):
            year_id = self.tree.insert("", "end", text=year, open=True, iid=f"year_{year}")
            for month, notes in sorted(months.items(), key=lambda item: datetime.strptime(item[0], "%B").month, reverse=True):
                month_id = self.tree.insert(year_id, "end", text=month, open=False, iid=f"month_{year}_{month}")
                for index, note in notes:
                    dt = datetime.fromisoformat(note["timestamp"])
                    self.tree.insert(month_id, "end", iid=index, text=dt.strftime("%d, %I:%M %p"))

    def on_tree_select(self, event):
        selected_id = self.tree.selection()
        if not selected_id or not str(selected_id[0]).isdigit():
            self.edit_button.config(state=tk.DISABLED)
            return
        self.current_note_index = int(selected_id[0])
        self.edit_button.config(state=tk.NORMAL)
        self.display_note()

    def display_note(self):
        if self.current_note_index is None: return
        note = self.all_notes[self.current_note_index]
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete("1.0", tk.END)
        content = note['content']
        self.text_area.insert("1.0", content)
        self.apply_styling()
        self.text_area.config(state=tk.DISABLED)

    def apply_styling(self):
        content = self.text_area.get("1.0", tk.END)
        for tag in ["highlight", "important", "code", "hidden"]: self.text_area.tag_remove(tag, "1.0", tk.END)
        for tag, pattern in [("h", "highlight"), ("i", "important"), ("c", "code")]:
            for match in re.finditer(f"<{tag}>(.*?)</{tag}>", content, re.DOTALL):
                start_tag, end_tag = match.span(0)
                start_content, end_content = match.span(1)
                self.text_area.tag_add(pattern, f"1.0+{start_content}c", f"1.0+{end_content}c")
                self.text_area.tag_add("hidden", f"1.0+{start_tag}c", f"1.0+{start_content}c")
                self.text_area.tag_add("hidden", f"1.0+{end_content}c", f"1.0+{end_tag}c")

    def enter_edit_mode(self):
        if self.current_note_index is None: return
        self.edit_button.pack_forget()
        self.save_button.pack(side=tk.LEFT, padx=(0, 5))
        self.cancel_button.pack(side=tk.LEFT)
        self.style_bar.grid(row=2, column=0, sticky="ew", pady=(5, 0))
        self.text_area.config(state=tk.NORMAL)
        # Remove styling for editing
        for tag in ["highlight", "important", "code", "hidden"]: self.text_area.tag_remove(tag, "1.0", tk.END)

    def exit_edit_mode(self, cancel=False):
        self.save_button.pack_forget()
        self.cancel_button.pack_forget()
        self.edit_button.pack(side=tk.LEFT)
        self.style_bar.grid_forget()
        if cancel:
            self.display_note()

    def save_note(self):
        if self.current_note_index is None: return
        new_content = self.text_area.get("1.0", tk.END).strip()
        self.all_notes[self.current_note_index]['content'] = new_content
        with open(ANNOTATIONS_FILE, "w") as f:
            json.dump(self.all_notes, f, indent=2)
        self.exit_edit_mode()
        self.display_note()

    def on_theme_change(self, event):
        self.settings["theme"] = self.current_theme.get()
        self.apply_theme()
        if self.current_note_index is not None:
            self.display_note()

    def on_closing(self):
        if self.current_note_index is not None:
            self.settings["last_note"] = self.all_notes[self.current_note_index]["timestamp"]
        save_settings(self.settings)
        self.destroy()

if __name__ == "__main__":
    if not os.path.exists(ANNOTATIONS_FILE):
        os.makedirs(os.path.dirname(ANNOTATIONS_FILE), exist_ok=True)
        dummy_data = [
            {"timestamp": "2025-07-22T10:00:00", "content": "This is a <h>highlighted</h> note."},
            {"timestamp": "2025-07-22T11:30:00", "content": "This is an <i>important</i> note."},
            {"timestamp": "2025-07-21T15:30:00", "content": "This is a note with some <c>code_example()</c>."}
        ]
        with open(ANNOTATIONS_FILE, "w") as f: json.dump(dummy_data, f, indent=2)

    app = AnnotationViewer()
    app.mainloop()