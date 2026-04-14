from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMessageBox
import sys
import re
class DangKyApp:
    def __init__(self):
        self.ui = uic.loadUi("Giaodienchinh.ui")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DangKyApp()
    window.ui.show()
    sys.exit(app.exec())
