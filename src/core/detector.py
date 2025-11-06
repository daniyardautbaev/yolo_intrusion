from ultralytics import YOLO

class YoloDetector:
    def __init__(self, weights="yolov8n.pt"):

        self.model = YOLO(weights)

    def predict_people(self, frame, conf=0.4, device="cpu"):

        results = self.model.predict(frame, conf=conf, device=device, verbose=False)
        detections = []
        for r in results:
            for box in r.boxes:
                cls = int(box.cls)

                if cls == 0:
                    detections.append({
                        "box": box.xyxy[0].tolist(),
                        "confidence": float(box.conf)
                    })
        return detections
