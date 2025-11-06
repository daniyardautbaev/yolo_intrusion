
import cv2
import json
import numpy as np

ZONES_PATH = "restricted_zones.json"
VIDEO_PATH = "assets/test.mp4"

points = []
zones = []

def mouse_callback(event, x, y, flags, param):
    global points
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))

def main():
    global points, zones
    cap = cv2.VideoCapture(VIDEO_PATH)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("Ошибка: не удалось загрузить видео.")
        return

    clone = frame.copy()
    cv2.namedWindow("Zone Annotation")
    cv2.setMouseCallback("Zone Annotation", mouse_callback)

    print("Инструкция:")
    print("1️⃣ Кликни ЛКМ по кадру, чтобы отметить точки зоны.")
    print("2️⃣ Когда закончил, нажми 's' чтобы сохранить.")
    print("3️⃣ Нажми 'r' чтобы сбросить текущую зону.")
    print("4️⃣ Нажми 'q' чтобы выйти без сохранения.\n")

    while True:
        temp_frame = clone.copy()
        if len(points) > 1:
            cv2.polylines(temp_frame, [np.array(points, np.int32)], True, (0, 255, 255), 2)
        elif len(points) == 1:
            cv2.circle(temp_frame, points[0], 3, (0, 0, 255), -1)

        cv2.imshow("Zone Annotation", temp_frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('r'):
            print("Сброс зоны")
            points = []

        elif key == ord('s') and len(points) > 2:
            zones.append({"points": points})
            with open(ZONES_PATH, "w") as f:
                json.dump(zones, f, indent=2)
            print(f"Зона сохранена в {ZONES_PATH}")
            points = []

        elif key == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
