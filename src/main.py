
import cv2
import time
import numpy as np

from io_utils.zones_io import load_zones
from utils.geometry import point_in_polygon
from core.detector import YoloDetector

ZONES_PATH = "restricted_zones.json"
VIDEO_PATH = "assets/test.mp4"
ALARM_TIMEOUT = 3

def draw_zones(frame, zones):
    for zone in zones:
        pts = np.array(zone.get("points", []), np.int32)
        if pts.size:
            cv2.polylines(frame, [pts], True, (0, 255, 255), 2)
    return frame

def draw_detections(frame, detections):
    for d in detections:
        x1,y1,x2,y2 = map(int, d['box'])
        cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
        cx, cy = (x1 + x2)//2, (y1 + y2)//2
        cv2.circle(frame, (cx,cy), 3, (255,0,0), -1)

def main():
    zones = load_zones(ZONES_PATH)
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print("Не удалось открыть видео")
        return

    detector = YoloDetector(weights="yolov8n.pt", device="cpu")

    alarm_on = False
    last_seen_time = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        detections = detector.predict_people(frame, conf=0.4)

        person_in_zone = False
        for d in detections:
            x1,y1,x2,y2 = d['box']
            cx, cy = (x1 + x2)/2, (y1 + y2)/2
            for zone in zones:
                if point_in_polygon((cx, cy), zone['points']):
                    person_in_zone = True
                    break
            if person_in_zone:
                break

        if person_in_zone:
            alarm_on = True
            last_seen_time = time.time()


        if alarm_on and (time.time() - last_seen_time > ALARM_TIMEOUT):
            alarm_on = False


        frame = draw_zones(frame, zones)
        draw_detections(frame, detections)
        if alarm_on:
            cv2.putText(frame, "ALARM!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.6, (0, 0, 255), 4)

        cv2.imshow("Intrusion Detection", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
