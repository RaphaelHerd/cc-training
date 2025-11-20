# bad_soc.py  (ABSICHTLICH SCHLECHT)
import csv
from dataclasses import dataclass
from datetime import date

PATIENTS_FILE = "patients.csv"  # globale Konfig

@dataclass
class Patient:
    pid: str
    name: str
    birthdate: date
    risk: str  # "low" | "medium" | "high"

def add_patient():
    # CLI, Validierung, Domäne, Persistenz & Logging vermischt
    pid = input("ID: ")
    name = input("Name: ")
    bd = input("Geburtsdatum (YYYY-MM-DD): ")
    risk = input("Risiko (low/medium/high): ")

    try:
        y, m, d = map(int, bd.split("-"))
        p = Patient(pid, name, date(y, m, d), risk)
    except Exception as e:
        print("Ungültiges Datum:", e)
        return

    if p.risk == "high":
        # Business-Regel + sofortige I/O
        print(f"[ALERT] Patient {p.pid} ({p.name}) ist HIGH RISK!")

    with open(PATIENTS_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([p.pid, p.name, p.birthdate.isoformat(), p.risk])
    print("Gespeichert.")

def monthly_report():
    # Persistenz, Domänenauswertung, Formatierung, Ausgabe vermischt
    try:
        rows = list(csv.reader(open(PATIENTS_FILE, "r", encoding="utf-8")))
    except FileNotFoundError:
        rows = []
    patients = []
    for r in rows:
        patients.append(Patient(r[0], r[1], date.fromisoformat(r[2]), r[3]))

    count = len(patients)
    high = sum(1 for p in patients if p.risk == "high")
    med = sum(1 for p in patients if p.risk == "medium")
    low = sum(1 for p in patients if p.risk == "low")

    fmt = input("Report-Format (text/csv): ").strip()
    if fmt == "csv":
        with open("report.csv", "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["count", "high", "medium", "low"])
            csv.writer(f).writerow([count, high, med, low])
        print("report.csv geschrieben")
    else:
        print("===== REPORT =====")
        print("count:", count, "high:", high, "medium:", med, "low:", low)

def main():
    while True:
        print("\n1) Patient anlegen\n2) Monatsreport\n3) Ende")
        c = input("> ").strip()
        if c == "1":
            add_patient()
        elif c == "2":
            monthly_report()
        elif c == "3":
            break
        else:
            print("Ungültig")

if __name__ == "__main__":
    main()
