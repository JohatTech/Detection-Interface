from logs.logger_config import get_logger
import sys 
import os

import cv2
from ultralytics import YOLO
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtGui import  QImage  


logger = get_logger(__name__)


class Thread(QThread):
    updatedFrame = Signal(QImage)
    updatedCapture = Signal(QImage)
    update_message = Signal(str)


    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        logger.info("THREAD INICIADO")
        self.status = True
        self.get_device()
        logger.info(f"DEVICE ENCONTRADO , TIPO: {self.device}")
        self.camera_index = 0
        logger.info(f"CAMERA INDEX SELECTED:{self.camera_index}")
        self.file_path = ""
        self.cap = True
        self.frame_count = 0
        self.confidence = 0.25
        logger.info(f"INICANDO UMBRAL A {self.confidence} ")
        self.i=0


    def run(self):
        self.model = self.load_model()
        logger.info(f"INCIANDO THREAD CON DEVICE TIPO: {self.device}")
        if self.file_path != "":
            try:
                self.cap = cv2.VideoCapture(self.file_path)
                logger.info(f"OPENCV LOGRO LEER EL ARCHIVO ")
            except cv2.error as e:
                logger.error(f"NO SE PUDO LEER EL ARCHIVO POR EL SIGUIENTE ERROR: {e}")
        else:
            try:       
                self.cap = cv2.VideoCapture(self.camera_index)
                logger.info(f"OPENCV ESTA ENCENDIENDO CAMARA...: {self.camera_index}")
            except IOError as e:
             logger.error(f"ERROR ENCENDIENDO LA CAMARA: {e} | REVISAR CONEXION ")
             
        while self.status or self.cap.isOpened():
            ret, frame = self.cap.read()
            logger.info("LEYENDO FRAMES ")
            self.frame_count += 1      
            if not ret:
                logger.error("ERROR: SE PERDIO CONEXION DE CAMARA, REVISAR")
                break
            results = self.inference(self.model,frame)
            annotated_frame = results[0].plot()
            self.updatedFrame.emit(self.post_processImage(annotated_frame))       
            
            if self.frame_count % 20 == 0:
                detection = self.findClass(results)
                self.take_photo(frame, detection)
                continue
        self.cap.release()
  

    def load_model(self):
        if getattr(sys, "frozen", False):
            modelo_path = os.path.join(sys._MEIPASS, './models/detector.pt')
        else:
            # La aplicación está corriendo en modo de desarrollo
            modelo_path = './models/detector.pt'
        
        return YOLO(modelo_path)
    def get_device(self):
            try:
                result = os.system('nvidia-smi')
                logger.info("GPU FINDED")
                self.device = "cuda:0"
            except Exception as e:
                logger.warning("GPU NO ENCONTRADA, HACIENDO INFERENCIAS EN CPU, SE VERA ALTA LATENCIA")
                self.device = "cpu"

    def inference(self,model, frame):
        results = model.predict(frame, device = self.device, conf=self.confidence, half=True)
        return results
    
    def post_processImage(self, frame):

        color_captured = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = color_captured.shape
        capture = QImage(color_captured.data, w,h, ch*w, QImage.Format_RGB888)
        scaled_capture = capture.scaled(640, 480, Qt.KeepAspectRatio)
        return scaled_capture


    def take_photo(self, frame, detection):
        for class_name, confid in detection:
            if class_name == "poste" and confid >= 0.70:
                self.i += 1  
                cv2.imwrite(f"./resultados/Poste_{self.i}.jpg", frame)
                logger.info("IMAGEN CAPTURADA A SIDO GUARDADA")
                self.update_message.emit(f"Imagen de poste numero: {self.i} Guardado!")
                self.updatedCapture.emit(self.post_processImage(frame))

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