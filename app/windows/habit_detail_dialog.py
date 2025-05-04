from datetime import date
from datetime import datetime

from PyQt6.QtWidgets import QDialog
from PyQt6.QtWidgets import QLabel

from app.db import get_habit_item_logs
from app.db import get_habit_items
from app.db import get_habit_logs
from app.db import get_habits
from app.ui.ui_HabitDetailDialog import Ui_HabitDetailDialog


class HabitDetailDialog(QDialog):
    def __init__(self, habit_id: int, parent=None):
        super().__init__(parent)
        self.ui = Ui_HabitDetailDialog()
        self.ui.setupUi(self)
        self.habit_id = habit_id
        self.ui.closeButton.clicked.connect(self.close)
        self.load_data()

    def load_data(self):
        # 1) данные привычки
        recs = get_habits(None)  # без фильтра по году
        rec = next((r for r in recs if r[0] == self.habit_id), None)
        if not rec:
            return
        _, title, reward, start_str, end_str, freq, hard_mode, is_failed, _ = rec

        # Заголовок
        self.ui.titleLabel.setText(title)
        # Статус
        today = date.today()
        end_date = datetime.fromisoformat(end_str.split("T")[0]).date()
        if is_failed:
            status_text = "Failed"
            color = "#e53935"
        elif today > end_date:
            status_text = "Completed"
            color = "#1976d2"
        else:
            status_text = "Active"
            color = "#4caf50"
        self.ui.statusLabel.setText(status_text)
        self.ui.statusLabel.setStyleSheet(f"color: {color}; font-weight:bold;")

        # 2) даты
        self.ui.datesLabel.setText(f"Start: {start_str.split('T')[0]}   End: {end_str.split('T')[0]}")

        # 3) стрик
        logs = sorted(get_habit_logs(self.habit_id), key=lambda x: x[2], reverse=True)
        streak = 0
        for _, _, log_date, done in logs:
            if log_date == date.today() and done:
                streak += 1
            elif done and streak == 0:
                streak += 1
            else:
                break
        self.ui.streakLabel.setText(f"Streak: {streak}")

        # 4) награда и режим
        self.ui.rewardLabel.setText(f"Reward: {reward}")
        mode = "Hard" if hard_mode else "Normal"
        self.ui.hardModeLabel.setText(f"Mode: {mode}")

        # 5) пункты и их состояние
        items = get_habit_items(self.habit_id)  # [(item_id, desc), ...]
        item_logs = get_habit_item_logs(self.habit_id, date.today())
        for item_id, desc, _ in items:
            done = item_logs.get(item_id, False)
            lbl = QLabel(f"[{'✔' if done else ' '}] {desc}")
            self.ui.itemsLayout.addWidget(lbl)
