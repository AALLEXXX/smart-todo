import os
import sqlite3
import sys
from datetime import datetime


def resource_path(relative_path):
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


DB_PATH = resource_path("data/todo.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def get_active_tasks():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE is_archived = 0 ORDER BY status, sort_index")
        return cursor.fetchall()


def get_archived_tasks():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE is_archived = 1 ORDER BY created_at DESC")
        return cursor.fetchall()


def add_task(title, description, priority, status, due_date, sort_index):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, description, priority, status, created_at, due_date, sort_index, is_archived) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, 0)",
            (title, description, priority, status, datetime.now().isoformat(), due_date, sort_index),
        )
        conn.commit()


def update_task(task_id, **fields):
    if "status" in fields and fields["status"] == "Done":
        fields["completed_at"] = datetime.now().isoformat()

    keys = ", ".join(f"{k}=?" for k in fields)
    values = list(fields.values())
    values.append(task_id)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE tasks SET {keys} WHERE id = ?", values)
        conn.commit()


def archive_task(task_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET is_archived = 1 WHERE id = ?", (task_id,))
        conn.commit()


def delete_task(task_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()


def add_habit(title, reward, start_date, end_date, frequency, hard_mode):
    """
    Создаёт новую привычку и возвращает её ID.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO habits (title, reward, start_date, end_date, frequency, hard_mode, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            title,
            reward,
            start_date,
            end_date,
            frequency,
            int(hard_mode),
            datetime.now().isoformat(),
        ),
    )
    conn.commit()
    return cur.lastrowid


def get_habits(year=None):
    """
    Возвращает список привычек. Если указан год, фильтрует по end_date или start_date.
    """
    conn = get_connection()
    cur = conn.cursor()
    if year:
        start = f"{year}-01-01"
        end = f"{year}-12-31"
        cur.execute(
            "SELECT * FROM habits WHERE (start_date<=? AND end_date>=?) OR (start_date>=? AND start_date<=?)",
            (end, start, start, end),
        )
    else:
        cur.execute("SELECT * FROM habits")
    return cur.fetchall()


def get_habit_logs(habit_id: int, year: int = None):
    """Return all log records for a habit; if year provided, filter to that calendar year."""
    conn = get_connection()
    cur = conn.cursor()
    if year:
        start = f"{year}-01-01"
        end = f"{year}-12-31"
        cur.execute("SELECT * FROM habit_logs WHERE habit_id=? AND log_date BETWEEN ? AND ?", (habit_id, start, end))
    else:
        cur.execute("SELECT * FROM habit_logs WHERE habit_id=?", (habit_id,))
    rows = cur.fetchall()
    # parse dates
    return [(r[0], r[1], datetime.fromisoformat(r[2]).date(), r[3]) for r in rows]
