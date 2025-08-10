# Arquivo de Arquivo do Projeto Anno

Este arquivo contém um resumo do projeto Anno e o conteúdo completo de todos os arquivos de código fonte, permitindo a recriação do aplicativo em um novo ambiente.

---

### Conteúdo do Arquivo: /home/sam/Projects/Annotation/PROJECT_SUMMARY.md

```markdown
# Resumo do Projeto: Anno - Aplicativo de Anotações

Este documento resume o estado atual e as funcionalidades do aplicativo "Anno", desenvolvido para Linux Mint XFCE.

## 1. Objetivo do Aplicativo

Um aplicativo leve para anotações que permite:
*   Capturar anotações rapidamente via terminal (usando `nano`).
*   Visualizar anotações em uma interface gráfica (GUI) organizada.
*   Visualizar anotações diretamente no terminal.
*   Manter as anotações persistentes e organizadas por data.

## 2. Estrutura de Arquivos e Localização

*   **Diretório Raiz do Projeto:** `/home/sam/Projects/Annotation/`
*   **Script Principal (Shell):** `/home/sam/Projects/Annotation/anno` (copiado para `/usr/local/bin/` para uso global)
*   **Módulos Python do App:** `/home/sam/Projects/Annotation/anno_app/`
    *   `anno_viewer.py`: Código da interface gráfica (GUI).
    *   `anno_terminal_viewer.py`: Código do visualizador de terminal.
*   **Arquivo de Dados:** `~/.local/share/annotations.json` (armazena todas as anotações).
*   **Arquivo de Configurações:** `~/.config/anno/settings.json` (armazena o tema selecionado e a última nota aberta).
*   **Pacote de Instalação:** `anno_deb_build.deb` (localizado em `/home/sam/Projects/Annotation/`).

## 3. Comandos Principais

Após a instalação do pacote `.deb` (ou cópia manual do script `anno` para `/usr/local/bin/`):

*   `anno`: Abre o editor `nano` para criar uma nova anotação.
    *   **Como usar `nano`:** `Ctrl+X` para sair, `Y` para salvar, `Enter` para confirmar o nome do arquivo.
*   `anno -o`: Abre a interface gráfica (GUI) do aplicativo.
*   `anno -t`: Exibe todas as anotações diretamente no terminal.

## 4. Funcionalidades da Interface Gráfica (`anno -o`)

*   **Layout:** Duas colunas (`PanedWindow` redimensionável).
    *   **Coluna Esquerda:** Visualização em árvore (`ttk.Treeview`) organizada por Ano > Mês > Anotação (Dia, Hora).
    *   **Coluna Direita:** Área de texto para exibir o conteúdo da anotação selecionada.
*   **Edição de Anotações:**
    *   Botão "Edit" para entrar no modo de edição.
    *   Botões "Save" e "Cancel" para gerenciar as alterações.
    *   **Estilização com Tags:** Suporte a tags pseudo-HTML para formatação visual:
        *   `<h>texto</h>`: Texto destacado (highlight).
        *   `<i>texto</i>`: Texto importante (negrito, cor diferente).
        *   `<c>texto</c>`: Texto de código (fonte monoespaçada, fundo diferente).
    *   Barra de ajuda com as tags visível no modo de edição.
*   **Temas Visuais:** Seletor de temas (dropdown) com as seguintes opções:
    *   Pastel (padrão)
    *   Dark
    *   Light
    *   Nord
    *   Solarized Light
    *   Gruvbox
*   **Persistência:**
    *   O tema selecionado é salvo e carregado automaticamente na próxima inicialização.
    *   A última anotação visualizada é salva e reaberta automaticamente na próxima inicialização.

## 5. Funcionalidades do Visualizador de Terminal (`anno -t`)

*   Exibe as anotações de forma hierárquica (Ano > Mês > Dia > Anotação).
*   Aplica cores ANSI e estilos (negrito) para as tags `<h>`, `<i>` e `<c>`, tornando a visualização no terminal organizada e legível.

## 6. Dependências

Para que o aplicativo funcione, as seguintes dependências devem estar instaladas no sistema:

*   `python3`
*   `python3-tk` (para a GUI)
*   `jq` (para processamento JSON no script `anno`)

## 7. Instalação em Outras Máquinas Linux Mint/Ubuntu

Um pacote Debian (`.deb`) foi gerado para facilitar a instalação:

*   **Localização do Pacote:** `/home/sam/Projects/Annotation/anno_deb_build.deb`
*   **Comando de Instalação:**
    ```bash
    sudo dpkg -i /caminho/para/anno_deb_build.deb
    sudo apt-get install -f  # Para resolver dependências, se necessário
    ```

## 8. Próximos Passos (se desejar continuar)

*   **Novas Funcionalidades:** Adicionar mais tags de estilização, funcionalidade de busca, exportação de anotações, etc.
*   **Refinamento Visual:** Embora o Tkinter tenha limitações, pequenos ajustes de padding, fontes e cores podem sempre ser explorados.
*   **Otimização:** Para sistemas extremamente limitados, pode-se investigar otimizações de código Python ou considerar linguagens de menor nível (C/C++), embora com maior complexidade de desenvolvimento.

Este resumo deve ser suficiente para você ou qualquer outro desenvolvedor entender o projeto e continuar trabalhando nele.
```

---

### Conteúdo do Arquivo: /home/sam/Projects/Annotation/anno

```bash
#!/bin/bash

# --- Configuration ---
ANNOTATIONS_FILE="${HOME}/.local/share/annotations.json"
VIEWER_ORIGINAL_SCRIPT="/home/sam/Projects/Annotation/anno_app/anno_viewer.py"
VIEWER_TERMINAL_SCRIPT="/home/sam/Projects/Annotation/anno_app/anno_terminal_viewer.py"

# --- Functions ---

# Function to create the annotations file and directory if they don't exist
ensure_annotations_file_exists() {
    mkdir -p "$(dirname "${ANNOTATIONS_FILE}")"
    if [ ! -f "${ANNOTATIONS_FILE}" ]; then
        echo "[]" > "${ANNOTATIONS_FILE}"
    fi
}

# Function to add a new annotation
add_annotation() {
    # Check for jq dependency first
    if ! command -v jq &> /dev/null; then
        echo "Error: 'jq' is not installed. Please install it to continue."
        echo "On Debian/Ubuntu: sudo apt-get install jq"
        exit 1
    fi

    # Create a temporary file for the note
    TMP_FILE=$(mktemp)

    # Open nano to write the annotation
    nano "${TMP_FILE}"

    # Check if the user actually wrote something
    if [ -s "${TMP_FILE}" ]; then
        CONTENT=$(<"${TMP_FILE}")
        TIMESTAMP=$(date --iso-8601=seconds)

        # Use jq to safely add the new entry to the JSON array
        if jq --arg ts "${TIMESTAMP}" --arg content "${CONTENT}" '. += [{timestamp: $ts, content: $content}]' "${ANNOTATIONS_FILE}" > "${ANNOTATIONS_FILE}.tmp"; then
            mv "${ANNOTATIONS_FILE}.tmp" "${ANNOTATIONS_FILE}"
            echo "Annotation saved."
        else
            echo "Error: Failed to save annotation. Your note content is still in ${TMP_FILE}"
            # No rm "${TMP_FILE}" here, so the user can recover the note
            exit 1
        fi
    else
        echo "Annotation canceled."
    fi

    # Clean up the temporary file
    rm "${TMP_FILE}"
}

# Function to open the viewer
open_viewer() {
    local viewer_script="$1"
    python3 "${viewer_script}"
}

# --- Main Logic ---

ensure_annotations_file_exists

# Check for flags
if [ "$1" == "-o" ]; then
    open_viewer "${VIEWER_ORIGINAL_SCRIPT}"
elif [ "$1" == "-t" ]; then
    open_viewer "${VIEWER_TERMINAL_SCRIPT}"
else
    add_annotation
fi
```

---

### Conteúdo do Arquivo: /home/sam/Projects/Annotation/anno_app/anno_viewer.py

```python
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
        if not cancel: self.display_note()

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
```

---

### Conteúdo do Arquivo: /home/sam/Projects/Annotation/anno_app/anno_viewer_canvas.py

```python
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

# --- Rounded Frame Widget ---
class RoundedFrame(tk.Canvas):
    def __init__(self, parent, corner_radius, padding, bg_color, **kwargs):
        super().__init__(parent, **kwargs)
        self.corner_radius = corner_radius
        self.padding = padding
        self.bg_color = bg_color
        self.configure(highlightthickness=0, borderwidth=0)
        self.bind("<Configure>", self._draw_rounded_rect)

        self.frame = ttk.Frame(self, style="RoundedFrame.TFrame")
        self.create_window(self.padding, self.padding, window=self.frame, anchor="nw")

    def _draw_rounded_rect(self, event=None):
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()

        # Draw the rounded rectangle
        points = [
            self.corner_radius, 0,
            width - self.corner_radius, 0,
            width, self.corner_radius,
            width, height - self.corner_radius,
            width - self.corner_radius, height,
            self.corner_radius, height,
            0, height - self.corner_radius,
            0, self.corner_radius
        ]
        self.create_polygon(points, smooth=True, fill=self.bg_color)

        # Adjust the inner frame size
        self.frame.place(x=self.padding, y=self.padding, width=width - 2 * self.padding, height=height - 2 * self.padding)

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

        # Left Pane: Treeview in a "Card"
        self.tree_card = RoundedFrame(self.paned_window, corner_radius=20, padding=10, bg_color="white")
        self.tree = ttk.Treeview(self.tree_card.frame, show="tree", selectmode="browse", style="Card.Treeview")
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.paned_window.add(self.tree_card, weight=1)

        # Right Pane: Content in a "Card"
        self.content_card = RoundedFrame(self.paned_window, corner_radius=20, padding=10, bg_color="white")
        self.content_card.frame.grid_rowconfigure(1, weight=1)
        self.content_card.frame.grid_columnconfigure(0, weight=1)

        top_bar = ttk.Frame(self.content_card.frame, style="Card.TFrame")
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

        self.text_area = tk.Text(self.content_card.frame, wrap=tk.WORD, font=self.text_font, relief=tk.FLAT, padx=15, pady=15)
        self.text_area.grid(row=1, column=0, sticky="nsew")
        self.text_area.config(state=tk.DISABLED)

        self.style_bar = ttk.Label(self.content_card.frame, text="Use <h>highlight</h>, <i>important</i>, <c>code</c>", anchor="center", style="Card.TLabel")
        self.paned_window.add(self.content_card, weight=3)

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
        self.style_bar.configure(style="Card.TLabel")

        # Update RoundedFrame background colors
        self.tree_card.bg_color = theme["card"]
        self.tree_card._draw_rounded_rect() # Redraw
        self.content_card.bg_color = theme["card"]
        self.content_card._draw_rounded_rect() # Redraw

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
            except (json.JSONDecodeError, IOError): self.all_notes = []
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
        if not cancel: self.display_note()

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
```
