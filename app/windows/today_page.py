from datetime import date
from datetime import datetime

from PyQt6.QtWidgets import QCheckBox
from PyQt6.QtWidgets import QFrame
from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget

from app.db import get_habit_item_logs
from app.db import get_habit_items
from app.db import get_habit_logs
from app.db import get_habits
from app.db import update_habit_item_log
from app.db import update_habit_log
from app.ui.ui_TodayPage import Ui_TodayPage


class TodayPageController:
    def __init__(self, container: QWidget):
        self.container = container
        self.ui = Ui_TodayPage()
        self.ui.setupUi(self.container)

        self.load_today_habits()

    def load_today_habits(self):
        layout = self.ui.habitsLayout
        # очищаем все элементы (виджеты и спейсеры)
        for i in reversed(range(layout.count())):
            item = layout.takeAt(i)
            w = item.widget()
            if w:
                w.setParent(None)

        today = date.today()
        weekday = today.weekday()
        all_habits = get_habits()
        has_any = False

        for rec in all_habits:
            hid, title, _, start_str, end_str, freq, hard_mode, is_failed, _ = rec
            if hard_mode == 1 and is_failed == 1:
                continue
            start = datetime.fromisoformat(start_str.split("T")[0]).date()
            end = datetime.fromisoformat(end_str.split("T")[0]).date()
            if not (start <= today <= end):
                continue
            if freq == "daily" or (freq == "weekdays" and weekday < 5) or (freq == "weekends" and weekday >= 5):
                self._add_habit_card(hid, title)
                has_any = True

        if has_any:
            self.ui.noHabitsWidget.hide()
            self.ui.habitsScrollArea.show()
            layout.addStretch()
        else:
            self.ui.habitsScrollArea.hide()
            self.ui.noHabitsWidget.show()

    def _add_habit_card(self, habit_id: int, title: str):
        card = QFrame(self.container)
        card.setObjectName("habitCard")
        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(8, 8, 8, 8)
        vbox.setSpacing(6)

        lbl_title = QLabel(title)
        lbl_title.setObjectName("title")
        vbox.addWidget(lbl_title)

        logs = sorted(get_habit_logs(habit_id), key=lambda x: x[2], reverse=True)
        streak = 0
        for _, _, log_date, done in logs:
            if log_date == date.today() and done:
                streak += 1
            elif done and streak == 0:
                streak += 1
            else:
                break
        lbl_streak = QLabel(f"Streak: {streak}")
        lbl_streak.setObjectName("streak")
        vbox.addWidget(lbl_streak)

        items = get_habit_items(habit_id)  # now returns list of (item_id, description)
        item_logs = get_habit_item_logs(habit_id, date.today())
        for item_id, desc in items:
            chk = QCheckBox(desc)
            is_done = item_logs.get(item_id, False)
            chk.setChecked(is_done)
            vbox.addWidget(chk)
            chk.stateChanged.connect(
                lambda state, hid=habit_id, iid=item_id, box=chk: self._on_item_check_change(hid, iid, box)
            )

        self.ui.habitsLayout.addWidget(card)

    def _on_item_check_change(self, habit_id: int, item_id: int, checkbox: QCheckBox):
        completed = checkbox.isChecked()
        update_habit_item_log(habit_id, item_id, date.today(), completed)
        # Update overall habit completion flag
        items = get_habit_items(habit_id)
        logs = get_habit_item_logs(habit_id, date.today())
        all_done = all(logs.get(iid, False) for iid, _ in items)
        update_habit_log(habit_id, date.today(), all_done)
        if all_done:
            QMessageBox.information(self.container, "Congratulations", "Ура, ты молодец!")
