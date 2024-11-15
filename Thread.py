
import cv2
import torch
from ultralytics import YOLO
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtCore import pyqtSignal as Signal

from PyQt5.QtGui import  QImage  

import sys 
import os



class Thread(QThread):
    updatedFrame = Signal(QImage)
    updatedCapture = Signal(QImage)
    update_message = Signal(str)


    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.status = True
        self.model = self.load_model()
        self.get_device()
        self.camera_index = 0
        self.file_path = None
        self.cap = True
        self.frame_count = 0
        self.confidence = 0.25


    def run(self):
        i=0
        print(self.device)
        if self.file_path !=None:
            self.cap = cv2.VideoCapture(self.file_path)

           
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.camera_index)
            print(f"camara encendida: {self.camera_index}")
                
        while self.status:
            ret, frame = self.cap.read()
            self.frame_count += 1      
            
            if not ret:
                continue
            results = self.inference(frame)
            annotated_frame = results[0].plot()
            self.updatedFrame(self.post_processImage(annotated_frame))       
            
            if self.frame_count % 30 == 0:
                detection = self.findClass(results)
                self.take_phot(detection, frame)
    def load_model(self):
        if getattr(sys, "frozen", False):
            modelo_path = os.path.join(sys._MEIPASS, 'detector.pt')
        else:
            # La aplicación está corriendo en modo de desarrollo
            modelo_path = './detector.pt'
        
        return YOLO(modelo_path)
    def get_device(self):
            try:
                result = os.system('nvidia-smi')
                self.device = "cuda:0"
            except Exception as e:
                self.device = "cpu"

    def inference(self,model, frame):
        results = model(frame, device = self.device, conf=self.confidence)
        return results
    
    def post_processImage(self, frame):
        color_captured = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = color_captured.shape
        capture = QImage(color_captured.data, w,h, ch*w, QImage.Format_RGB888)
        scaled_capture = capture.scaled(640, 480, Qt.KeepAspectRatio)
        return scaled_capture
    
    def take_phot(self, frame, detection):
        for class_name, confid in detection:
            if class_name == "poste" and confid >= 0.70:
                i += 1  
                cv2.imwrite(f"./resultados/Poste_{i}.jpg", frame)
                self.update_message.emit(f"Imagen de poste numero: {i} Guardado!")
                self.updatedCapture(self.post_processImage(frame))
                
    def findClass(self, results):
        detected_classes = []  # List to hold detected classes and confidences
            for result in results:
                for det in result.boxes:
                    class_id = int(det.cls)
                    class_name = result.names[class_id]
                    confid = det.conf.item()

                    # Append the class and confidence to the list
                    detected_classes.append((class_name, confid))

        return detected_classes  # Return all detected classes
        