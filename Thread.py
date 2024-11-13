import os
import sys
import time

import cv2
import torch
from ultralytics import YOLO
from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtGui import QAction, QImage, QKeySequence, QPixmap, QIcon, QPalette, QColor
from PIL import Image, ImageDraw, ImageFont
import numpy as np


model = YOLO("yolo11n.pt")
conf_options = [0.25, 0.50, 0.60, 0.80, 0.90]
if not torch.cuda.is_available:
    DEVICE = "cpu"
else:
    DEVICE = "cuda:0"

# def draw_boxes(image, boxes, scores, class_ids, class_names, threshold=0.5):
#     image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
#     draw = ImageDraw.Draw(image)
#     font = ImageFont.load_default()
    
#     for i, box in enumerate(boxes):
#         if scores[i] >= threshold:
#             x, y, w, h = box
#             class_id = class_ids[i]
#             label = f"{class_names[class_id]}: {scores[i]:.2f}"
            
#             # Draw rectangle and label
#             draw.rectangle([x, y, x+w, y+h], outline="red", width=2)
#             draw.text((x, y - 10), label, fill="white", font=font)
    
#     # Convert back to OpenCV format
#     return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


class Thread(QThread):
    updatedFrame = Signal(QImage)
    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.status = True
        self.cap = True
        self.confidence = 0.25  
        
    def run(self):
        i = 0
        self.cap = cv2.VideoCapture(0)
        while self.status:
            ret, frame = self.cap.read()
            if not ret:
                continue
            results = model(frame, device = DEVICE, conf=self.confidence)
            
            for result in results:
                for det in result.boxes:
                    class_id = int(det.cls)
                    class_name=result.names[class_id]
                    confid = det.conf.item()


                    if class_name == "laptop" and confid >=0.90:
                        i += 1  
                        ##time.sleep(3)
                        result.save(f"chair_{i}.jpg")
            


            annotated_frame = results[0].plot()
            # net = cv2.dnn.readNetFromONNX("yolo11n.onnx")
            # blob = cv2.dnn.blobFromImage(frame, scalefactor=1/255.0, size=(640,640), swapRB=True)
            # net.setInput(blob)
            # pred = net.forward()

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