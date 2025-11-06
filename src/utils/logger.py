
import datetime

LOG_FILE = "events.log"

def log_event(event_type: str, details: str = ""):
    """
    event_type: "ALARM_ON" | "ALARM_OFF"
    details: дополнительная информация
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {event_type} {details}\n"
    with open(LOG_FILE, "a") as f:
        f.write(line)
    print(line.strip())
