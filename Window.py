import cv2
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtCore import pyqtSlot as Slot

from PyQt5.QtGui import  QImage, QPixmap, QIcon, QPalette, QColor
from PyQt5.QtWidgets import ( QSlider, QComboBox, QHBoxLayout, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget, QAction, QFileDialog)
from Thread import Thread


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Applus+ Vision 1.0")
        self.setWindowIcon(QIcon("./Logo-Applus_orange.jpg"))
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255))  # Set background color of the window
        palette.setColor(QPalette.WindowText, QColor(0, 0, 0))  # Set text color to white
        self.setPalette(palette)
        self.setGeometry(0,0,800,500)

        widget = QWidget(self)
        layout = QVBoxLayout(self)
        widget.setLayout(layout)
        #message label
        self.message_label = QLabel("Detectando...",self)
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("background-color: Black; color: white; font-size: 20px")
        
        #photo shooting label 
        self.shoot_label = QLabel(self)
        self.shoot_label.setFixedSize(640,480)
        self.shoot_label.setStyleSheet("background-color: black; color: transparent ; font-size: 20px; ")

        self.camera_selection= QComboBox()
        self.camera_selection.addItem("Camera 1")
        
        self.camera_selection.addItem("Camera 2")
        #stream camera label 
        self.camera_label = QLabel(self)
        self.camera_label.setFixedSize(640,480)
        self.camera_label.setStyleSheet("background-color: black; color: transparent ; font-size: 20px; ")

        camera_shoot_layout = QHBoxLayout()
        camera_shoot_layout.addWidget(self.camera_label)
        camera_shoot_layout.addWidget(self.shoot_label)
 
        #menu bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("Archivos")

        load_action = QAction("Cargar image", self)
        file_menu.addAction(load_action)
        load_action.triggered.connect(self.load_file)
        
        # confidence slider setting 
        
        self.conf_options = [0.25, 0.50, 0.60, 0.80, 0.90]
        self.config_label = QLabel("Ajuste de nivel de confianza", self)   
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setMinimum(0)
        self.slider.setMaximum(len(self.conf_options)-1)
        self.slider.setTickPosition(QSlider.TicksAbove)
        self.slider.setTickInterval(1)
        self.slider.valueChanged.connect(self.update_conf)
        
        # Crear el layout de etiquetas de valores
        labels_layout = QHBoxLayout()
        for value in self.conf_options:  # Invertimos el orden para que coincidan con los ticks
            label = QLabel(f"{value}")
            labels_layout.addWidget(label,1)
        
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.config_label)
        slider_layout.addWidget(self.camera_selection)

        camera_slider_layout = QVBoxLayout()
        camera_slider_layout.addLayout(camera_shoot_layout)
        camera_slider_layout.addLayout(labels_layout)
        camera_slider_layout.addLayout(slider_layout)
        
        
        #thread setting 
        self.th = Thread(self)
        self.th.finished.connect(self.close)
        self.th.updatedFrame.connect(self.setImage)
        self.th.update_message.connect(self.display_message)
        self.th.updatedCapture.connect(self.setCapture)
        
        
        #timer
        self.message_reset = QTimer(self)
        self.message_reset.setSingleShot(True)
        self.message_reset.timeout.connect(self.reset_message)

        #Button layout 
        buttons_layout = QHBoxLayout()
        self.start_button = QPushButton("Iniciar")
        self.start_button.setStyleSheet("background-color: green; color: white ; font-size: 20px; ")
        self.close_button = QPushButton("Detener")
        self.close_button.setStyleSheet("background-color: red; color: white ; font-size: 20px; ")
        buttons_layout.addWidget(self.close_button)
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.message_label)
        right_layout = QHBoxLayout()
        right_layout.addLayout(buttons_layout)
        #camera selection




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
        self.message_label.setText("Deteccion finalizada")
        self.th.cap.release()
        self.status = False
        self.th.terminate()

    
    @Slot()   
    def start(self):
        print("Starting...")
        self.message_label.setText("Iniciando...")
        self.close_button.setEnabled(True)
        self.start_button.setEnabled(False)
        self.th.start()
        self.message_label.setText("Detectando...")
    @Slot(QImage)    
    def setImage(self, image):
        self.camera_label.setPixmap(QPixmap.fromImage(image))
    @Slot(QImage)
    def setCapture(self, capture):
        self.shoot_label.setPixmap(QPixmap.fromImage(capture))
        
    @Slot(str)
    def display_message(self, message):
        self.message_label.setText(message)
        self.message_label.setStyleSheet("background-color: #FFA500; color: white; font-size: 20px")
        self.message_reset.start(1000)
    @Slot(int)
    def update_conf(self, value):
        self.th.confidence = self.conf_options[value]

    @Slot()
    def reset_message(self):
        self.message_label.setText("Detectando...")
        self.message_label.setStyleSheet("background-color: black; color: white; font-size: 20px")
    
    @Slot()
    def cameraselected(self):
        if self.camera_selection.currentIndex == 0:
            self.th.camera_index = 0 
        else:
            self.th.camera_index = 1


    @Slot()
    def load_file(self):
        options = QFileDialog.Options()

        file_path, _ = QFileDialog.getOpenFileName(self,
                                                  "Open File",
                                                  "",  # Initial directory
                                                   "All Files (*);;Text Files (*.txt);;Images (*.png *.jpg)",  # File filters
                                                   options=options
                                                  )
        if file_path:
            print("file loaded")
            self.th.file_path = file_path
        else:
            print("file not readed")
        
        