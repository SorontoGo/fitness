import sys
from PyQt6.QtWidgets import QApplication
from ui.startwindow import StartWindow



if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Применение стиля
    file = "venv/ui/style.qss"
    with open(file, "r") as f:
        app.setStyleSheet(f.read())

    window = StartWindow()
    window.show()
    sys.exit(app.exec())

