
from ultralytics import YOLO 
import numpy as np

class YoloDetector:
    def __init__(self, weights="yolov8n.pt", device="cpu"):
        self.model = YOLO(weights, device=device)

    def predict_people(self, frame, conf=0.4):
        """
        Возвращает список детекций людей:
        [{ 'box': [x1,y1,x2,y2], 'conf': 0.9 }, ...]
        """
        results = self.model.predict(source=frame, conf=conf, imgsz=640, verbose=False)
        detections = []
        r = results[0]
        boxes = r.boxes  
        for box in boxes:
            cls = int(box.cls[0])

            if cls == 0:
                xyxy = box.xyxy[0].cpu().numpy() 
                conf_val = float(box.conf[0].cpu().numpy())
                detections.append({'box': xyxy.tolist(), 'conf': conf_val})
        return detections
