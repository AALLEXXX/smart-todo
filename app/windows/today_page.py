from datetime import date
from datetime import datetime

from PyQt6.QtWidgets import QCheckBox
from PyQt6.QtWidgets import QFrame
from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget

from app.db import get_habit_items
from app.db import get_habit_logs
from app.db import get_habits
from app.db import update_habit_log
from app.ui.ui_TodayPage import Ui_TodayPage


class TodayPageController:
    def __init__(self, container: QWidget):
        self.container = container
        self.ui = Ui_TodayPage()
        self.ui.setupUi(self.container)

        # theme = config.load_user_theme()
        # icon_name = f"icons/no_habit_today_{theme}.png"
        # icon_path = resource_path(icon_name)
        #
        # # Загружаем и масштабируем иконку
        # pixmap = QPixmap(icon_path)
        # pixmap = pixmap.scaled(
        #     100, 100,
        #     Qt.AspectRatioMode.KeepAspectRatio,
        #     Qt.TransformationMode.SmoothTransformation
        # )
        # self.ui.noHabitsImage.setPixmap(pixmap)
        # self.ui.noHabitsImage.setFixedSize(100, 100)
        #
        # # placeholder растягивается и центрируется
        # self.ui.noHabitsWidget.setSizePolicy(
        #     QSizePolicy.Policy.Expanding,
        #     QSizePolicy.Policy.Minimum
        # )
        # self.ui.verticalLayout.setAlignment(
        #     self.ui.noHabitsWidget,
        #     Qt.AlignmentFlag.AlignHCenter
        # )

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

        items = get_habit_items(habit_id)
        boxes = []
        todays_done = {d: done for _, _, d, done in get_habit_logs(habit_id)}.get(date.today(), False)
        for desc in items:
            chk = QCheckBox(desc)
            chk.setChecked(todays_done)
            boxes.append(chk)
            vbox.addWidget(chk)
            chk.stateChanged.connect(lambda _, hid=habit_id, b=boxes: self._on_check_change(hid, b))

        self.ui.habitsLayout.addWidget(card)

    def _on_check_change(self, habit_id, boxes):
        done_all = all(box.isChecked() for box in boxes)
        update_habit_log(habit_id, date.today(), done_all)
        if done_all:
            QMessageBox.information(self.container, "Congratulations", "Ура, ты молодец!")
