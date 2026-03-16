import cv2
import face_recognition
import numpy as np
from datetime import datetime
from db import students_col, attendance_col

TOLERANCE = 0.5


def load_encodings():
    docs = list(students_col().find({}, {"_id": 0, "name": 1, "student_id": 1, "encodings": 1}))
    if not docs:
        print("[ERROR] No registered students found. Register students first.")
        return None, None, 0
    final_encodings, final_names = [], []
    for doc in docs:
        encs = [np.array(e) for e in doc["encodings"]]
        avg_enc = np.mean(encs, axis=0)
        final_encodings.append(avg_enc)
        final_names.append(f"{doc['name']}_{doc['student_id']}")
    return final_encodings, final_names, len(final_names)


def get_marked_today():
    today = datetime.now().strftime("%Y-%m-%d")
    records = attendance_col().find({"date": today}, {"_id": 0, "name": 1, "student_id": 1})
    return set(f"{r['name']}_{r['student_id']}" for r in records)


def mark_attendance_bulk(detected, marked_today):
    now = datetime.now()
    new_records = []
    for name, student_id in detected:
        name_id = f"{name}_{student_id}"
        if name_id not in marked_today:
            new_records.append({
                "name": name,
                "student_id": student_id,
                "time": now.strftime("%H:%M:%S"),
                "date": now.strftime("%Y-%m-%d"),
                "timestamp": now
            })
            marked_today.add(name_id)
            print(f"[MARKED] {name} (ID: {student_id}) at {now.strftime('%H:%M:%S')}")
    if new_records:
        attendance_col().insert_many(new_records)
    return marked_today


def draw_panel(frame, marked_names, total):
    h, w = frame.shape[:2]
    panel_w = 220
    overlay = frame.copy()
    cv2.rectangle(overlay, (w - panel_w, 0), (w, h), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
    cv2.putText(frame, "Present Today", (w - panel_w + 10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 200), 2)
    cv2.putText(frame, f"{len(marked_names)} / {total}",
                (w - panel_w + 10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
    cv2.line(frame, (w - panel_w + 5, 70), (w - 5, 70), (80, 80, 80), 1)
    for i, n in enumerate(list(marked_names)[-10:]):
        display_name = n.rsplit("_", 1)[0]
        cv2.putText(frame, f"+ {display_name}", (w - panel_w + 10, 95 + i * 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, (100, 255, 100), 1)


def run_attendance():
    cam = None
    try:
        final_encodings, final_names, total = load_encodings()
        if final_encodings is None:
            return

        marked_today = get_marked_today()
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            print("[ERROR] Cannot open webcam.")
            return

        print(f"[INFO] {total} students registered. {len(marked_today)} already marked today.")
        print("[INFO] Press Q to stop.\n")

        frame_count = 0
        boxes, encodings = [], []

        while True:
            ret, frame = cam.read()
            if not ret:
                break

            if frame_count % 4 == 0:
                small = cv2.resize(frame, (0, 0), fx=0.4, fy=0.4)
                rgb = np.ascontiguousarray(cv2.cvtColor(small, cv2.COLOR_BGR2RGB), dtype=np.uint8)
                boxes = face_recognition.face_locations(rgb, model="hog")
                encodings = face_recognition.face_encodings(rgb, boxes)
            frame_count += 1

            scale = int(1 / 0.4)
            detected_this_frame = []
            face_labels = []

            for encoding, box in zip(encodings, boxes):
                distances = face_recognition.face_distance(final_encodings, encoding)
                best = int(np.argmin(distances))
                name_id = final_names[best] if distances[best] < TOLERANCE else "Unknown"
                if name_id != "Unknown":
                    parts = name_id.rsplit("_", 1)
                    name, student_id = parts[0], parts[1] if len(parts) == 2 else "N/A"
                    detected_this_frame.append((name, student_id))
                    face_labels.append((box, True, f"{name} ({student_id})"))
                else:
                    face_labels.append((box, False, "Unknown"))

            marked_today = mark_attendance_bulk(detected_this_frame, marked_today)

            for box, known, label in face_labels:
                top, right, bottom, left = [v * scale for v in box]
                color = (0, 255, 0) if known else (0, 0, 255)
                if known:
                    label += " [Present]"
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.rectangle(frame, (left, bottom - 28), (right, bottom), color, -1)
                cv2.putText(frame, label, (left + 4, bottom - 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.52, (0, 0, 0), 1)

            cv2.rectangle(frame, (0, 0), (frame.shape[1] - 220, 40), (30, 30, 30), -1)
            cv2.putText(frame, f"Attendance  |  {datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}  |  Q=quit",
                        (10, 27), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (200, 200, 200), 1)

            draw_panel(frame, marked_today, total)
            cv2.imshow("Attendance System", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        print(f"\n[DONE] {len(marked_today)} / {total} students marked present today.")

    except Exception as e:
        print(f"[ERROR] Attendance failed: {e}")
    finally:
        if cam is not None:
            cam.release()
        cv2.destroyAllWindows()
