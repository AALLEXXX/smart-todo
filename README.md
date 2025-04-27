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

## Development Setup

Use the provided `Makefile` to set up the development environment and git hooks:

```bash
make install-dev   # install runtime + dev dependencies and activate pre-commit hooks
```

---

## Makefile Reference

| Target           | Description                                                                 |
| ---------------- | --------------------------------------------------------------------------- |
| `make install`   | Install runtime dependencies via Poetry                                      |
| `make install-dev` | Install runtime and dev dependencies, and install pre-commit hooks         |
| `make compile-ui` | Compile all `.ui` files into Python modules                                  |
| `make init-db`    | Initialize the SQLite database                                               |
| `make run`        | Run the application                                                           |
| `make lint`       | Run Ruff linting and formatting checks                                        |
| `make build`      | Build a standalone executable using PyInstaller                               |
| `make clean`      | Remove build artifacts (`build/`, `dist/`, `*.spec`)                          |

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
  --icon "app/icons/app_icns.icns" \
  --add-data "app/styles:styles" \
  --add-data "app/ui:ui" \
  --add-data "app/user_config.ini:." \
  --add-data "app/data/todo.db:data" \
  --windowed main.py
```  

The built application will be in the `dist/AlexTodo` folder.


## Configuration

- **User Settings** are saved in `user_config.ini` in the working directory.
- To reset the database, delete `data/todo.db` and rerun the init script.

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed list of changes by version.

---

## Contributing

1. Fork the repository.  
2. Create a new branch (`git checkout -b feature-name`).  
3. Run `make install-dev` and ensure `make lint` passes without errors.  
4. Commit your changes and push to your branch (`git push origin feature-name`).  
5. Open a pull request; pre-commit hooks will run automatically.

---

## License

MIT License. See [LICENSE](LICENSE) for details.

