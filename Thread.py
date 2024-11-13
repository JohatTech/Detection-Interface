import os
import sys
import time
import asyncio

import cv2
import torch
from ultralytics import YOLO
from PySide6.QtCore import Qt, QThread, Signal, Slot, QTimer
from PySide6.QtGui import QAction, QImage, QKeySequence, QPixmap, QIcon, QPalette, QColor
from PIL import Image, ImageDraw, ImageFont
import numpy as np


model = YOLO("detector.pt")
conf_options = [0.25, 0.50, 0.60, 0.80, 0.90]
if not torch.cuda.is_available:
    DEVICE = "cpu"
else:
    DEVICE = "cuda:0"
class Thread(QThread):
    updatedFrame = Signal(QImage)
    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.status = True
        self.cap = True

        self.frame_count =0
        self.confidence = 0.25  

    def run(self):
        i=0
        self.cap = cv2.VideoCapture(0)
        while self.status:
            ret, frame = self.cap.read()
            if not ret:
                continue
            self.frame_count += 1      
            results = model(frame, device = DEVICE, conf=self.confidence)

            if self.frame_count % 30 ==0:
                for result in results:
                    for det in result.boxes:
                        class_id = int(det.cls)
                        class_name=result.names[class_id]
                        confid = det.conf.item()
                        if class_name == "poste" and confid >=0.70:
                            i += 1  
                            cv2.imwrite(f"Poste_{i}.jpg", frame)
        
            
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