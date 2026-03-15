import cv2
import face_recognition
import numpy as np
from datetime import datetime
from db import students_col

SAMPLES_NEEDED = 5


def load_all_encodings():
    docs = list(students_col().find({}, {"_id": 0, "name": 1, "student_id": 1, "encodings": 1}))
    names, encodings = [], []
    for doc in docs:
        for enc in doc["encodings"]:
            names.append(f"{doc['name']}_{doc['student_id']}")
            encodings.append(np.array(enc))
    return names, encodings


def is_duplicate(new_encoding, tolerance=0.5):
    _, known_encodings = load_all_encodings()
    if not known_encodings:
        return False, None
    distances = face_recognition.face_distance(known_encodings, new_encoding)
    best = int(np.argmin(distances))
    if distances[best] < tolerance:
        _, known_names = load_all_encodings()
        return True, known_names[best].rsplit("_", 1)[0]
    return False, None


def save_student(name, student_id, encodings):
    col = students_col()
    existing = col.find_one({"student_id": student_id})
    enc_list = [e.tolist() for e in encodings]
    if existing:
        col.update_one({"student_id": student_id}, {"$set": {"encodings": enc_list}})
        print(f"[UPDATED] {name} (ID: {student_id}) updated in database.")
    else:
        col.insert_one({
            "name": name,
            "student_id": student_id,
            "encodings": enc_list,
            "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        print(f"[SAVED] {name} (ID: {student_id}) saved to MongoDB.")


def draw_progress_bar(frame, progress, total, y=95):
    bar_x, bar_w, bar_h = 10, 300, 20
    cv2.rectangle(frame, (bar_x, y), (bar_x + bar_w, y + bar_h), (50, 50, 50), -1)
    filled = int(bar_w * progress / total)
    cv2.rectangle(frame, (bar_x, y), (bar_x + filled, y + bar_h), (0, 255, 100), -1)
    cv2.putText(frame, f"{progress}/{total} samples", (bar_x + bar_w + 10, y + 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)


def capture_and_register(name, student_id):
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("[ERROR] Cannot open webcam.")
        return

    captured_encodings = []
    cooldown = 0
    print(f"[INFO] Look at the camera. Capturing {SAMPLES_NEEDED} face samples automatically...")

    while True:
        ret, frame = cam.read()
        if not ret:
            break

        display = frame.copy()
        rgb = np.ascontiguousarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), dtype=np.uint8)
        boxes = face_recognition.face_locations(rgb, model="hog")
        encodings = face_recognition.face_encodings(rgb, boxes)

        status_msg = "Position your face in the frame"
        status_color = (0, 200, 255)

        if boxes:
            top, right, bottom, left = boxes[0]
            cv2.rectangle(display, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(display, "Face Detected", (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            if cooldown == 0 and encodings:
                enc = encodings[0]
                is_dup, dup_name = is_duplicate(enc)
                if is_dup and len(captured_encodings) == 0:
                    status_msg = f"Already registered as: {dup_name}"
                    status_color = (0, 0, 255)
                else:
                    captured_encodings.append(enc)
                    cooldown = 15
                    status_msg = f"Sample {len(captured_encodings)} captured!"
                    status_color = (0, 255, 0)
        else:
            cv2.putText(display, "No face detected", (10, 110),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        if cooldown > 0:
            cooldown -= 1

        cv2.rectangle(display, (0, 0), (frame.shape[1], 55), (30, 30, 30), -1)
        cv2.putText(display, f"Registering: {name}  |  ID: {student_id}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
        cv2.putText(display, status_msg, (10, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
        draw_progress_bar(display, len(captured_encodings), SAMPLES_NEEDED)
        cv2.putText(display, "Press Q to cancel", (frame.shape[1] - 200, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
        cv2.imshow("Register Student", display)

        if len(captured_encodings) >= SAMPLES_NEEDED:
            save_student(name, student_id, captured_encodings)
            success = display.copy()
            cv2.rectangle(success, (0, 0), (success.shape[1], success.shape[0]), (0, 180, 0), 10)
            cv2.putText(success, "Registration Complete!", (50, success.shape[0] // 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)
            cv2.imshow("Register Student", success)
            cv2.waitKey(2000)
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[INFO] Registration cancelled.")
            break

    cam.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    print("=== Student Face Registration ===")
    while True:
        name = input("\nEnter student name (or 'q' to quit): ").strip()
        if name.lower() == 'q':
            break
        student_id = input("Enter student ID: ").strip()
        if name and student_id:
            capture_and_register(name, student_id)
        else:
            print("[WARN] Name and ID cannot be empty.")
