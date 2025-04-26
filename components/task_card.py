from PyQt6 import QtWidgets, QtGui, QtCore

import config
from utils import format_deadline


class TaskCard(QtWidgets.QFrame):
    def __init__(self, task, theme="light", parent=None,
                 on_delete=None, on_archive=None, on_edit=None, on_view=None):
        super().__init__(parent)
        self.task = task
        self.on_delete = on_delete
        self.on_archive = on_archive
        self.on_edit = on_edit
        self.on_view = on_view

        # Для светлой темы: фон карточки белый, для тёмной — тёмно-серый; левая граница – цвет приоритета.
        if theme == "light":
            card_bg = "#ffffff"
            text_color = "#172b4d"
        else:
            card_bg = "#2b2b2b"
            text_color = "#ffffff"
        priority_color = config.PRIORITY_COLORS.get(task[3], "#87CEFA")

        self.setMaximumSize(config.CARD_WIDTH, config.CARD_HEIGHT)
        self.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.setObjectName("taskCard")
        # Используем RichText + CSS для принудительного переноса даже длинных слов
        self.setStyleSheet(f"""
        QFrame#taskCard {{
            background-color: {card_bg};
            color: {text_color};
            border: 1px solid #dfe1e6;
            border-left: 5px solid {priority_color};
            border-radius: 5px;
            padding: 10px;
            font-family: Arial, sans-serif;
        }}
        QLabel {{
            color: {text_color};
            white-space: pre-wrap;
            word-break: break-all;
        }}
        QPushButton {{
            border: none;
            background: transparent;
            font-size: 14px;
            color: {text_color};
        }}
        QPushButton:hover {{
            color: #e53935;
        }}
        """)
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 1) Заголовок задачи: используем HTML для принудительного переноса
        title_label = QtWidgets.QLabel(task[1])
        title_label.setWordWrap(True)
        title_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        title_label.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Maximum)
        title_label.setMaximumWidth(config.CARD_WIDTH - 30)  # вычитаем отступы
        main_layout.addWidget(title_label)

        # 2) Дедлайн и дата создания
        due_date_formatted = format_deadline(task[6])
        created_at = task[5][:10] if task[5] else ""
        deadline_label = QtWidgets.QLabel(f"Дедлайн: {due_date_formatted}    Создана: {created_at}")
        deadline_label.setStyleSheet("font-size: 12px;")
        main_layout.addWidget(deadline_label)

        # 3) Блок кнопок под информацией
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(10)
        view_btn = QtWidgets.QPushButton("👁")
        view_btn.setToolTip("View details")
        view_btn.clicked.connect(lambda: self.on_view(self.task) if self.on_view else None)
        button_layout.addWidget(view_btn)

        edit_btn = QtWidgets.QPushButton("✏")
        edit_btn.setToolTip("Edit task")
        edit_btn.clicked.connect(lambda: self.on_edit(self.task) if self.on_edit else None)
        button_layout.addWidget(edit_btn)

        delete_btn = QtWidgets.QPushButton("❌")
        delete_btn.setToolTip("Delete task")
        delete_btn.clicked.connect(lambda: self.on_delete(self.task) if self.on_delete else None)
        button_layout.addWidget(delete_btn)

        if task[4] == "Done" and self.on_archive:
            archive_btn = QtWidgets.QPushButton("🗄")
            archive_btn.setToolTip("Archive task")
            archive_btn.clicked.connect(lambda: self.on_archive(self.task))
            button_layout.addWidget(archive_btn)

        main_layout.addLayout(button_layout)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))

    def mouseDoubleClickEvent(self, event):
        if self.on_view:
            self.on_view(self.task)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            drag = QtGui.QDrag(self)
            mime_data = QtCore.QMimeData()
            mime_data.setData("application/x-task-id", str(self.task[0]).encode())
            drag.setMimeData(mime_data)
            drag.setPixmap(QtGui.QPixmap())
            drag.exec(QtCore.Qt.DropAction.MoveAction)
