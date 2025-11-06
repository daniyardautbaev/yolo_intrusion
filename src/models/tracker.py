from deep_sort_realtime.deepsort_tracker import DeepSort

class PersonTracker:
    
    def __init__(self, max_age=15, n_init=2, max_cosine_distance=0.3):
        self.tracker = DeepSort(max_age=max_age, n_init=n_init, max_cosine_distance=max_cosine_distance)

    def update(self, detections, frame):
        
        bboxes = [d['box'] for d in detections]
        confidences = [d['conf'] for d in detections]
        tracks = self.tracker.update_tracks(bboxes, confidences, frame=frame)

        results = []
        for track in tracks:
            if not track.is_confirmed():
                continue
            x1, y1, x2, y2 = track.to_ltrb()
            results.append({
                'id': track.track_id,
                'box': [x1, y1, x2, y2]
            })
        return results
