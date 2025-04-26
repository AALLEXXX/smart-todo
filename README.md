## AlexTodo

A simple and elegant **To-Do** desktop application built with **PyQt6**. Organize tasks by status and priority, switch between light and dark themes, and archive completed tasks.

---

## Features

- **Task Management**: Create, edit, delete, and archive tasks.
- **Drag & Drop**: Move tasks between columns: Backlog, In Progress, Blocked, Done.
- **Priority Filters**: Show tasks by Low, Medium, or High priority.
- **Themes**: Toggle between light and dark modes; preference saved between sessions.
- **Database**: SQLite for local task storage; easy setup and portability.

---

## Prerequisites

- Python 3.11 or higher
- [Poetry](https://python-poetry.org/) for dependency management
- [PyInstaller](https://www.pyinstaller.org/) for building executables (optional)

---

## Installation & Setup

Use the provided `Makefile` to simplify setup and common tasks.

```bash
make install     # install dependencies via Poetry
make compile-ui  # compile Qt .ui files into Python modules
make init-db     # create and initialize the SQLite database
make run         # launch the application
make build       # package the app into a standalone executable with PyInstaller
make clean       # remove build artifacts and temporary files
```

---

## Building a Standalone Executable

Use PyInstaller to package the app into a single executable. You can either use a spec file or run the command directly.

### 1. Spec File (`Todo.spec`)

Create `Todo.spec` in the project root with the following datas configuration:

```python
# Todo.spec

datas = [
    ('styles', 'styles'),
    ('ui', 'ui'),
    ('user_config.ini', '.'),
    ('data', 'data')
]
```  

### 2. PyInstaller Command

Run PyInstaller with icon, data folders, and windowed mode:

```bash
pyinstaller \
  --name "AlexTodo" \
  --icon "icons/app_icns.icns" \
  --add-data "styles:styles" \
  --add-data "ui:ui" \
  --add-data "user_config.ini:." \
  --add-data "data/todo.db:data" \
  --windowed main.py
```  

The built application will be in the `dist/AlexTodo` folder.

---

## Project Structure

```
.
├── README.md            # This file
├── components           # UI components (TaskCard)
│   └── task_card.py
├── config.py            # Settings and constants
├── data                 # Database scripts and file
│   ├── init_db.py       # DB initialization script
│   └── todo.db          # SQLite database (after init)
├── db.py                # CRUD operations on tasks
├── icons                # Application icons
├── main.py              # Entry point
├── poetry.lock          # Poetry lock file
├── pyproject.toml       # Poetry project config
├── styles               # QSS style sheets
├── ui                   # Qt UI definitions and generated modules
├── ui_uploader.py       # Compile `.ui` files to Python
└── windows              # Dialog windows implementation
```

---

## Configuration

- **User Settings** are saved in `user_config.ini` in the working directory.
- To reset the database, delete `data/todo.db` and rerun the init script.

---

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-name`).
3. Commit your changes (`git commit -m 'Add feature'`).
4. Push to the branch (`git push origin feature-name`).
5. Open a pull request.

---

## License

MIT License. See [LICENSE](LICENSE) for details.

