import os
import sqlite3
import sys
from datetime import date
from datetime import date as _date
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
        cursor.execute("SELECT * FROM tasks WHERE is_archived = 0 ORDER BY status")
        return cursor.fetchall()


def get_archived_tasks():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE is_archived = 1 ORDER BY created_at DESC")
        return cursor.fetchall()


def add_task(title, description, priority, status, due_date):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, description, priority, status, created_at, due_date, is_archived) "
            "VALUES (?, ?, ?, ?, ?, ?, 0)",
            (title, description, priority, status, datetime.now().isoformat(), due_date),
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


def add_habit(title, reward, start_date, end_date, frequency, hard_mode, items: list[str]):
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

    habit_id = cur.lastrowid
    for idx, desc in enumerate(items):
        cur.execute(
            "INSERT INTO habit_items (habit_id, description, sort_index) VALUES (?, ?, ?)", (habit_id, desc, idx)
        )

    conn.commit()

    return habit_id


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
    conn = get_connection()
    cur = conn.cursor()
    if year:
        start = f"{year}-01-01"
        end = f"{year}-12-31"
        # используем date() чтобы отбросить время
        cur.execute(
            "SELECT * FROM habit_logs WHERE habit_id=? AND date(log_date) BETWEEN ? AND ?",
            (habit_id, start, end),
        )
    else:
        cur.execute("SELECT * FROM habit_logs WHERE habit_id=?", (habit_id,))
    rows = cur.fetchall()
    # parse dates...
    return [(r[0], r[1], datetime.fromisoformat(r[2]).date(), r[3]) for r in rows]


def get_habit_items(habit_id: int):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, description, sort_index FROM habit_items WHERE habit_id=? ORDER BY sort_index", (habit_id,)
        )
        return cur.fetchall()


def update_habit_log(habit_id: int, log_date: str | date, completed: bool):
    # всегда храним только YYYY-MM-DD
    if isinstance(log_date, _date):
        log_iso = log_date.isoformat()
    else:
        # если строка с временем, отрезаем
        log_iso = log_date.split("T")[0]

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE habit_logs SET completed = ? WHERE habit_id = ? AND log_date = ?",
        (int(completed), habit_id, log_iso),
    )
    if cur.rowcount == 0:
        cur.execute(
            "INSERT INTO habit_logs (habit_id, log_date, completed) VALUES (?, ?, ?)",
            (habit_id, log_iso, int(completed)),
        )
    conn.commit()


def get_habit_item_logs(habit_id: int, log_date: str | _date):
    if isinstance(log_date, _date):
        log_iso = log_date.isoformat()
    else:
        log_iso = log_date.split("T")[0]
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT item_id, completed FROM habit_item_logs WHERE habit_id=? AND log_date=?",
        (habit_id, log_iso),
    )
    return {r[0]: bool(r[1]) for r in cur.fetchall()}


def update_habit_item_log(habit_id: int, item_id: int, log_date: str | _date, completed: bool):
    if isinstance(log_date, _date):
        log_iso = log_date.isoformat()
    else:
        log_iso = log_date.split("T")[0]
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE habit_item_logs SET completed=? WHERE habit_id=? AND item_id=? AND log_date=?",
        (int(completed), habit_id, item_id, log_iso),
    )
    if cur.rowcount == 0:
        cur.execute(
            "INSERT INTO habit_item_logs (habit_id, item_id, log_date, completed) VALUES (?, ?, ?, ?)",
            (habit_id, item_id, log_iso, int(completed)),
        )
    conn.commit()


def evaluate_hard_habits():
    """
    Для всех hard_mode=1 и is_failed=0:
    проверяем все обязательные даты от start_date до вчерашнего;
    если хотя бы один обязательный день не выполнен — ставим is_failed=1.
    """
    from datetime import date
    from datetime import timedelta

    conn = get_connection()
    cur = conn.cursor()
    today = date.today()
    yesterday = today - timedelta(days=1)

    cur.execute("SELECT id, start_date, end_date, frequency FROM habits WHERE hard_mode=1 AND is_failed=0")
    rows = cur.fetchall()

    for hid, start_str, end_str, freq in rows:
        # отбросить время, оставить только YYYY-MM-DD
        start_iso = start_str.split("T")[0]
        start = date.fromisoformat(start_iso)

        if end_str:
            end_iso = end_str.split("T")[0]
            end = date.fromisoformat(end_iso)
        else:
            end = yesterday

        period_end = min(end, yesterday)

        missed = False
        current = start
        while current <= period_end:
            need = (
                freq == "daily"
                or (freq == "weekdays" and current.weekday() < 5)
                or (freq == "weekends" and current.weekday() >= 5)
            )
            if need:
                cur.execute(
                    "SELECT completed FROM habit_logs WHERE habit_id=? AND date(log_date)=?", (hid, current.isoformat())
                )
                row = cur.fetchone()
                if not row or row[0] != 1:
                    missed = True
                    break
            current += timedelta(days=1)

        if missed:
            cur.execute("UPDATE habits SET is_failed=1 WHERE id=?", (hid,))

    conn.commit()


def clear_all_user_data(conn=None):
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    cur = conn.cursor()
    for tbl in ["tasks", "habits", "habit_items", "habit_logs", "habit_item_logs", "tags", "habit_tags"]:
        cur.execute(f"DELETE FROM {tbl}")
    if own_conn:
        conn.commit()


def insert_tag(id: int, name: str, conn=None):
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    cur = conn.cursor()
    cur.execute("INSERT INTO tags (id, name) VALUES (?, ?)", (id, name))
    if own_conn:
        conn.commit()


def insert_task_full(
    id, title, description, priority, status, created_at, due_date, completed_at, is_archived, conn=None
):
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (id, title, description, priority, status, created_at, due_date, completed_at, is_archived) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (id, title, description, priority, status, created_at, due_date, completed_at, is_archived),
    )
    if own_conn:
        conn.commit()


def insert_habit_full(id, title, reward, start_date, end_date, frequency, hard_mode, is_failed, created_at, conn=None):
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO habits (id, title, reward, start_date, end_date, frequency, hard_mode, is_failed, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (id, title, reward, start_date, end_date, frequency, hard_mode, is_failed, created_at),
    )
    if own_conn:
        conn.commit()


def insert_habit_item_full(id, habit_id, description, sort_index, conn=None):
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO habit_items (id, habit_id, description, sort_index) VALUES (?, ?, ?, ?)",
        (id, habit_id, description, sort_index),
    )
    if own_conn:
        conn.commit()


def insert_habit_log_full(habit_id, log_date, completed, conn=None):
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO habit_logs (habit_id, log_date, completed) VALUES (?, ?, ?)", (habit_id, log_date, completed)
    )
    if own_conn:
        conn.commit()


def insert_habit_item_log_full(habit_id, item_id, log_date, completed, conn=None):
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO habit_item_logs (habit_id, item_id, log_date, completed) VALUES (?, ?, ?, ?)",
        (habit_id, item_id, log_date, completed),
    )
    if own_conn:
        conn.commit()


def insert_habit_tag(habit_id, tag_id, conn=None):
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    cur = conn.cursor()
    cur.execute("INSERT INTO habit_tags (habit_id, tag_id) VALUES (?, ?)", (habit_id, tag_id))
    if own_conn:
        conn.commit()


def get_tag_id_by_name(name: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM tags WHERE name=?", (name,))
    row = cur.fetchone()
    return row[0] if row else None
