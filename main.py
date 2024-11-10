import os
import sys
import time

import cv2
from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtGui import QAction, QImage, QKeySequence, QPixmap
from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox,
                               QHBoxLayout, QLabel, QMainWindow, QPushButton,
                               QSizePolicy, QVBoxLayout, QWidget)





class Thread(QThread):
    updatedFrame = Signal(QImage)
    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.status = True
        self.cap = True
    def run(self):
        self.cap = cv2.VideoCapture(0)
        while self.status:
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            color_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            h, w, ch = color_frame.shape
            img = QImage(color_frame.data, w,h, ch*w, QImage.Format_RGB888)
            scaled_img = img.scaled(640, 480, Qt.KeepAspectRatio)
            self.updatedFrame.emit(scaled_img)

        sys.exit(-1)



class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Applus+ Detector")
        self.setGeometry(0,0,800,500)
        
    
        widget = QWidget(self)
        layout = QVBoxLayout(self)
        widget.setLayout(layout)


        #camera label 
        self.label = QLabel(self)
        self.label.setFixedSize(640,480)
        
        
        self.th = Thread(self)
        self.th.finished.connect(self.close)
        self.th.updatedFrame.connect(self.setImage)
        
        #Button layout 
        buttons_layout = QHBoxLayout()
        self.button1 = QPushButton("Start")
        self.button2 = QPushButton("Stop")
 
        buttons_layout.addWidget(self.button2)
        buttons_layout.addWidget(self.button1)
        
        
        right_layout = QHBoxLayout()
        right_layout.addLayout(buttons_layout, 1)


        #main layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addLayout(right_layout)
        
        #central widget 
        
        widget = QWidget(self)
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        
        #connections
        
        self.button1.clicked.connect(self.start)
        self.button2.clicked.connect(self.kill_thread)
        self.button2.setEnabled(False)
        
    @Slot()
    def kill_thread(self):
        print("finishing...")
        self.button2.setEnabled(False)
        self.button1.setEnabled(True)
        self.th.cap.release()
        cv2.destroyAllWindows()
        self.status = False
        self.th.terminate()
        time.sleep(1)
    @Slot()   
    def start(self):
        print("Starting...")
        self.button2.setEnabled(True)
        self.button1.setEnabled(False)
        self.th.start()
    @Slot(QImage)    
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))
        
        
if __name__=="__main__":
    app = QApplication()
    window = Window()
    window.show()

    sys.exit(app.exec())