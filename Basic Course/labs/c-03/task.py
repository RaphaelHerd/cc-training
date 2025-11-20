# mod_bad.py
# ============================================================
# ÜBUNG: MODULARITÄT (30-Minuten-Aufgabe)
#
# ZIELE
# 1) Verantwortlichkeiten trennen (Domäne, Persistenz, Reporting/Alerts, CLI).
# 2) Abhängigkeiten explizit machen (keine Globals).
# 3) Reine Domänenfunktionen (ohne I/O) testbar machen.
#
# AUFGABEN
# A) Extrahiere die Domäne: "Patient" + reine Funktion "stats(patients)".
# B) Ersetze Datei-/Print-Logik durch getrennte Klassen/Interfaces.
# C) Baue einen kleinen "UseCase" (register_patient, produce_report),
#    der nur über entkoppelte Interfaces spricht.
# D) Verlege Konfiguration/Verkabelung in eine "Composition Root".
#    (Tipp: kleine in-memory Adapter reichen für diese Übung!)
# ============================================================

import csv
from dataclasses import dataclass
from datetime import date

PATIENTS_FILE = "data/patients.csv"   # globale Konfig (anti-modular)
ALERTS_TO = "alerts@hospital.local"   # weitere globale Konfig

@dataclass
class Patient:
    pid: str
    name: str
    birthdate: date
    risk: str  # "low"|"medium"|"high"

def add_patient_cli():
    # CLI + Domäne + Persistenz + Alerts vermischt
    pid = input("ID: ").strip()
    name = input("Name: ").strip()
    y, m, d = map(int, input("Geburtsdatum (YYYY-MM-DD): ").split("-"))
    risk = input("Risiko (low/medium/high): ").strip()
    p = Patient(pid, name, date(y, m, d), risk)

    # "Business-Regel" + I/O vermischt
    if p.risk.lower() == "high":
        print(f"[EMAIL to={ALERTS_TO}] High Risk: {p.pid} :: Patient {p.name} is HIGH risk")

    # Persistenz im UI
    with open(PATIENTS_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([p.pid, p.name, p.birthdate.isoformat(), p.risk])
    print("Gespeichert.")

def report_cli():
    # Persistenz + Domäne + Formatierung vermischt
    try:
        with open(PATIENTS_FILE, "r", encoding="utf-8") as f:
            rows = list(csv.reader(f))
    except FileNotFoundError:
        rows = []
    patients = [Patient(r[0], r[1], date.fromisoformat(r[2]), r[3]) for r in rows]

    # Ad-hoc Domänenlogik
    count = len(patients)
    high = sum(1 for p in patients if p.risk == "high")
    medium = sum(1 for p in patients if p.risk == "medium")
    low = sum(1 for p in patients if p.risk == "low")

    fmt = input("Report-Format (text/csv): ").strip()
    if fmt == "csv":
        with open("out/report.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["count", "high", "medium", "low"])
            w.writerow([count, high, medium, low])
        print("report.csv geschrieben")
    else:
        print(f"count={count} high={high} medium={medium} low={low}")

def main():
    while True:
        print("\n1) Patient anlegen\n2) Report erstellen\n3) Ende")
        c = input("> ").strip()
        if c == "1":
            add_patient_cli()
        elif c == "2":
            report_cli()
        elif c == "3":
            break
        else:
            print("Ungültig")

if __name__ == "__main__":
    main()
