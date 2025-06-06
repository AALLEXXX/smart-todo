import os
import sys

from PyQt6 import QtCore
from PyQt6 import QtWidgets
from PyQt6.QtGui import QIcon

from app import config
from app.db import evaluate_hard_habits
from app.ui.ui_BoardPage import Ui_BoardPage
from app.ui.ui_MainWindow import Ui_MainWindow
from app.windows.archive_dialog import ArchiveDialog
from app.windows.board_window import BoardController
from app.windows.habits_page import HabitsPageController
from app.windows.settings_dialog import SettingsDialog
from app.windows.today_page import TodayPageController


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        evaluate_hard_habits()

        self.settings = QtCore.QSettings(config.USER_CONFIG_PATH, QtCore.QSettings.Format.IniFormat)
        geometry = self.settings.value("MainWindow/geometry", type=QtCore.QByteArray)
        if geometry:
            self.restoreGeometry(geometry)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.current_theme = config.load_user_theme()

        self.set_settings_icon()
        self.ui.settingsButton.clicked.connect(self.open_settings)

        try:
            version = config.VERSION
        except AttributeError:
            version = ""
        self.ui.versionLabel.setText(version)

        self.today_controller = TodayPageController(self.ui.today_page)

        self.board_ui = Ui_BoardPage()
        self.board_ui.setupUi(self.ui.board_page)

        self.stacked = self.ui.stackedWidget
        self.board = BoardController(self.ui.board_page, self)
        self.habits_controller = HabitsPageController(self.ui.habits_page, self)

        self.ui.tabToday.clicked.connect(lambda: self.select_tab(0))
        self.ui.tabBoard.clicked.connect(lambda: self.select_tab(1))
        self.ui.tabHabits.clicked.connect(lambda: self.select_tab(2))
        self.select_tab(0)

        self.ui.themeToggleButton.clicked.connect(self.toggle_theme)
        self.apply_theme()

        self.setMinimumSize(config.DEFAULT_WINDOW_WIDTH, config.DEFAULT_WINDOW_HEIGHT)

    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()

    def select_tab(self, idx):
        # отметить кнопки
        for btn in (self.ui.tabToday, self.ui.tabBoard, self.ui.tabHabits):
            btn.setChecked(False)
        {0: self.ui.tabToday, 1: self.ui.tabBoard, 2: self.ui.tabHabits}[idx].setChecked(True)
        # показать страницу
        self.stacked.setCurrentIndex(idx)

        if idx == 0:  # Today
            self.today_controller.load_today_habits()
        elif idx == 1:  # Board
            self.board.load_tasks()
        elif idx == 2:  # Habits
            self.habits_controller.load_habits()

    def closeEvent(self, event):
        self.settings.setValue("MainWindow/geometry", self.saveGeometry())
        super().closeEvent(event)

    def apply_theme(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(base_path, "app/styles/base.qss"), encoding="utf-8") as f:
            base = f.read()
        theme_file = "style_light.qss" if self.current_theme == "light" else "style_dark.qss"
        with open(os.path.join(base_path, f"app/styles/{theme_file}"), encoding="utf-8") as f:
            theme = f.read()
        # объединяем
        self.setStyleSheet(base + "\n" + theme)

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        config.save_user_theme(self.current_theme)
        self.apply_theme()
        self.board.load_tasks()

        # update settings icon according to new theme
        self.set_settings_icon()

    def set_settings_icon(self):
        icon = QIcon.fromTheme("settings")
        if icon.isNull():
            if self.current_theme == "light":
                icon_path = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)), "app", "icons", "settings_light.png"
                )
            else:
                icon_path = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)), "app", "icons", "settings_dark.png"
                )
            icon = QIcon(icon_path)
        self.ui.settingsButton.setIcon(icon)
        _btn_size = self.ui.settingsButton.sizeHint()
        self.ui.settingsButton.setIcon(icon)
        self.ui.settingsButton.setIconSize(QtCore.QSize(25, 25))
        self.ui.settingsButton.setFixedSize(_btn_size)

    def open_archive(self):
        dialog = ArchiveDialog(self)
        dialog.resize(config.ARCHIVE_WINDOW_WIDTH, config.ARCHIVE_WINDOW_HEIGHT)
        dialog.exec()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
