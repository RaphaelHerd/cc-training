# bad_cqrs.py
# ============================================================
# ÜBUNG: CQRS (Command Query Responsibility Segregation)
#
# ZIELE:
# - Verstehe, warum Befehle (write) und Abfragen (read) getrennt werden sollten.
# - Wende CQRS an, um Verantwortlichkeiten zu entkoppeln.
# - Mache die Logik testbarer und klarer strukturiert.
#
# AUFGABEN:
# 1) Analysiere: Welche Funktionen vermischen Commands und Queries?
# 2) Trenne:
#    - CommandHandler: "Patient anlegen" (write)
#    - QueryHandler: "Statistik abrufen" (read)
# 3) Verwende getrennte Schnittstellen oder Klassen für Command- und Query-Pfade.
# 4) Optional: Implementiere Tests für jeden Pfad separat.
# ============================================================

import csv
from dataclasses import dataclass
from datetime import date

DATA_FILE = "data/patients.csv"

@dataclass
class Patient:
    pid: str
    name: str
    birthdate: date
    risk: str

class PatientService:
    """Macht alles auf einmal: Commands UND Queries -> kein CQRS"""
    def __init__(self, data_file=DATA_FILE):
        self.data_file = data_file

    def add_patient_and_report(self, pid, name, birthdate_str, risk):
        y, m, d = map(int, birthdate_str.split("-"))
        patient = Patient(pid, name, date(y, m, d), risk)

        # schreibt sofort in Datei
        with open(self.data_file, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([patient.pid, patient.name, patient.birthdate.isoformat(), patient.risk])

        # UND macht gleich Statistik (vermischt read/write)
        with open(self.data_file, "r", encoding="utf-8") as f:
            rows = list(csv.reader(f))
        total = len(rows)
        high = sum(1 for r in rows if r[3] == "high")

        # gibt gemischtes Ergebnis zurück
        return {"added": patient.name, "total": total, "high": high}

if __name__ == "__main__":
    svc = PatientService()
    result = svc.add_patient_and_report("p004", "Sabine Schulz", "1985-02-14", "high")
    print(result)
