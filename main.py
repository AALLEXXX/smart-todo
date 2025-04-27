import os
import sys

from PyQt6 import QtCore
from PyQt6 import QtWidgets

from app import config
from app.ui.ui_BoardPage import Ui_BoardPage
from app.ui.ui_HabitsPage import Ui_HabitsPage
from app.ui.ui_MainWindow import Ui_MainWindow
from app.ui.ui_TodayPage import Ui_TodayPage
from app.windows.archive_dialog import ArchiveDialog
from app.windows.board_window import BoardController


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.settings = QtCore.QSettings(config.USER_CONFIG_PATH, QtCore.QSettings.Format.IniFormat)
        geometry = self.settings.value("MainWindow/geometry", type=QtCore.QByteArray)
        if geometry:
            self.restoreGeometry(geometry)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.today_page = QtWidgets.QWidget()
        Ui_TodayPage().setupUi(self.today_page)
        self.board_page = QtWidgets.QWidget()
        self.board_ui = Ui_BoardPage()
        self.board_ui.setupUi(self.board_page)
        # Habits page
        self.habits_page = QtWidgets.QWidget()
        Ui_HabitsPage().setupUi(self.habits_page)

        tabs = self.ui.tabWidget
        tabs.addTab(self.today_page, "Today")
        tabs.addTab(self.board_page, "Board")
        tabs.addTab(self.habits_page, "Habits")
        tabs.setMovable(True)
        tabs.setCurrentIndex(0)

        self.setMinimumSize(config.DEFAULT_WINDOW_WIDTH, config.DEFAULT_WINDOW_HEIGHT)
        # Загружаем тему из INI-файла через config.load_user_theme()
        self.current_theme = config.load_user_theme()

        self.apply_theme()
        self.board = BoardController(self.board_page, self)

    def closeEvent(self, event):
        self.settings.setValue("MainWindow/geometry", self.saveGeometry())
        super().closeEvent(event)

    def apply_theme(self):
        if getattr(sys, "frozen", False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        theme_path = os.path.join(base_path, config.THEMES[self.current_theme])
        with open(theme_path, "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        config.save_user_theme(self.current_theme)
        self.apply_theme()
        self.board.load_tasks()

    def open_archive(self):
        dialog = ArchiveDialog(self)
        dialog.resize(config.ARCHIVE_WINDOW_WIDTH, config.ARCHIVE_WINDOW_HEIGHT)
        dialog.exec()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
