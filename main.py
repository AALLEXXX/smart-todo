import os
import sys

from PyQt6 import QtCore
from PyQt6 import QtWidgets

from app import config
from app.components.task_card import TaskCard
from app.db import add_task
from app.db import archive_task
from app.db import delete_task
from app.db import get_active_tasks
from app.db import update_task
from app.ui.ui_MainWindow import Ui_MainWindow
from app.windows.archive_dialog import ArchiveDialog
from app.windows.task_dialog import TaskDetailDialog
from app.windows.task_dialog import TaskDialog


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.settings = QtCore.QSettings(config.USER_CONFIG_PATH, QtCore.QSettings.Format.IniFormat)
        geometry = self.settings.value("MainWindow/geometry", type=QtCore.QByteArray)
        if geometry:
            self.restoreGeometry(geometry)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setMinimumSize(config.DEFAULT_WINDOW_WIDTH, config.DEFAULT_WINDOW_HEIGHT)
        # Загружаем тему из INI-файла через config.load_user_theme()
        self.current_theme = config.load_user_theme()

        fixed_width = config.FIXED_WIDTH_COLUMN
        self.ui.backlogArea.setMinimumWidth(fixed_width)
        self.ui.backlogArea.setMaximumWidth(fixed_width)
        self.ui.inProgressArea.setMinimumWidth(fixed_width)
        self.ui.inProgressArea.setMaximumWidth(fixed_width)
        self.ui.blockedArea.setMinimumWidth(fixed_width)
        self.ui.blockedArea.setMaximumWidth(fixed_width)
        self.ui.doneArea.setMinimumWidth(fixed_width)
        self.ui.doneArea.setMaximumWidth(fixed_width)

        self.ui.lowPriorityCheckBox.stateChanged.connect(self.load_tasks)
        self.ui.mediumPriorityCheckBox.stateChanged.connect(self.load_tasks)
        self.ui.highPriorityCheckBox.stateChanged.connect(self.load_tasks)

        self.columns = {
            "Backlog": self.ui.backlogList,
            "In Progress": self.ui.inProgressList,
            "Blocked": self.ui.blockedList,
            "Done": self.ui.doneList,
        }
        self.columnContainers = {
            "Backlog": self.ui.backlogContainer,
            "In Progress": self.ui.inProgressContainer,
            "Blocked": self.ui.blockedContainer,
            "Done": self.ui.doneContainer,
        }
        for status, container in self.columnContainers.items():
            container.setAcceptDrops(True)
            container.dragEnterEvent = self.create_dragEnterEvent()
            container.dropEvent = self.create_dropEvent(status)

        self.ui.addTaskButton.clicked.connect(self.add_task)
        self.ui.archiveButton.clicked.connect(self.open_archive)
        self.ui.themeToggleButton.clicked.connect(self.toggle_theme)

        self.apply_theme()
        self.load_tasks()

    def closeEvent(self, event):
        self.settings.setValue("MainWindow/geometry", self.saveGeometry())
        super().closeEvent(event)

    def create_dragEnterEvent(self):
        def dragEnterEvent(event):
            if event.mimeData().hasFormat("application/x-task-id"):
                event.acceptProposedAction()

        return dragEnterEvent

    def create_dropEvent(self, target_status):
        def dropEvent(event):
            data = event.mimeData().data("application/x-task-id")
            try:
                task_id = int(data.data().decode())
            except Exception:
                return
            update_task(task_id, status=target_status)
            self.load_tasks()
            event.acceptProposedAction()

        return dropEvent

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
        self.load_tasks()

    def clear_columns(self):
        for layout in self.columns.values():
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

    def load_tasks(self):
        self.clear_columns()
        selected_priorities = []
        if self.ui.lowPriorityCheckBox.isChecked():
            selected_priorities.append("Low")
        if self.ui.mediumPriorityCheckBox.isChecked():
            selected_priorities.append("Medium")
        if self.ui.highPriorityCheckBox.isChecked():
            selected_priorities.append("High")
        if not selected_priorities:
            selected_priorities = ["Low", "Medium", "High"]

        columns_tasks = {"Backlog": [], "In Progress": [], "Blocked": [], "Done": []}
        for task in get_active_tasks():
            if task[3] not in selected_priorities:
                continue
            widget = TaskCard(
                task,
                theme=self.current_theme,
                on_delete=self.confirm_delete,
                on_archive=self.archive_task,
                on_edit=self.edit_task,
                on_view=lambda t: TaskDetailDialog(t, self).exec(),
            )
            columns_tasks[task[4]].append(widget)

        for status, widgets in columns_tasks.items():
            layout = self.columns[status]
            for widget in widgets:
                layout.addWidget(widget)
            layout.addStretch()

    def confirm_delete(self, task):
        confirm = QtWidgets.QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{task[1]}'?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
        )
        if confirm == QtWidgets.QMessageBox.StandardButton.Yes:
            delete_task(task[0])
            self.load_tasks()

    def archive_task(self, task):
        archive_task(task[0])
        self.load_tasks()

    def add_task(self):
        dialog = TaskDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            add_task(**data, sort_index=0)
            self.load_tasks()

    def edit_task(self, task):
        dialog = TaskDialog(self, task=task)
        if dialog.exec():
            data = dialog.get_data()
            update_task(task[0], **data)
            self.load_tasks()

    def open_archive(self):
        dialog = ArchiveDialog(self)
        dialog.resize(config.ARCHIVE_WINDOW_WIDTH, config.ARCHIVE_WINDOW_HEIGHT)
        dialog.exec()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
