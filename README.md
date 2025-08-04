# Anno - A Simple Note-Taking Application

Anno is a lightweight, fast, and versatile note-taking application designed for the command line, but with a powerful GUI as well. It allows you to quickly jot down, edit, search, and manage your notes without leaving the terminal, while also providing a rich graphical interface for more complex tasks.

![Anno GUI Screenshot](https://i.imgur.com/YOUR_SCREENSHOT_URL.png)  <!-- Placeholder: You can upload a screenshot and replace this URL -->

---

## Installation (for Ubuntu/Debian Users)

1.  **Download the `.deb` package:** Go to the [**Releases Page**](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY/releases) on GitHub and download the `anno_deb_build.deb` file from the latest release.
2.  **Install the package:** Open your terminal, navigate to the directory where you downloaded the file, and run:

    ```bash
    sudo dpkg -i anno_deb_build.deb
    ```

3.  **Run the application:** You can now use `anno` from anywhere in your terminal!

---

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

## Usage

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

---

## For Developers

### Building from Source

If you want to build the `.deb` package from the source code, follow these steps.

1.  **Prerequisites:**

    Make sure you have the following installed:

    *   `python3`
    *   `python3-tk` (for the GUI)
    *   `jq` (for JSON processing in the shell script)
    *   `dpkg-deb` (for building the package)

    You can usually install these on a Debian-based system (like Ubuntu) with:
    ```bash
    sudo apt-get update
    sudo apt-get install python3 python3-tk jq dpkg-deb
    ```

2.  **Build the Package:**

    From the root of the project directory, run the build command:
    ```bash
    dpkg-deb --build anno_deb_build
    ```
    This will create the `anno_deb_build.deb` file in the project root.

### Contributing

Contributions are welcome! If you have ideas for new features or have found a bug, please open an issue on the GitHub repository. If you'd like to contribute code, please fork the repository and submit a pull request.

### License

This project is open-source and available under the [MIT License](LICENSE). <!-- You would need to add a LICENSE file for this link to work -->