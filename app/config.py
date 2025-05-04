import os

from PyQt6 import QtCore

VERSION = "v0.3.0"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_NAME = "Todo"
ORGANIZATION = "Alex"

# Темы оформления: пути к qss-файлам
THEMES = {"light": os.path.join("styles", "style_light.qss"), "dark": os.path.join("styles", "style_dark.qss")}

USER_CONFIG_PATH = os.path.join(BASE_DIR, "user_config.ini")


def load_user_theme():
    # Используем QSettings в формате INI для загрузки настроек из файла user_config.ini
    settings = QtCore.QSettings(USER_CONFIG_PATH, QtCore.QSettings.Format.IniFormat)
    theme = settings.value("General/theme", "light")
    return theme


def save_user_theme(theme):
    settings = QtCore.QSettings(USER_CONFIG_PATH, QtCore.QSettings.Format.IniFormat)
    settings.setValue("General/theme", theme)


# Размеры главного окна по умолчанию
DEFAULT_WINDOW_WIDTH = 800
DEFAULT_WINDOW_HEIGHT = 600

# Ключ для сохранения геометрии главного окна в QSettings
WINDOW_GEOMETRY_KEY = "main_window_geometry"

# Цвета для задач по приоритету
# Low – голубой, Medium – синий, High (hard) – алый
PRIORITY_COLORS = {
    "Low": "#87CEFA",  # голубой
    "Medium": "#0000FF",  # синий
    "High": "#FF2400",  # алый
}

ARCHIVE_WINDOW_WIDTH = 500
ARCHIVE_WINDOW_HEIGHT = 800

FIXED_WIDTH_COLUMN = 350

CARD_WIDTH = 350
CARD_HEIGHT = 200

BUILD_MODE = "dev"

DB_PATH = "app/data/todo.db"
