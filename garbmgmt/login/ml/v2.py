from ultralytics import YOLO
import cv2
import time
import csv
import os
from datetime import datetime

# ------------------ HELPERS ------------------

def is_inside(waste_box, vehicle_box):
    wx1, wy1, wx2, wy2 = waste_box
    vx1, vy1, vx2, vy2 = vehicle_box

    return not (wx2 < vx1 or wx1 > vx2 or wy2 < vy1 or wy1 > vy2)

# ------------------ LOAD MODELS ------------------

waste_model = YOLO("best.pt")
vehicle_model = YOLO("yolov8n.pt")

cap = cv2.VideoCapture("10.mp4")

# ------------------ CONFIG ------------------

CSV_FILE = "dumping_events.csv"
EVIDENCE_DIR = "evidence"

WASTE_PERSIST_TIME = 2.0
PERSON_LEAVE_TIME = 1.0
GROUND_RATIO = 0.55   # bottom half of frame

os.makedirs(EVIDENCE_DIR, exist_ok=True)

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as f:
        csv.writer(f).writerow([
            "event_id", "timestamp", "video",
            "waste_type", "vehicle",
            "confidence", "image_path"
        ])

# ------------------ STATE ------------------

person_last_seen = 0
waste_first_seen = 0
event_logged = False
event_id = 0
person_seen_once = False

# ------------------ LOOP ------------------

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    now = time.time()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    H = frame.shape[0]

    vehicle_boxes = []
    waste_boxes = []

    waste_label = ""
    waste_conf = 0
    actor_label = ""

    # ------------------ VEHICLE DETECTION ------------------

    veh_results = vehicle_model(frame, conf=0.4, verbose=False)

    for box in veh_results[0].boxes:
        label = vehicle_model.names[int(box.cls[0])]
        if label in ["car", "truck", "bus", "motorcycle"]:
            person_seen_once = True
            person_last_seen = now
            actor_label = label

            x1,y1,x2,y2 = map(int, box.xyxy[0])
            vehicle_boxes.append((x1,y1,x2,y2))

    # ------------------ WASTE DETECTION ------------------

    waste_results = waste_model(frame, conf=0.25, verbose=False)

    for box in waste_results[0].boxes:
        x1,y1,x2,y2 = map(int, box.xyxy[0])

        # must be on ground
        if y2 < H * GROUND_RATIO:
            continue

        # must NOT overlap vehicle
        overlap = False
        for vb in vehicle_boxes:
            if is_inside((x1,y1,x2,y2), vb):
                overlap = True
                break

        if overlap:
            continue

        waste_boxes.append((x1,y1,x2,y2))
        waste_label = waste_model.names[int(box.cls[0])]
        waste_conf = float(box.conf[0])

        if waste_first_seen == 0:
            waste_first_seen = now

    # ------------------ DUMPING CONFIRM ------------------

    dumping_confirmed = False

    if person_seen_once and waste_boxes:
        if (now - person_last_seen) > PERSON_LEAVE_TIME:
            if (now - waste_first_seen) >= WASTE_PERSIST_TIME:
                dumping_confirmed = True

    # ------------------ SAVE EXACT MOMENT ------------------

    if dumping_confirmed and not event_logged:
        event_id += 1
        event_logged = True

        event_folder = os.path.join(EVIDENCE_DIR, f"event_{event_id}")
        os.makedirs(event_folder, exist_ok=True)

        img_path = os.path.join(event_folder, "dumping_frame.jpg")
        cv2.imwrite(img_path, frame)

        with open(CSV_FILE, "a", newline="") as f:
            csv.writer(f).writerow([
                event_id, timestamp, "10.mp4",
                waste_label, actor_label,
                round(waste_conf,2), img_path
            ])

        print(f"[CONFIRMED] Illegal dumping {event_id}")

    # ------------------ RESET ------------------

    if not waste_boxes and (now - person_last_seen) > 5:
        waste_first_seen = 0
        event_logged = False

    cv2.imshow("Dumping Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
