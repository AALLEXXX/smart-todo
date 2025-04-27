from datetime import date
from datetime import timedelta

from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtProperty
from PyQt6.QtGui import QColor
from PyQt6.QtGui import QFont
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import QWidget


class HabitCalendar(QWidget):
    def __init__(self, log_dates: set[date], start_date: date, end_date: date, parent=None):
        super().__init__(parent)
        self.setObjectName("habitCalendar")
        self.log_dates = log_dates
        self.orig_start = start_date
        self.orig_end = end_date
        self.current_year = start_date.year
        self.square = 12
        self.spacing = 4
        self.weekday_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        self.month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        # default colors, override via QSS using qproperty
        self._active_color = QColor("#4caf50")
        self._inactive_color = QColor("#eeeeee")
        self._text_color = QColor("#000000")
        self._weekday_font_pt = 12
        self._month_font_pt = 12
        self._recompute_geometry()

    def _recompute_geometry(self):
        span_days = (self.orig_end - self.orig_start).days
        if span_days < 365:
            self.start = self.orig_start
            self.end = self.orig_end
        else:
            self.start = date(self.current_year, 1, 1)
            self.end = date(self.current_year, 12, 31)
        offset = (self.start.weekday() + 6) % 7
        self.display_start = self.start - timedelta(days=offset)
        total_days = (self.end - self.display_start).days + 1
        self.weeks = (total_days + 6) // 7
        w = self.weeks * (self.square + self.spacing) + 40
        h = 7 * (self.square + self.spacing) + 20
        self.setMinimumSize(w, h)

    def prev_year(self):
        if self.current_year > self.orig_start.year:
            self.current_year -= 1
            self._recompute_geometry()
            self.update()

    def next_year(self):
        if self.current_year < self.orig_end.year:
            self.current_year += 1
            self._recompute_geometry()
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        # Use properties for colors, set via QSS with qproperty-
        active_color = self._active_color
        inactive_color = self._inactive_color
        text_color = self._text_color

        # Draw weekday labels
        font = QFont()
        font.setPointSize(self._weekday_font_pt)
        painter.setFont(font)
        painter.setPen(text_color)
        for i, dow in enumerate(self.weekday_labels):
            y = 20 + i * (self.square + self.spacing)
            painter.drawText(0, y + self.square // 2 + 4, dow)

        # Draw month labels
        font_m = QFont()
        font_m.setPointSize(self._month_font_pt)
        painter.setFont(font_m)
        painter.setPen(text_color)
        for m, label in enumerate(self.month_labels):
            first = date(self.current_year, m + 1, 1)
            delta = (first - self.display_start).days
            week = delta // 7
            x = 40 + week * (self.square + self.spacing)
            painter.drawText(int(x), 10, label)

        # Draw heatmap squares
        painter.setPen(Qt.PenStyle.NoPen)
        for wk in range(self.weeks):
            for d in range(7):
                day = self.display_start + timedelta(days=wk * 7 + d)
                if day < self.orig_start or day > self.orig_end:
                    col = inactive_color.darker(150)
                else:
                    col = active_color if day in self.log_dates else inactive_color
                x = 40 + wk * (self.square + self.spacing)
                y = 20 + d * (self.square + self.spacing)
                painter.fillRect(int(x), int(y), self.square, self.square, col)
        painter.end()

    @pyqtProperty(QColor)
    def activeColor(self):
        return self._active_color

    @activeColor.setter
    def activeColor(self, c):
        self._active_color = c
        self.update()

    @pyqtProperty(QColor)
    def inactiveColor(self):
        return self._inactive_color

    @inactiveColor.setter
    def inactiveColor(self, c):
        self._inactive_color = c
        self.update()

    @pyqtProperty(QColor)
    def textColor(self):
        return self._text_color

    @textColor.setter
    def textColor(self, c):
        self._text_color = c
        self.update()

    @pyqtProperty(int)
    def weekdayFontPointSize(self):
        return self._weekday_font_pt

    @weekdayFontPointSize.setter
    def weekdayFontPointSize(self, v):
        self._weekday_font_pt = v
        self.update()

    @pyqtProperty(int)
    def monthFontPointSize(self):
        return self._month_font_pt

    @monthFontPointSize.setter
    def monthFontPointSize(self, v):
        self._month_font_pt = v
        self.update()
