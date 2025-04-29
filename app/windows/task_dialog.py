from PyQt6 import QtCore
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QMessageBox

from app.ui.ui_TaskDialog import Ui_TaskDialog
from app.utils import format_deadline
from app.windows.base_dialog import PersistentDialog


class TaskDialog(PersistentDialog):
    def __init__(self, parent=None, task=None):
        super().__init__("TaskDialog_geometry", parent)
        self.ui = Ui_TaskDialog()
        self.ui.setupUi(self)
        self.task = task
        self.ui.saveButton.clicked.connect(self._on_save)
        self.ui.cancelButton.clicked.connect(self.reject)
        self.ui.dueDateEdit.setDate(QtCore.QDate.currentDate())
        if task:
            self.ui.titleEdit.setText(task[1])
            self.ui.descriptionEdit.setPlainText(task[2])
            self.ui.priorityCombo.setCurrentText(task[3])
            self.ui.statusCombo.setCurrentText(task[4])
            self.ui.dueDateEdit.setDate(QtCore.QDate.fromString(task[6], "yyyy-MM-dd"))
            self.ui.createdDateLabel.setText(f"Created: {task[5][:10]}")

    def _on_save(self):
        title = self.ui.titleEdit.text().strip()
        if not title:
            QMessageBox.warning(self, "Error", "Title cannot be empty.")
            return
        # все ок
        self.accept()

    def get_data(self):
        return {
            "title": self.ui.titleEdit.text(),
            "description": self.ui.descriptionEdit.toPlainText(),
            "priority": self.ui.priorityCombo.currentText(),
            "status": self.ui.statusCombo.currentText(),
            "due_date": self.ui.dueDateEdit.date().toString("yyyy-MM-dd"),
        }


class TaskDetailDialog(PersistentDialog):
    def __init__(self, task, parent=None):
        super().__init__("TaskDetailDialog_geometry", parent)
        self.setWindowTitle("Описание задачи")
        self.setMinimumSize(400, 300)
        layout = QtWidgets.QVBoxLayout(self)
        title = QtWidgets.QLabel(task[1])
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        desc = QtWidgets.QTextEdit()
        desc.setReadOnly(True)
        desc.setPlainText(task[2])
        layout.addWidget(desc)
        due_date_formatted = format_deadline(task[6])
        created_at = task[5][:10] if task[5] else ""
        info_label = QtWidgets.QLabel(f"Дедлайн: {due_date_formatted}    Создана: {created_at}")
        info_label.setStyleSheet("font-size: 12px; color: #5e6c84;")
        layout.addWidget(info_label)
        close_btn = QtWidgets.QPushButton("Закрыть")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
