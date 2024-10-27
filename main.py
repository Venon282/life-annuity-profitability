import sys
from PyQt6.QtWidgets import QApplication

# internal
from app import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QPushButton {
            padding: 3px 7px 3px 7px;
        }
    """)

    window = MainWindow()
    window.show()
    app.exec()
