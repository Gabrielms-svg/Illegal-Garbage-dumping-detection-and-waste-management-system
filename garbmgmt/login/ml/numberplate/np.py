from ultralytics import YOLO
import cv2
import easyocr
import os
import csv
import time
from datetime import datetime
import re

# ------------------ HELPER ------------------
def normalize_plate(text):
    text = text.upper()
    text = re.sub(r'[^A-Z0-9]', '', text)
    replacements = {'O':'0','I':'1','Z':'2','S':'5','B':'8'}
    return ''.join(replacements.get(c,c) for c in text)

# ------------------ MODELS ------------------
plate_model = YOLO("license_plate_detector.pt")
reader = easyocr.Reader(['en'], gpu=True)

# ------------------ VIDEO ------------------
cap = cv2.VideoCapture("1.mp4")
if not cap.isOpened():
    print("ERROR: Video not opened")
    exit()

# ------------------ LOGGING ------------------
os.makedirs("plate_evidence", exist_ok=True)
CSV_FILE = "plate_log.csv"

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as f:
        csv.writer(f).writerow(["event_id","time","plate_text","confidence","image"])

# ------------------ STATE ------------------
event_id = 0
seen_plates = {}  # store plate -> last detection time
COOLDOWN = 5       # seconds to ignore same plate

# ------------------ MAIN LOOP ------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    plates = plate_model(frame, conf=0.4, verbose=False)

    for box in plates[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        crop = frame[y1:y2, x1:x2]

        ocr_result = reader.readtext(crop)
        if not ocr_result:
            continue

        raw_text = ocr_result[0][1]
        conf = ocr_result[0][2]
        if conf < 0.4:
            continue

        norm_text = normalize_plate(raw_text)
        if len(norm_text) < 6:
            continue

        # check cooldown to prevent duplicates
        now = time.time()
        last_seen = seen_plates.get(norm_text, 0)
        if now - last_seen < COOLDOWN:
            continue

        seen_plates[norm_text] = now
        event_id += 1

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        img_path = f"plate_evidence/event_{event_id}_{norm_text}.jpg"
        cv2.imwrite(img_path, crop)

        with open(CSV_FILE, "a", newline="") as f:
            csv.writer(f).writerow([event_id, ts, norm_text, round(conf,2), img_path])

        print(f"[LOGGED] Plate {norm_text}")

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
        cv2.putText(frame, norm_text, (x1, y1-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

    cv2.imshow("Number Plate Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
