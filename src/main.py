
import cv2
import time
import numpy as np
import json
import os

from io_utils.zones_io import load_zones, save_zones
from utils.geometry import point_in_polygon
from core.detector import YoloDetector

ZONES_PATH = "restricted_zones.json"
VIDEO_PATH = "assets/test.mp4"
ALARM_TIMEOUT = 3
DEBUG = True 

def ensure_zones_for_frame(frame_w, frame_h):
  
    if os.path.exists(ZONES_PATH):
        zones = load_zones(ZONES_PATH)
        if zones:
            return zones


    left = int(frame_w * 0.70)
    right = int(frame_w * 0.98)
    top = int(frame_h * 0.55)
    bottom = int(frame_h * 0.92)

    zone = {
        "id": "zone_gate_right",
        "name": "right_gate",
        "points": [
            [left, top],
            [right, top],
            [right, bottom],
            [int(left + (right-left)*0.1), bottom]
        ]
    }
    save_zones(ZONES_PATH, [zone])
    print(f"Создана примерная зона и сохранена в {ZONES_PATH}")
    return [zone]

def draw_zones(frame, zones):
    for zone in zones:
        pts = np.array(zone.get("points", []), np.int32)
        if pts.size:
            cv2.polylines(frame, [pts], True, (0, 255, 255), 2)  # желтый

            cx = int(pts[:,0].mean())
            cy = int(pts[:,1].mean())
            cv2.putText(frame, zone.get("name", zone.get("id","")), (cx, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)
    return frame

def draw_detections(frame, detections):
    for d in detections:

        box = d.get('box') or d.get('bbox') or d.get('xyxy')
        if box is None:
            continue
        x1, y1, x2, y2 = map(int, box)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        cv2.circle(frame, (cx, cy), 4, (255, 0, 0), -1)

        conf = d.get('conf') or d.get('confidence') or d.get('score')
        if conf is not None:
            cv2.putText(frame, f"{conf:.2f}", (x1, y1 - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
        if 'id' in d:
            cv2.putText(frame, f"ID:{d['id']}", (x2-40, y1-6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,0), 1)

def safe_get_center(box):
    x1, y1, x2, y2 = box
    return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)

def main():
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print("Не удалось открыть видео:", VIDEO_PATH)
        return


    ret, frame = cap.read()
    if not ret:
        print("Не удалось прочитать первый кадр.")
        return

    frame_h, frame_w = frame.shape[:2]
    zones = ensure_zones_for_frame(frame_w, frame_h)
    if DEBUG:
        print("Загруженные зоны:", json.dumps(zones, indent=2))


    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    detector = YoloDetector(weights="yolov8n.pt")  
    alarm_on = False
    last_seen_time = 0

    print("Запуск. Нажми 'q' чтобы выйти.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        try:
            raw_dets = detector.predict_people(frame, conf=0.45, device="cpu")
        except TypeError:
            
            raw_dets = detector.predict_people(frame, conf=0.45)

      
        detections = []
        for rd in raw_dets:

            box = rd.get('box') if isinstance(rd, dict) else None
            if box is None and hasattr(rd, 'xyxy'):

                box = list(map(float, rd.xyxy))
            if box is None:
                continue
            detections.append({
                'box': [float(box[0]), float(box[1]), float(box[2]), float(box[3])],
                'conf': float(rd.get('conf') or rd.get('confidence') or rd.get('score', 0.0))
            })

        if DEBUG:
            print(f"Detections count: {len(detections)}")
            for i, d in enumerate(detections):
                cx, cy = safe_get_center(d['box'])
                print(f"  det#{i} center=({cx:.1f},{cy:.1f}) conf={d['conf']:.2f}")

        person_in_zone = False
        alarm_point = None 

        for d in detections:
            x1, y1, x2, y2 = d['box']

            cx = (x1 + x2) / 2
            cy = y2  

            for zone in zones:
                poly = zone.get('points', [])
                poly = [[float(p[0]), float(p[1])] for p in poly]
                try:
                    if point_in_polygon((float(cx), float(cy)), poly):
                        person_in_zone = True
                        alarm_point = (int(cx), int(cy))
                        if DEBUG:
                            print(f" Человек в зоне: {zone.get('name', zone.get('id'))} "
                                  f"({cx:.1f}, {cy:.1f})")
                        break
                except Exception as e:
                    print("Ошибка проверки point_in_polygon:", e)

            if person_in_zone:
                break

        if person_in_zone:
            alarm_on = True
            last_seen_time = time.time()
        elif alarm_on and (time.time() - last_seen_time > ALARM_TIMEOUT):
            alarm_on = False

        draw_zones(frame, zones)
        draw_detections(frame, detections)

        if alarm_point is not None:
            cv2.circle(frame, alarm_point, 6, (0, 0, 255), -1)

        if alarm_on:
            cv2.putText(frame, "ALARM!", (50, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 0, 255), 4)


        cv2.imshow("Intrusion Detection", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('p'):
            cv2.imwrite("assets/zone_screenshot_current.png", frame)
            print("Скрин сохранён: assets/zone_screenshot_current.png")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
