import cv2
import time
from io_utils.zones_io import load_zones

ZONES_PATH = "restricted_zones.json"
VIDEO_PATH = "assets/test.mp4"

ALARM_TIMEOUT = 3 

def draw_zones(frame , zones ):
    for zone in zones :
        pts = zone.get("points" , [])
        if pts:
            cv2.polylines(frame, [np.array(pts, np.int32)], True, (0, 255, 255), 2)
    return frame

def main():
    zones = load_zones(ZONES_PATH)
    cap = cv2.VideoCapture(VIDEO_PATH)

    if not cap.isOpened():
        print("Не удалось открыть видео")
        return

    alarm_on = False
    last_seen_time = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = draw_zones(frame , zones)
        if alarm_on:
            cv2.putText(frame, "ALARM!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
            if time.time() - last_seen_time > ALARM_TIMEOUT:
                alarm_on = False

        cv2.imshow("Intrusion Detection", frame)

        key = cv2.waitKey(30) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('a'):
            alarm_on = True
            last_seen_time = time.time()

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    import numpy as np
    main()
