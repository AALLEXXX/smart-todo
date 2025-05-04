import configparser
import json
import os
from datetime import date
from datetime import datetime

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtWidgets import QSizePolicy

from app import config
from app.db import clear_all_user_data
from app.db import get_active_tasks
from app.db import get_archived_tasks
from app.db import get_connection
from app.db import get_habit_items
from app.db import get_habit_logs
from app.db import get_habits
from app.db import get_tag_id_by_name
from app.db import insert_habit_full
from app.db import insert_habit_item_full
from app.db import insert_habit_item_log_full
from app.db import insert_habit_log_full
from app.db import insert_habit_tag
from app.db import insert_tag
from app.db import insert_task_full


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(600, 500)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        export_btn = QtWidgets.QPushButton("Export Data", self)
        import_btn = QtWidgets.QPushButton("Import Data", self)
        layout.addWidget(export_btn)
        layout.addWidget(import_btn)

        export_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        import_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        export_btn.clicked.connect(self.export_data)
        import_btn.clicked.connect(self.import_data)

    def export_data(self):
        folder = QFileDialog.getExistingDirectory(self, "Select export folder")
        if not folder:
            return

        filename = f"export_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        path = os.path.join(folder, filename)

        conn = get_connection()
        data = {
            "meta": {
                "app_version": config.VERSION,
                "exported_at": datetime.now().isoformat(),
            },
            "tasks": [
                dict(zip([col[1] for col in conn.execute("PRAGMA table_info(tasks)").fetchall()], row))
                for row in get_active_tasks()
            ],
            "archived_tasks": [
                dict(zip([col[1] for col in conn.execute("PRAGMA table_info(tasks)").fetchall()], row))
                for row in get_archived_tasks()
            ],
            "habits": [],
            "tags": [
                dict(zip([col[1] for col in conn.execute("PRAGMA table_info(tags)").fetchall()], row))
                for row in conn.execute("SELECT * FROM tags")
            ],
            "config": {},
        }

        for h in get_habits():
            hid = h[0]
            habit = dict(zip([col[1] for col in conn.execute("PRAGMA table_info(habits)").fetchall()], h))

            habit["items"] = [dict(zip(["id", "description", "sort_index"], item)) for item in get_habit_items(hid)]

            # ensure log_date is a string
            habit["logs"] = [
                {"log_date": (log_date.isoformat() if isinstance(log_date, date) else log_date), "completed": completed}
                for (_id, _hid, log_date, completed) in get_habit_logs(hid)
            ]

            item_logs_rows = conn.execute(
                "SELECT item_id, log_date, completed FROM habit_item_logs WHERE habit_id=?", (hid,)
            ).fetchall()
            habit["item_logs"] = [
                {"item_id": row[0], "log_date": row[1], "completed": bool(row[2])} for row in item_logs_rows
            ]

            habit["tags"] = [
                t["name"]
                for t in data["tags"]
                if any(
                    t["id"] == tag_id
                    for (tag_id,) in conn.execute("SELECT tag_id FROM habit_tags WHERE habit_id=?", (hid,))
                )
            ]

            data["habits"].append(habit)

        cfg = configparser.RawConfigParser()
        cfg.read(config.USER_CONFIG_PATH)
        for section in cfg.sections():
            data["config"][section] = dict(cfg.items(section))

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        QMessageBox.information(self, "Export", f"Data exported to {path}")

    def import_data(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select import file", filter="JSON Files (*.json)")
        if not path:
            return

        reply = QMessageBox.warning(
            self,
            "Confirm Import",
            "This will overwrite all existing data. Continue?",
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
        )
        if reply != QMessageBox.StandardButton.Ok:
            return

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        conn = get_connection()
        try:
            # begin atomic import
            clear_all_user_data(conn)

            # restore tags
            for tag in data.get("tags", []):
                insert_tag(tag["id"], tag["name"], conn)

            # restore tasks
            for row in data.get("tasks", []) + data.get("archived_tasks", []):
                insert_task_full(
                    row["id"],
                    row["title"],
                    row["description"],
                    row["priority"],
                    row["status"],
                    row["created_at"],
                    row["due_date"],
                    row["completed_at"],
                    row.get("is_archived", 0),
                    conn,
                )

            # restore habits and related
            for h in data.get("habits", []):
                insert_habit_full(
                    h["id"],
                    h["title"],
                    h["reward"],
                    h["start_date"],
                    h["end_date"],
                    h["frequency"],
                    h["hard_mode"],
                    h["is_failed"],
                    h["created_at"],
                    conn,
                )
                for item in h.get("items", []):
                    insert_habit_item_full(item["id"], h["id"], item["description"], item["sort_index"], conn)
                for log in h.get("logs", []):
                    insert_habit_log_full(h["id"], log["log_date"], log["completed"], conn)
                for il in h.get("item_logs", []):
                    insert_habit_item_log_full(h["id"], il["item_id"], il["log_date"], il["completed"], conn)
                for tag_name in h.get("tags", []):
                    tag_id = get_tag_id_by_name(tag_name)
                    if tag_id is not None:
                        insert_habit_tag(h["id"], tag_id, conn)

            # commit transaction
            conn.commit()
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Import Error", f"Data import failed: {e}")
            return

        # restore user config
        cfg = configparser.RawConfigParser()
        cfg.read_dict(data.get("config", {}))
        with open(config.USER_CONFIG_PATH, "w", encoding="utf-8") as f:
            cfg.write(f)

        QMessageBox.information(self, "Import", "Data imported. Please restart the app.")
