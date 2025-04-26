import sqlite3
import os

DB_PATH = "todo.db"

def init_db():
    if os.path.exists(DB_PATH):
        print("База данных уже существует.")
        return

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT CHECK(priority IN ('Low', 'Medium', 'High')) NOT NULL,
            status TEXT CHECK(status IN ('Backlog', 'In Progress', 'Blocked', 'Done')) NOT NULL,
            created_at TEXT NOT NULL,
            due_date TEXT,
            sort_index INTEGER NOT NULL DEFAULT 0,
            is_archived INTEGER NOT NULL DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()
    print("База данных успешно создана.")

if __name__ == "__main__":
    init_db()