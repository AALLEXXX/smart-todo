from datetime import datetime

from PyQt6 import QtWidgets
from PyQt6.QtCore import QDate
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog
from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtWidgets import QMessageBox

from app.components.habit_calendar import HabitCalendar
from app.db import add_habit
from app.db import get_habit_logs
from app.db import get_habits
from app.ui.ui_HabitCard import Ui_HabitCard
from app.ui.ui_HabitDialog import Ui_HabitDialog
from app.ui.ui_HabitsPage import Ui_HabitsPage
from app.windows.habit_detail_dialog import HabitDetailDialog


def _parse_date(date_str: str):
    """Convert ISO string to date, default to today on error."""
    from datetime import datetime as _dt

    try:
        return _dt.fromisoformat(date_str).date()
    except Exception:
        return _dt.now().date()


class HabitsPageController:
    def __init__(self, container, parent=None):
        self.parent = parent
        self.ui = Ui_HabitsPage()
        self.ui.setupUi(container)

        # Настройка скроллера без рамки
        scroll = self.ui.habitsScrollArea
        scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        scroll.setViewportMargins(0, 0, 0, 0)

        self.ui.verticalLayout.setStretch(0, 0)
        self.ui.verticalLayout.setStretch(1, 1)

        self.connect_signals()
        self.load_habits()

    def connect_signals(self):
        self.ui.newHabitButton.clicked.connect(self.open_dialog)
        if hasattr(self.ui, "yearList"):
            self.ui.yearList.currentTextChanged.connect(self.load_habits)

    def load_habits(self):
        layout = self.ui.habitsListLayout
        self._clear_cards(layout)

        current_year = datetime.now().year
        habits = get_habits(current_year)

        for record in habits:
            card = self._create_card(record, current_year)
            layout.addWidget(card)

        layout.addStretch()

    def _clear_cards(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _create_card(self, record, year) -> QtWidgets.QFrame:
        card_frame = QtWidgets.QFrame()
        card_frame.setCursor(Qt.CursorShape.PointingHandCursor)
        ui_card = Ui_HabitCard()
        ui_card.setupUi(card_frame)

        # распакуем флаг хард-мода и провала
        hid, title, _, start_str, end_str, freq, hard_mode, is_failed, _ = record

        display = title
        if hard_mode == 1 and is_failed == 1:
            display += " (Failed – Hard mode)"
        ui_card.titleLabel.setText(display)

        # дальше как было…
        start = _parse_date(start_str)
        end = _parse_date(end_str)
        logs = get_habit_logs(hid, year)
        completed = {d for (_, _, d, done) in logs if done}
        calendar = HabitCalendar(completed, start, end, parent=card_frame)
        span_days = (end - start).days
        if span_days > 365:
            self._attach_calendar_with_buttons(ui_card, calendar)
        else:
            ui_card.calendarWidget.layout().addWidget(calendar)

        card_frame.mouseDoubleClickEvent = lambda ev, hid=record[0]: self.open_detail(hid)

        return card_frame

    def _attach_calendar_with_buttons(self, ui_card, calendar):
        container = ui_card.calendarWidget

        year_bar = QtWidgets.QHBoxLayout()
        year_bar.setContentsMargins(0, 0, 0, 0)
        year_bar.setSpacing(2)
        year_bar.addStretch()

        btn_prev = QtWidgets.QToolButton(parent=container)
        btn_prev.setArrowType(Qt.ArrowType.LeftArrow)
        btn_prev.setStyleSheet("background: transparent; border: none;")
        btn_prev.setAutoRaise(True)
        btn_prev.setFixedSize(20, 20)

        lbl_year = QtWidgets.QLabel(str(calendar.current_year), parent=container)
        lbl_year.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_next = QtWidgets.QToolButton(parent=container)
        btn_next.setArrowType(Qt.ArrowType.RightArrow)
        btn_next.setStyleSheet("background: transparent; border: none;")
        btn_next.setAutoRaise(True)
        btn_next.setFixedSize(20, 20)

        year_bar.addWidget(btn_prev)
        year_bar.addWidget(lbl_year)
        year_bar.addWidget(btn_next)
        year_bar.addStretch()

        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(4)
        vbox.addLayout(year_bar)
        vbox.addWidget(calendar, 1)

        container.layout().addLayout(vbox)

        def shift(delta):
            if delta < 0:
                calendar.prev_year()
            else:
                calendar.next_year()
            lbl_year.setText(str(calendar.current_year))

        btn_prev.clicked.connect(lambda: shift(-1))
        btn_next.clicked.connect(lambda: shift(+1))

    def open_dialog(self):
        dlg = QDialog(self.parent)
        ui = Ui_HabitDialog()
        ui.setupUi(dlg)
        ui.endDateEdit.setDate(QDate.currentDate())

        # динамические поля для пунктов привычки
        item_fields: list[QLineEdit] = []

        def add_item_field():
            line = QLineEdit()
            line.setPlaceholderText("Checklist item")
            ui.itemsLayout.addWidget(line)
            item_fields.append(line)

        # один начальный
        add_item_field()
        ui.addItemBtn.clicked.connect(add_item_field)

        ui.cancelBtn.clicked.connect(dlg.reject)
        ui.okBtn.clicked.connect(lambda: self.create_habit(dlg, ui, item_fields))
        dlg.exec()

    def create_habit(self, dlg, ui, item_fields: list[QLineEdit]):
        end_date = ui.endDateEdit.date()
        min_date = QDate.currentDate().addDays(2)
        if end_date < min_date:
            QMessageBox.warning(self.parent, "Invalid End Date", "End date must be at least two days from today.")
            return

        title = ui.titleEdit.text().strip()
        reward = ui.rewardEdit.text().strip()
        start = datetime.now().isoformat()
        end = end_date.toString(Qt.DateFormat.ISODate)
        freq = ui.freqCombo.currentText()
        hard = ui.hardCheck.isChecked()
        # собираем непустые пункты
        items = [f.text().strip() for f in item_fields if f.text().strip()]
        if not title or not items:
            QMessageBox.warning(dlg, "Error", "Нужно название и хотя бы один пункт.")
            return

        add_habit(title, reward, start, end, freq, hard, items)
        dlg.accept()
        self.load_habits()

    def open_detail(self, habit_id: int):
        dlg = HabitDetailDialog(habit_id, self.parent)
        dlg.setMinimumSize(450, 450)
        dlg.exec()
