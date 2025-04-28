from PyQt6 import QtCore
from PyQt6 import QtWidgets

import config


class PersistentDialog(QtWidgets.QDialog):
    """Базовый класс для диалоговых окон с сохранением геометрии."""

    def __init__(self, geometry_key, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry_key = geometry_key
        self.settings = QtCore.QSettings(config.ORGANIZATION, config.APP_NAME)
        geometry = self.settings.value(self.geometry_key)
        if geometry is not None:
            self.restoreGeometry(geometry)

    def closeEvent(self, event):
        self.settings.setValue(self.geometry_key, self.saveGeometry())
        super().closeEvent(event)
