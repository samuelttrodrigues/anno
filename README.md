
# Anno - A Simple Note-Taking Application

Anno is a lightweight, fast, and versatile note-taking application designed for the command line, but with a powerful GUI as well. It allows you to quickly jot down, edit, search, and manage your notes without leaving the terminal, while also providing a rich graphical interface for more complex tasks.

![Anno GUI Screenshot](https://i.imgur.com/YOUR_SCREENSHOT_URL.png)  <!-- Placeholder: You can upload a screenshot and replace this URL -->

## Features

*   **Fast Note Creation:** Create a new note instantly from the command line with `anno`.
*   **Dual Interfaces:** Choose between a full-featured graphical UI (`anno -o`) or a fast, interactive terminal UI (`anno -t`).
*   **Rich Text Formatting:** Add styling to your notes:
    *   `<h>highlight</h>` for highlighted text.
    *   `<i>important</i>` for bold, red text.
    *   `<c>code</c>` for monospaced code blocks.
    *   `[ ]` and `[x]` for checklists.
    *   `*` or `1.` for bulleted or numbered lists.
*   **Tag-Based Search:** Organize and find your notes with tags (e.g., `[#project, #ideas]`). Search from both the GUI and the terminal (`anno -s <tag>`).
*   **Data Portability:**
    *   **Export:** Export all your notes to individual `.txt` files with `anno --export <directory>`.
    *   **Backup & Restore:** Create a timestamped `.zip` backup of your notes database with `anno --backup` and restore from it with `anno --restore`.
*   **Customizable Themes:** The GUI features multiple color themes to suit your preference.

## Installation

Anno is designed to be run from a local directory or installed system-wide on Linux.

### 1. Prerequisites

Make sure you have the following installed:

*   `python3`
*   `python3-tk` (for the GUI)
*   `jq` (for JSON processing in the shell script)

You can usually install these on a Debian-based system (like Ubuntu) with:
```bash
sudo apt-get update
sudo apt-get install python3 python3-tk jq
```

### 2. System-Wide Installation

To make the `anno` command available from anywhere in your terminal, follow these steps:

1.  Navigate to your project directory:
    ```bash
    cd /path/to/your/Annotation
    ```
2.  Run the following commands to copy the application files to system directories:
    ```bash
    # Create the directory for the application's Python files
    sudo mkdir -p /usr/share/anno_app

    # Copy the Python scripts
    sudo cp -r ./anno_app/* /usr/share/anno_app/

    # Copy the main executable script
    sudo cp ./anno /usr/local/bin/anno
    ```

## Usage

### Command-Line Options

| Command                 | Description                                         |
| ----------------------- | --------------------------------------------------- |
| `anno`                  | Create a new note in your default text editor.      |
| `anno -o`               | Open the graphical user interface (GUI).            |
| `anno -t`               | Open the interactive terminal user interface (TUI). |
| `anno -s <tag>`         | Search for notes containing a specific tag.         |
| `anno --export <dir>`   | Export all notes as `.txt` files to a directory.    |
| `anno --backup`         | Create a compressed backup of the notes database.   |
| `anno --restore`        | Restore notes from an existing backup.              |
| `anno -h`, `--help`     | Show the help message.                              |

### Terminal UI Commands

When using the interactive terminal (`anno -t`), use the following commands:

| Command      | Action                                              |
| ------------ | --------------------------------------------------- |
| `<number>`   | **Read** the full content of the specified note.    |
| `<number>e` | **Edit** the specified note in your text editor.    |
| `<number>d` | **Delete** the specified note after confirmation.   |
| `quit`       | Exit the terminal interface.                        |

## Contributing

Contributions are welcome! If you have ideas for new features or have found a bug, please open an issue on the GitHub repository. If you'd like to contribute code, please fork the repository and submit a pull request.

## License

This project is open-source and available under the [MIT License](LICENSE). <!-- You would need to add a LICENSE file for this link to work -->
