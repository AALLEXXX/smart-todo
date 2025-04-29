from datetime import datetime

from PyQt6 import QtCore
from PyQt6 import QtGui
from PyQt6 import QtWidgets
from PyQt6.QtCore import QByteArray
from PyQt6.QtCore import QMimeData
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDrag
from PyQt6.QtGui import QPainter
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication

import config
from app.db import resource_path
from app.utils import format_deadline


class TaskCard(QtWidgets.QFrame):
    def __init__(
        self,
        task,
        theme="light",
        parent=None,
        on_delete=None,
        on_archive=None,
        on_edit=None,
        on_view=None,
    ):
        super().__init__(parent)
        self.setProperty("priority", task[3].lower())

        self.task = task
        self.on_delete = on_delete
        self.on_archive = on_archive
        self.on_edit = on_edit
        self.on_view = on_view

        # Базовые настройки виджета
        self.setObjectName("taskCard")
        self.setMaximumSize(config.CARD_WIDTH, config.CARD_HEIGHT)
        self.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.setMouseTracking(True)
        self._drag_start_pos = None

        # Основной layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Заголовок
        title_layout = QtWidgets.QHBoxLayout()
        title_label = QtWidgets.QLabel(task[1])
        title_label.setWordWrap(True)
        title_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        # 1) label растягивается, чтобы занять всё доступное место до иконки
        title_label.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Maximum,
        )
        # 2) добавляем с stretch=1
        title_layout.addWidget(title_label, 1)

        # 3) иконка «просрочен»
        due_str = task[6]
        if due_str:
            try:
                due_dt = datetime.fromisoformat(due_str).date()
                if due_dt < datetime.now().date():
                    icon = QtWidgets.QLabel()
                    pix = QtGui.QPixmap(resource_path("icons/timeover.png"))
                    icon.setPixmap(
                        pix.scaled(
                            16,
                            16,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation,
                        )
                    )
                    # фиксируем иконку по размеру — не даст ей расширяться
                    icon.setSizePolicy(
                        QtWidgets.QSizePolicy.Policy.Fixed,
                        QtWidgets.QSizePolicy.Policy.Fixed,
                    )
                    title_layout.addWidget(icon)
            except ValueError:
                pass

        main_layout.addLayout(title_layout)

        # Дата
        due = format_deadline(task[6])
        created = task[5][:10] if task[5] else ""
        deadline_label = QtWidgets.QLabel(f"Дедлайн: {due}    Создана: {created}")
        deadline_label.setStyleSheet("font-size: 12px;")
        main_layout.addWidget(deadline_label)

        # Кнопки
        button_layout = QtWidgets.QHBoxLayout()
        for icon, tooltip, handler in (
            ("👁", "View details", self.on_view),
            ("✏", "Edit task", self.on_edit),
            ("❌", "Delete task", self.on_delete),
        ):
            btn = QtWidgets.QPushButton(icon)
            btn.setToolTip(tooltip)
            btn.clicked.connect(lambda _, h=handler: h(self.task) if h else None)
            button_layout.addWidget(btn)

        if task[4] == "Done" and self.on_archive:
            archive_btn = QtWidgets.QPushButton("🗄")
            archive_btn.setToolTip("Archive task")
            archive_btn.clicked.connect(lambda: self.on_archive(self.task))
            button_layout.addWidget(archive_btn)

        main_layout.addLayout(button_layout)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._drag_start_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if event.buttons() & QtCore.Qt.MouseButton.LeftButton and self._drag_start_pos is not None:
            distance = (event.pos() - self._drag_start_pos).manhattanLength()
            if distance >= QApplication.startDragDistance():
                drag = QDrag(self)
                mime = QMimeData()
                mime.setData("application/x-task-id", QByteArray(str(self.task[0]).encode()))
                drag.setMimeData(mime)

                pixmap = QPixmap(self.size())
                pixmap.fill(Qt.GlobalColor.transparent)
                painter = QPainter(pixmap)
                self.render(painter)
                painter.end()

                drag.setPixmap(pixmap)
                drag.setHotSpot(event.pos())
                # сбрасываем, чтобы больше не заходить сюда
                self._drag_start_pos = None
                drag.exec(Qt.DropAction.MoveAction)
                return  # не вызываем super() после возможного удаления
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        self._drag_start_pos = None
        super().mouseReleaseEvent(event)
