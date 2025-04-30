# AlexTodo

A simple and elegant **To‑Do & Habit** desktop application built with **PyQt6**. Organize tasks by status and priority, track daily habits with interactive checklists and calendars, and switch between light and dark themes.

---

## Features

### Task Management
- **Create / Edit / Delete** tasks with title, description, priority, status, and due date.
- **Drag & Drop** tasks between columns: Backlog, In Progress, Blocked, Done.
- **Archive** completed tasks and view them in an archive dialog.
- **Priority Filters**: Show or hide Low, Medium, High priority tasks.

### Habit Tracking
- **Habit Creation**: Define habits with title, end date, frequency (`daily`, `weekdays`, `weekends`), optional reward, and “Hard Mode” toggle.
- **Dynamic Checklist**: Add an arbitrary number of checklist items per habit via a plus‑button interface.
- **Today View**: Automatic checklist view for today’s habits matching frequency and active period; partial checks saved immediately.
- **Habit Calendar**: Visual heatmap calendar showing completion history; double‑click a card to view full details.
- **Habit Detail Dialog**: Minimalist dialog with status (Active / Completed / Failed), start/end dates, current streak, reward, mode, and item list.
- **Failure Logic**: For `Hard Mode` habits, any missed required day marks the habit as **Failed** and removes it from the Today view.

### Themes & Styling
- **Light / Dark Mode** toggle; user preference persisted in config.
- **Consistent QSS**: Shared base styles plus theme overrides, including custom styling for habit calendars and detail dialogs.

### Development & Build
- **Python** 3.11+
- **Poetry** for dependency management
- **PyInstaller** for packaging (optional)

---

## Development Setup

Clone the repo and install dependencies:

```bash
make install-dev    # install with dev dependencies + pre‑commit hooks
```

Set up the database:

```bash
make init-db        # initialize SQLite
```

Set up the database and demo data:

```bash
make init-db-dev
```

Compile all Qt `.ui` files:

```bash
make compile-ui
```

Run the app:

```bash
make run
```

Run linters and formatters:

```bash
make lint
```

Build standalone executable:

```bash
make build
```

Clean build artifacts:

```bash
make clean
```

---

## Configuration

- **User Settings** (window geometry, theme) stored in `user_config.ini`.
- **Reset DB**: Delete `app/data/todo.db` and rerun `make init-db`.

---

## Contributing

1. Fork the repository and create a feature branch (`git checkout -b feature-name`).
2. Install dependencies and run linters:
   ```bash
   make install-dev
   make lint
   ```
3. Commit your changes and push to your branch.
4. Open a Pull Request; tests and pre‑commit hooks will run automatically.

---

## License

[MIT License](LICENSE)
