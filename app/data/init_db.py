import os
import sqlite3

DB_PATH = "app/data/todo.db"


def init_db():
    if os.path.exists(DB_PATH):
        print("База данных уже существует.")
        return

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Существующая таблица задач
    cursor.execute(
        """
        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT CHECK(priority IN ('Low', 'Medium', 'High')) NOT NULL,
            status TEXT CHECK(status IN ('Backlog', 'In Progress', 'Blocked', 'Done')) NOT NULL,
            created_at TEXT NOT NULL,
            due_date TEXT,
            completed_at TEXT,
            sort_index INTEGER NOT NULL DEFAULT 0,
            is_archived INTEGER NOT NULL DEFAULT 0
        )
    """
    )

    # Новая таблица привычек
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            reward TEXT,
            start_date TEXT NOT NULL,
            end_date TEXT,
            frequency TEXT CHECK(frequency IN ('daily','weekdays','weekends')) NOT NULL DEFAULT 'daily',
            hard_mode INTEGER NOT NULL DEFAULT 0,
            is_failed INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """
    )

    # Логи выполнения привычек (чек-лист за каждый день)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS habit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            log_date TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(habit_id) REFERENCES habits(id) ON DELETE CASCADE,
            UNIQUE(habit_id, log_date)
        )
    """
    )

    # Таблица тегов
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """
    )

    # Связка «многие-ко-многим» привычек и тегов
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS habit_tags (
            habit_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (habit_id, tag_id),
            FOREIGN KEY(habit_id) REFERENCES habits(id) ON DELETE CASCADE,
            FOREIGN KEY(tag_id) REFERENCES tags(id) ON DELETE CASCADE
        )
    """
    )

    conn.commit()
    conn.close()
    print("База данных успешно создана.")


if __name__ == "__main__":
    init_db()
