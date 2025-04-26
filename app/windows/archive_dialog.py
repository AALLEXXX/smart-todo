from PyQt6 import QtWidgets

from app.components.task_card import TaskCard
from app.db import delete_task
from app.db import get_archived_tasks
from app.db import update_task
from app.ui.ui_ArchiveDialog import Ui_ArchiveDialog
from app.windows.base_dialog import PersistentDialog
from app.windows.task_dialog import TaskDetailDialog
from app.windows.task_dialog import TaskDialog


class ArchiveDialog(PersistentDialog):
    def __init__(self, parent=None):
        super().__init__("ArchiveDialog_geometry", parent)
        self.ui = Ui_ArchiveDialog()
        self.ui.setupUi(self)
        self.ui.closeButton.clicked.connect(self.close)
        self.load_archived_tasks()

    def clear_layout(self, layout):
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                child_layout = item.layout()
                if child_layout is not None:
                    self.clear_layout(child_layout)

    def load_archived_tasks(self):
        # Получаем текущий лейаут. Если его нет, создаём новый.
        layout = self.ui.archiveList.layout()
        if layout is None:
            layout = QtWidgets.QVBoxLayout()
            self.ui.archiveList.setLayout(layout)
        else:
            self.clear_layout(layout)
        # Добавляем карточки заново
        for task in get_archived_tasks():
            card = TaskCard(
                task,
                theme=self.parent().current_theme,
                on_view=lambda t: TaskDetailDialog(t, self).exec(),
                on_delete=self.confirm_delete,
                on_edit=self.edit_task,
            )
            layout.addWidget(card)
        layout.addStretch()
        layout.update()

    def confirm_delete(self, task):
        confirm = QtWidgets.QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{task[1]}'?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
        )
        if confirm == QtWidgets.QMessageBox.StandardButton.Yes:
            delete_task(task[0])
            self.load_archived_tasks()

    def edit_task(self, task):
        dialog = TaskDialog(self, task=task)
        if dialog.exec():
            data = dialog.get_data()
            update_task(task[0], **data)
            self.load_archived_tasks()
