import sys
from scripts.Window import Window

from PyQt5.QtWidgets import QApplication
            
if __name__=="__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()

    sys.exit(app.exec())