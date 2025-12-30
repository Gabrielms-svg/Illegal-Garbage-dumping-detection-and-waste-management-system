from ultralytics import YOLO
import cv2

# Load models
waste_model = YOLO("best.pt")        # Your waste model
human_model = YOLO("yolov8n.pt")     # Person + vehicle model

cap = cv2.VideoCapture("10.mp4")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Run detection
    waste_results = waste_model(frame, conf=0.3, verbose=False)
    human_results = human_model(frame, conf=0.4, verbose=False)

    # ---- DRAW WASTE DETECTIONS (GREEN) ----
    for box in waste_results[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        label = waste_model.names[cls_id]

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            frame,
            f"{label} {conf:.2f}",
            (x1, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2
        )

    # ---- DRAW PERSON & VEHICLE (BLUE) ----
    for box in human_results[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        label = human_model.names[cls_id]

        # Only draw people & vehicles
        if label in ["person", "car", "truck", "motorcycle", "bus"]:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(
                frame,
                f"{label} {conf:.2f}",
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 0, 0),
                2
            )

    cv2.imshow("Illegal Dumping Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
