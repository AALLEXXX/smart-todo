from datetime import datetime

from PyQt6 import QtWidgets

import config
from app.components.task_card import TaskCard
from app.db import add_task
from app.db import archive_task
from app.db import delete_task
from app.db import get_active_tasks
from app.db import update_task
from app.windows.task_dialog import TaskDetailDialog
from app.windows.task_dialog import TaskDialog


class BoardController:
    """Encapsulates all board-related UI logic."""

    def __init__(self, board_widget, parent):
        self.parent = parent
        self.ui = parent.board_ui

        self.setup_width()
        self.setup_signals()
        self.setup_drag_drop()
        self.load_tasks()

    def setup_width(self):
        fw = config.FIXED_WIDTH_COLUMN
        self.ui.backlogArea.setMinimumWidth(fw)
        self.ui.backlogArea.setMaximumWidth(fw)
        self.ui.inProgressArea.setMinimumWidth(fw)
        self.ui.inProgressArea.setMaximumWidth(fw)
        self.ui.blockedArea.setMinimumWidth(fw)
        self.ui.blockedArea.setMaximumWidth(fw)
        self.ui.doneArea.setMinimumWidth(fw)
        self.ui.doneArea.setMaximumWidth(fw)

    def setup_signals(self):
        self.ui.lowPriorityCheckBox.stateChanged.connect(self.load_tasks)
        self.ui.mediumPriorityCheckBox.stateChanged.connect(self.load_tasks)
        self.ui.highPriorityCheckBox.stateChanged.connect(self.load_tasks)
        self.ui.addTaskButton.clicked.connect(self.add_task)
        self.ui.archiveButton.clicked.connect(self.parent.open_archive)

    def setup_drag_drop(self):
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
            container.dragEnterEvent = self.create_drag_enter_event()
            container.dropEvent = self.create_drop_event(status)

    def create_drag_enter_event(self):
        def dragEnterEvent(event):
            if event.mimeData().hasFormat("application/x-task-id"):
                event.acceptProposedAction()

        return dragEnterEvent

    def create_drop_event(self, status):
        def dropEvent(event):
            data = event.mimeData().data("application/x-task-id")
            try:
                task_id = int(data.data().decode())
            except Exception:
                return
            update_task(task_id, status=status)
            self.load_tasks()
            event.acceptProposedAction()

        return dropEvent

    def clear_columns(self):
        for layout in self.columns.values():
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

    def load_tasks(self):
        self.clear_columns()
        # собираем выбранные приоритеты
        selected = []
        if self.ui.lowPriorityCheckBox.isChecked():
            selected.append("Low")
        if self.ui.mediumPriorityCheckBox.isChecked():
            selected.append("Medium")
        if self.ui.highPriorityCheckBox.isChecked():
            selected.append("High")
        if not selected:
            selected = ["Low", "Medium", "High"]

        # получаем и фильтруем задачи
        tasks = [t for t in get_active_tasks() if t[3] in selected]

        # сортируем по дедлайну: ближайшие в начало
        def due_key(t):
            d = t[6]
            try:
                return datetime.fromisoformat(d) if d else datetime.max
            except ValueError:
                return datetime.max

        tasks.sort(key=due_key)

        # распределяем по статусам
        tasks_by_status = {k: [] for k in self.columns}
        for task in tasks:
            card = TaskCard(
                task,
                theme=self.parent.current_theme,
                on_delete=self.confirm_delete,
                on_archive=self.archive_task,
                on_edit=self.edit_task,
                on_view=lambda t: TaskDetailDialog(t, self.parent).exec(),
            )
            tasks_by_status[task[4]].append(card)

        # добавляем карточки в колонки
        for status, cards in tasks_by_status.items():
            layout = self.columns[status]
            for card in cards:
                layout.addWidget(card)
            layout.addStretch()

    def confirm_delete(self, task):
        ans = QtWidgets.QMessageBox.question(
            self.parent,
            "Confirm Delete",
            f"Are you sure you want to delete '{task[1]}'?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
        )
        if ans == QtWidgets.QMessageBox.StandardButton.Yes:
            delete_task(task[0])
            self.load_tasks()

    def archive_task(self, task):
        archive_task(task[0])
        self.load_tasks()

    def add_task(self):
        dlg = TaskDialog(self.parent)
        if dlg.exec():
            data = dlg.get_data()
            add_task(**data, sort_index=0)
            self.load_tasks()

    def edit_task(self, task):
        dlg = TaskDialog(self.parent, task=task)
        if dlg.exec():
            data = dlg.get_data()
            update_task(task[0], **data)
            self.load_tasks()
