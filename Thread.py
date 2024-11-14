
import cv2
import torch
from ultralytics import YOLO
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtCore import pyqtSignal as Signal

from PyQt5.QtGui import  QImage  

import sys 
import os
if getattr(sys, "frozen", False):
    modelo_path = os.path.join(sys._MEIPASS, 'detector.pt')
else:
    # La aplicación está corriendo en modo de desarrollo
    modelo_path = './detector.pt'

model = YOLO("yolo11n.pt")



conf_options = [0.25, 0.50, 0.60, 0.80, 0.90]
if not torch.cuda.is_available:
    DEVICE = "cpu"
else:
    DEVICE = "cuda:0"




class Thread(QThread):
    updatedFrame = Signal(QImage)
    updatedCapture = Signal(QImage)
    update_message = Signal(str)

    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.status = True
        self.cap = True

        self.frame_count = 0
        self.confidence = 0.25  

    def run(self):
        i=1
        for i in range(4):
            self.cap = cv2.VideoCapture(i)
            if self.cap.isOpened():
                break
        while self.status:
            ret, frame = self.cap.read()
            if not ret:
                continue
            self.frame_count += 1      
            results = model(frame, device = DEVICE, conf=self.confidence)

            if self.frame_count % 40 ==0:
                for result in results:
                    for det in result.boxes:
                        class_id = int(det.cls)
                        class_name=result.names[class_id]
                        confid = det.conf.item()
                        if class_name == "laptop" and confid >=0.70:
                            cv2.imwrite(f"./resultados/Poste_{i}.jpg", frame)
                            self.update_message.emit(f"Imagen de poste numero: {i} Guardado!")
                            i += 1  
                            
                            
                            color_captured = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            h, w, ch = color_captured.shape
                            capture = QImage(color_captured.data, w,h, ch*w, QImage.Format_RGB888)
                            scaled_capture = capture.scaled(640, 480, Qt.KeepAspectRatio)
                            
                            self.updatedCapture.emit(scaled_capture)      
            
            annotated_frame = results[0].plot()
            color_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            
            h, w, ch = color_frame.shape
            img = QImage(color_frame.data, w,h, ch*w, QImage.Format_RGB888)
            scaled_img = img.scaled(640, 480, Qt.KeepAspectRatio)
            
            self.updatedFrame.emit(scaled_img)
        


if __name__ == "__main__":
    YOLO("detector.pt")

    # Run inference on an image
    results = model("images/test.jpg")  # results list

    # View results
    for r in results:
        print(r.probs)