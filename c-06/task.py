# bad_repository.py
# ============================================================
# ÜBUNG: Repository Pattern (Dauer: ca. 30 Minuten)
#
# ZIELE:
# - Verstehe, warum direkte Datei-/DB-Zugriffe in der Domäne problematisch sind.
# - Entkopple die Geschäftslogik von der Persistenzschicht.
# - Verwende ein Repository-Interface, das leicht mockbar ist (z. B. für Tests).
#
# AUFGABEN:
# 1) Analysiere, warum die Klasse "PatientService" schlecht wartbar/testbar ist.
# 2) Extrahiere die Datei-Zugriffe in ein Repository.
# 3) Definiere ein Repository-Interface (z. B. `PatientRepository`).
# 4) Implementiere eine konkrete Klasse (z. B. `CsvPatientRepository`).
# 5) Refaktoriere den Service so, dass er nur das Interface nutzt (Dependency Injection).
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
    """Kombiniert Geschäftslogik + Persistenz → kein Repository Pattern."""
    def __init__(self, file_path=DATA_FILE):
        self.file_path = file_path

    def add_patient(self, pid, name, birthdate_str, risk):
        y, m, d = map(int, birthdate_str.split("-"))
        patient = Patient(pid, name, date(y, m, d), risk)

        # Persistenz direkt in der Domäne
        with open(self.file_path, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([patient.pid, patient.name, patient.birthdate.isoformat(), patient.risk])

        return f"Patient {patient.name} gespeichert."

    def list_patients(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                rows = list(csv.reader(f))
        except FileNotFoundError:
            return []
        return [Patient(r[0], r[1], date.fromisoformat(r[2]), r[3]) for r in rows]

if __name__ == "__main__":
    svc = PatientService()
    print(svc.add_patient("p001", "Max Mustermann", "1980-01-12", "high"))
    for p in svc.list_patients():
        print(p)
