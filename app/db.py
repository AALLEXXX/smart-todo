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
