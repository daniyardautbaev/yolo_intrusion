import cv2
import json
import time
import os
import numpy as np

from io_utils.zones_io import save_zones, load_zones

ZONES_PATH = "restricted_zones.json"
VIDEO_PATH = "assets/test.mp4"
SCREENSHOT_PATH = "assets/zone_screenshot.png"

current_polygon = []
polygons = load_zones(ZONES_PATH) or []

def mouse_callback(event, x, y, flags, param):
    global current_polygon
    if event == cv2.EVENT_LBUTTONDOWN:
        current_polygon.append([int(x), int(y)])

def draw_all(frame):

    for zone in polygons:
        pts = np.array(zone.get("points", []), np.int32)
        if pts.size:
            cv2.polylines(frame, [pts], True, (0, 255, 255), 2)
            cx = int(pts[:,0].mean())
            cy = int(pts[:,1].mean())
            cv2.putText(frame, zone.get("name", zone.get("id","")), (cx, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)

    if current_polygon:
        pts = np.array(current_polygon, np.int32)
        cv2.polylines(frame, [pts], False, (0, 0, 255), 2)
        for p in current_polygon:
            cv2.circle(frame, tuple(p), 4, (0,0,255), -1)

def make_zone_from_current():
    if not current_polygon:
        return None
    zone = {
        "id": f"zone_{int(time.time())}",
        "name": f"zone_{len(polygons)+1}",
        "points": current_polygon.copy()
    }
    return zone

def main():
    global current_polygon, polygons
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print("Не удалось открыть видео:", VIDEO_PATH)
        return


    ret, frame = cap.read()
    cap.release()
    if not ret:
        print("Не удалось прочитать кадр.")
        return

    win = "Zone Editor - click to add points, s=save zone, n=new zone, c=clear current, p=save screenshot, q=quit"
    cv2.namedWindow(win)
    cv2.setMouseCallback(win, mouse_callback)

    while True:
        display = frame.copy()
        draw_all(display)
        cv2.imshow(win, display)
        key = cv2.waitKey(10) & 0xFF

        if key == ord('q'):
            break
        elif key == ord('s'): 
            z = make_zone_from_current()
            if z:
                polygons.append(z)
                save_zones(ZONES_PATH, polygons)
                current_polygon = []
                print("Zone saved:", z["id"])
            else:
                print("Нет точек для сохранения.")
        elif key == ord('n'): 
            if current_polygon:
                print("Зона ещё не сохранена, нажмите s чтобы сохранить или c чтобы очистить.")
            else:
                print("Новая зона — начинайте клики.")
        elif key == ord('c'):
            current_polygon = []
            print("Текущая разметка очищена.")
        elif key == ord('p'):
            cv2.imwrite(SCREENSHOT_PATH, display)
            print("Скрин сохранён в", SCREENSHOT_PATH)

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
