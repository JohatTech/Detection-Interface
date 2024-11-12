import os
import sys
import time

import cv2
import torch
from ultralytics import YOLO
from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtGui import QAction, QImage, QKeySequence, QPixmap, QIcon, QPalette, QColor
from PySide6.QtWidgets import (QApplication, QSlider, QComboBox, QGroupBox,
                               QHBoxLayout, QLabel, QMainWindow, QPushButton,
                               QSizePolicy, QVBoxLayout, QWidget)


model = YOLO("yolo11n")
conf_options = [0.25, 0.50, 0.60, 0.80, 0.90]
if not torch.cuda.is_available:
    DEVICE= "cpu"
else:
    DEVICE ="cuda"

print(DEVICE)
class Thread(QThread):
    updatedFrame = Signal(QImage)
    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.status = True
        self.cap = True
        self.confidence = 0.25  
        
    def run(self):
        self.cap = cv2.VideoCapture(0)
        while self.status:
            ret, frame = self.cap.read()
            if not ret:
                continue
            results = model.predict(frame, device ='cpu', conf=self.confidence)
            print(self.confidence)
            annotated_frame = results[0].plot()
            color_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            
            h, w, ch = color_frame.shapeEEE
            img = QImage(color_frame.data, w,h, ch*w, QImage.Format_RGB888)
            scaled_img = img.scaled(640, 480, Qt.KeepAspectRatio)
            
            self.updatedFrame.emit(scaled_img)
            print(f" This is the class predicted : {results[0]}")

        sys.exit(-1)

#
# <palette>
#   <color name="Atomic tangerine" hex="FDAD8A" r="253" g="173" b="138" />
#   <color name="Pale Dogwood" hex="FED8CA" r="254" g="216" b="202" />
#   <color name="Pumpkin" hex="FE6601" r="254" g="102" b="1" />
#   <color name="Pumpkin" hex="FE6601" r="254" g="102" b="1" />
#   <color name="Raw umber" hex="8E6656" r="142" g="102" b="86" />
# </palette>
# # #
class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Applus+ Detector")
        self.setWindowIcon(QIcon("./Logo-Applus_orange.jpg"))
        # palette = QPalette()
        # palette.setColor(QPalette.Window, QColor(252, 102, 2))  # Set background color of the window
        # palette.setColor(QPalette.WindowText, QColor(255, 255, 255))  # Set text color to white
        # self.setPalette(palette)
        self.setGeometry(0,0,800,500)
        
    
        widget = QWidget(self)
        layout = QVBoxLayout(self)
        widget.setLayout(layout)


        #camera label 
        self.camera_label = QLabel(self)
        self.camera_label.setFixedSize(640,480)
        
        #confidence slider setting 
        
        self.conf_options = [0.25, 0.50, 0.60, 0.80, 0.90]
        self.config_label = QLabel("Seleciona un umbral de confianza", self)   
        self.slider = QSlider(Qt.Vertical, self)
        self.slider.setMinimum(0)
        self.slider.setMaximum(len(self.conf_options)-1)
        self.slider.setTickPosition(QSlider.TicksAbove)
        self.slider.setTickInterval(1)
        self.slider.valueChanged.connect(self.update_conf)
        
        # Crear el layout de etiquetas de valores
        labels_layout = QVBoxLayout()
        for value in reversed(self.conf_options):  # Invertimos el orden para que coincidan con los ticks
            label = QLabel(f"{value}")
            labels_layout.addWidget(label,1)
        
        slider_layout = QHBoxLayout()
        slider_layout.addLayout(labels_layout)
        slider_layout.addWidget(self.slider)

        camera_slider_layout = QHBoxLayout()
        camera_slider_layout.addWidget(self.camera_label)
        camera_slider_layout.addLayout(slider_layout)
        
        
        #thread setting 
        self.th = Thread(self)
        self.th.finished.connect(self.close)
        self.th.updatedFrame.connect(self.setImage)
        
        #Button layout 
        buttons_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.close_button = QPushButton("Stop")
 
        buttons_layout.addWidget(self.close_button)
        buttons_layout.addWidget(self.start_button)
        right_layout = QHBoxLayout()
        right_layout.addLayout(buttons_layout)


        #main layout
        layout = QVBoxLayout()
        layout.addLayout(camera_slider_layout)
        layout.addLayout(right_layout)
        
        #central widget 
        
        widget = QWidget(self)
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        
        #connections
        
        self.start_button.clicked.connect(self.start)
        self.close_button.clicked.connect(self.kill_thread)
        self.close_button.setEnabled(False)
        
    @Slot()
    def kill_thread(self):
        print("finishing...")
        self.close_button.setEnabled(False)
        self.start_button.setEnabled(True)
        self.th.cap.release()
        cv2.destroyAllWindows()
        self.status = False
        self.th.terminate()
        time.sleep(1)
    @Slot()   
    def start(self):
        print("Starting...")
        self.close_button.setEnabled(True)
        self.start_button.setEnabled(False)
        self.th.start()
    @Slot(QImage)    
    def setImage(self, image):
        self.camera_label.setPixmap(QPixmap.fromImage(image))
        
    @Slot()
    def update_conf(self, value):
        self.th.confidence = self.conf_options[value]

        
            
if __name__=="__main__":
    app = QApplication()
    window = Window()
    window.show()

    sys.exit(app.exec())