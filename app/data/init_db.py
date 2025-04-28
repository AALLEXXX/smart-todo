import os
import sqlite3

MODE = "dev"
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

    cursor.execute(
        """
            CREATE TABLE IF NOT EXISTS habit_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            sort_index INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(habit_id) REFERENCES habits(id) ON DELETE CASCADE
        );
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

    if MODE == "dev":
        from datetime import date
        from datetime import datetime as _dt
        from datetime import timedelta

        today = date.today()
        start_iso = (today - timedelta(days=3)).isoformat()
        end_iso = (today + timedelta(days=3)).isoformat()
        created_at = _dt.now().isoformat()

        # Создаём «жёсткую» привычку с пустым днём пропуска
        cursor.execute(
            "INSERT INTO habits (title, reward, start_date, end_date, frequency, hard_mode, is_failed, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("Demo Hard Habit", "Test reward", start_iso, end_iso, "daily", 1, 0, created_at),
        )
        habit_id = cursor.lastrowid

        # Пункты привычки
        demo_items = ["Item A", "Item B", "Item C"]
        for idx, desc in enumerate(demo_items):
            cursor.execute(
                "INSERT INTO habit_items (habit_id, description, sort_index) VALUES (?, ?, ?)", (habit_id, desc, idx)
            )

        # Логи: ставим выполнение за 3 и 1 день назад, пропускаем 2 дня назад
        cursor.execute(
            "INSERT INTO habit_logs (habit_id, log_date, completed) VALUES (?, ?, ?)",
            (habit_id, (today - timedelta(days=3)).isoformat(), 1),
        )
        cursor.execute(
            "INSERT INTO habit_logs (habit_id, log_date, completed) VALUES (?, ?, ?)",
            (habit_id, (today - timedelta(days=1)).isoformat(), 1),
        )

        # Тестовые задачи «взлом Пентагона»
        demo_tasks = [
            (
                "Reconnaissance Pentagon Networks",
                "Gather intel on publicly exposed Pentagon servers.",
                "High",
                "Backlog",
                created_at,
                (today + timedelta(days=1)).isoformat(),
                None,
            ),
            (
                "Develop Exploit for Pentagon Firewall",
                "Write and test exploit code to bypass the firewall.",
                "High",
                "In Progress",
                created_at,
                (today + timedelta(days=3)).isoformat(),
                None,
            ),
            (
                "Spear-Phishing Pentagon Contractors",
                "Craft targeted phishing emails to obtain credentials.",
                "Medium",
                "Blocked",
                created_at,
                (today - timedelta(days=1)).isoformat(),
                None,
            ),
            (
                "Credential Harvesting Operations",
                "Capture login details from compromised endpoints.",
                "High",
                "Backlog",
                created_at,
                (today + timedelta(days=7)).isoformat(),
                None,
            ),
            (
                "Establish Persistence on Pentagon Servers",
                "Install backdoors for long-term access.",
                "Medium",
                "Backlog",
                created_at,
                (today + timedelta(days=14)).isoformat(),
                None,
            ),
            (
                "Data Exfiltration from Secure Databases",
                "Extract sensitive information without detection.",
                "High",
                "Backlog",
                created_at,
                (today + timedelta(days=5)).isoformat(),
                None,
            ),
            (
                "Log Cleanup and Anti-Forensics",
                "Remove traces of intrusion and clear system logs.",
                "Low",
                "Done",
                created_at,
                (today - timedelta(days=2)).isoformat(),
                created_at,
            ),
            (
                "Proxy Infrastructure Setup",
                "Configure proxy servers to anonymize traffic.",
                "Medium",
                "In Progress",
                created_at,
                (today + timedelta(days=10)).isoformat(),
                None,
            ),
            (
                "IDS Evasion Testing",
                "Validate stealth techniques against intrusion detection.",
                "Medium",
                "Backlog",
                created_at,
                (today + timedelta(days=2)).isoformat(),
                None,
            ),
            (
                "Draft Pentagon Breach Report",
                "Document methods and findings for stakeholders.",
                "Low",
                "In Progress",
                created_at,
                (today + timedelta(days=15)).isoformat(),
                None,
            ),
        ]
        for idx, (title, desc, pri, stat, created, due, completed) in enumerate(demo_tasks):
            cursor.execute(
                "INSERT INTO tasks "
                "(title, description, priority, status, created_at, due_date, completed_at, sort_index, is_archived) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (title, desc, pri, stat, created, due, completed, idx, 0),
            )

        print("тестовые данные созданы")

    conn.commit()
    conn.close()
    print("База данных успешно создана.")


if __name__ == "__main__":
    init_db()
