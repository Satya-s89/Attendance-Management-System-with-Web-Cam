import sys
import os
from datetime import datetime
import pandas as pd
from db import students_col, attendance_col
from register import capture_and_register
from attendance import run_attendance

EXPORT_DIR = "data/exports"
os.makedirs(EXPORT_DIR, exist_ok=True)


def view_registered():
    docs = list(students_col().find({}, {"_id": 0, "name": 1, "student_id": 1, "registered_at": 1}))
    if not docs:
        print("[INFO] No students registered yet.")
        return
    print(f"\n{'─'*55}")
    print(f"  Registered Students ({len(docs)} total)")
    print(f"{'─'*55}")
    for doc in docs:
        print(f"  {doc['name']:<20} ID: {doc['student_id']:<15} Registered: {doc.get('registered_at', 'N/A')}")
    print(f"{'─'*55}\n")


def view_attendance_by_date():
    date_str = input("  Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")
    records = list(attendance_col().find({"date": date_str}, {"_id": 0, "name": 1, "student_id": 1, "time": 1}))
    total = students_col().count_documents({})
    print(f"\n{'─'*55}")
    print(f"  Attendance for {date_str}  ({len(records)}/{total} present)")
    print(f"{'─'*55}")
    if not records:
        print("  No attendance recorded for this date.")
    for r in records:
        print(f"  {r['name']:<20} ID: {r['student_id']:<15} Time: {r['time']}")
    print(f"{'─'*55}\n")


def export_attendance():
    print("\n  Export options:")
    print("  1. Export specific date")
    print("  2. Export all records")
    sub = input("  Select: ").strip()

    if sub == "1":
        date_str = input("  Enter date (YYYY-MM-DD): ").strip()
        query = {"date": date_str}
        filename = f"attendance_{date_str}"
    else:
        query = {}
        filename = f"attendance_all_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    records = list(attendance_col().find(query, {"_id": 0, "name": 1, "student_id": 1, "date": 1, "time": 1}))
    if not records:
        print("  [INFO] No records found.")
        return

    df = pd.DataFrame(records)[["name", "student_id", "date", "time"]]
    df.columns = ["Name", "Student ID", "Date", "Time"]

    print("\n  Format:")
    print("  1. CSV")
    print("  2. Excel")
    fmt = input("  Select: ").strip()

    if fmt == "2":
        path = os.path.join(EXPORT_DIR, f"{filename}.xlsx")
        df.to_excel(path, index=False)
    else:
        path = os.path.join(EXPORT_DIR, f"{filename}.csv")
        df.to_csv(path, index=False)

    print(f"  [EXPORTED] {len(records)} records → {path}\n")


def attendance_report():
    date_str = input("  Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    all_students = list(students_col().find({}, {"_id": 0, "name": 1, "student_id": 1}))
    present_records = attendance_col().find({"date": date_str}, {"_id": 0, "name": 1, "student_id": 1, "time": 1})
    present_ids = {r["student_id"]: r["time"] for r in present_records}

    print(f"\n{'─'*60}")
    print(f"  Attendance Report — {date_str}")
    print(f"  Present: {len(present_ids)} / {len(all_students)}")
    print(f"{'─'*60}")
    print(f"  {'Name':<20} {'Student ID':<18} {'Status':<10} {'Time'}")
    print(f"{'─'*60}")
    for s in sorted(all_students, key=lambda x: x["name"]):
        if s["student_id"] in present_ids:
            status = "PRESENT"
            time = present_ids[s["student_id"]]
            color = "\033[92m"
        else:
            status = "ABSENT"
            time = "—"
            color = "\033[91m"
        reset = "\033[0m"
        print(f"  {s['name']:<20} {s['student_id']:<18} {color}{status:<10}{reset} {time}")
    print(f"{'─'*60}\n")


def register_student():
    print("=== Student Face Registration ===")
    while True:
        name = input("\nEnter student name (or 'q' to go back): ").strip()
        if name.lower() == 'q':
            break
        student_id = input("Enter student ID: ").strip()
        if name and student_id:
            capture_and_register(name, student_id)
        else:
            print("[WARN] Name and ID cannot be empty.")


def main():
    while True:
        print("\n=== Attendance Management System ===")
        print("  1. Register new student (face scan)")
        print("  2. Take attendance (webcam)")
        print("  3. View registered students")
        print("  4. View attendance by date")
        print("  5. Export attendance (CSV / Excel)")
        print("  6. Attendance report (present/absent)")
        print("  7. Exit")
        choice = input("Select option: ").strip()

        if choice == "1":
            register_student()
        elif choice == "2":
            run_attendance()
        elif choice == "3":
            view_registered()
        elif choice == "4":
            view_attendance_by_date()
        elif choice == "5":
            export_attendance()
        elif choice == "6":
            attendance_report()
        elif choice == "7":
            print("Goodbye!")
            sys.exit(0)
        else:
            print("[WARN] Invalid option, choose 1-7.")


if __name__ == "__main__":
    main()
