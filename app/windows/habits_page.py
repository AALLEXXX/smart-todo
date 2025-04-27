from datetime import datetime

from PyQt6 import QtWidgets
from PyQt6.QtCore import QDate
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QToolButton
from PyQt6.QtWidgets import QVBoxLayout

from app.components.habit_calendar import HabitCalendar
from app.db import add_habit
from app.db import get_habit_logs
from app.db import get_habits
from app.ui.ui_HabitCard import Ui_HabitCard
from app.ui.ui_HabitDialog import Ui_HabitDialog
from app.ui.ui_HabitsPage import Ui_HabitsPage


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
        ui_card = Ui_HabitCard()
        ui_card.setupUi(card_frame)

        _, title, _, start_str, end_str, *_ = record
        ui_card.titleLabel.setText(title)

        start = _parse_date(start_str)
        end = _parse_date(end_str)

        logs = get_habit_logs(record[0], year)
        completed = {d for (_, _, d, done) in logs if done}

        calendar = HabitCalendar(completed, start, end, parent=card_frame)

        span_days = (end - start).days
        if span_days > 365:
            self._attach_calendar_with_buttons(ui_card, calendar)
        else:
            ui_card.calendarWidget.layout().addWidget(calendar)

        return card_frame

    def _attach_calendar_with_buttons(self, ui_card, calendar):
        container = ui_card.calendarWidget

        year_bar = QHBoxLayout()
        year_bar.setContentsMargins(0, 0, 0, 0)
        year_bar.setSpacing(2)
        year_bar.addStretch()

        btn_prev = QToolButton(parent=container)
        btn_prev.setArrowType(Qt.ArrowType.LeftArrow)
        btn_prev.setStyleSheet("background: transparent; border: none;")
        btn_prev.setAutoRaise(True)
        btn_prev.setFixedSize(20, 20)

        lbl_year = QLabel(str(calendar.current_year), parent=container)
        lbl_year.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_next = QToolButton(parent=container)
        btn_next.setArrowType(Qt.ArrowType.RightArrow)
        btn_next.setStyleSheet("background: transparent; border: none;")
        btn_next.setAutoRaise(True)
        btn_next.setFixedSize(20, 20)

        year_bar.addWidget(btn_prev)
        year_bar.addWidget(lbl_year)
        year_bar.addWidget(btn_next)
        year_bar.addStretch()

        vbox = QVBoxLayout()
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
        dlg = QtWidgets.QDialog(self.parent)
        ui = Ui_HabitDialog()
        ui.setupUi(dlg)
        ui.endDateEdit.setDate(QDate.currentDate())
        ui.cancelBtn.clicked.connect(dlg.reject)
        ui.okBtn.clicked.connect(lambda: self.create_habit(dlg, ui))
        dlg.exec()

    def create_habit(self, dlg, ui):
        end_date = ui.endDateEdit.date()
        min_date = QDate.currentDate().addDays(2)
        if end_date < min_date:
            QtWidgets.QMessageBox.warning(
                self.parent, "Invalid End Date", "End date must be at least two days from today."
            )
            return

        title = ui.titleEdit.text()
        reward = ui.rewardEdit.text()
        start = datetime.now().isoformat()
        end = end_date.toString(Qt.DateFormat.ISODate)
        freq = ui.freqCombo.currentText()
        hard = ui.hardCheck.isChecked()

        add_habit(title, reward, start, end, freq, hard)
        dlg.accept()
        self.load_habits()
