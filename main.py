import os
import sys
import time

from Window import Window

from PySide6.QtWidgets import QApplication
            
if __name__=="__main__":
    app = QApplication()
    window = Window()
    window.show()

    sys.exit(app.exec())