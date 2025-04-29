import os

from PyQt6.uic import compileUi

UI_FOLDER = "app/ui"
OUTPUT_FOLDER = "app/ui"

for filename in os.listdir(UI_FOLDER):
    if filename.endswith(".ui"):
        ui_path = os.path.join(UI_FOLDER, filename)
        py_path = os.path.join(OUTPUT_FOLDER, f"ui_{filename.replace('.ui', '')}.py")
        with open(py_path, "w", encoding="utf-8") as fout:
            compileUi(ui_path, fout)
        print(f"Compiled: {ui_path} → {py_path}")
