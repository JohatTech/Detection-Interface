from logs.logger_config import get_logger

from PyQt5.QtWidgets import (QHBoxLayout, QLabel, QWidget)

logger = get_logger(__name__)

class CameraDisplay(QWidget):
    def __init__(self, parent= None):
        super().__init__(parent)
        #photo shooting label 
        self.shoot_label = QLabel(self)
        self.shoot_label.setFixedSize(640,480)
        self.shoot_label.setStyleSheet("background-color: black; color: transparent ; font-size: 20px; ")
        #stream camera label 
        self.camera_label = QLabel(self)
        self.camera_label.setFixedSize(640,480)
        self.camera_label.setStyleSheet("background-color: black; color: transparent ; font-size: 20px; ")

        camera_shoot_layout = QHBoxLayout()
        camera_shoot_layout.addWidget(self.camera_label)
        camera_shoot_layout.addWidget(self.shoot_label)
        self.setLayout(camera_shoot_layout)
 
