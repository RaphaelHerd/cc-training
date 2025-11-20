# good_repository.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Iterable, Protocol
from pathlib import Path
import csv

# ------------------- Domäne -------------------
@dataclass(frozen=True)
class Patient:
    pid: str
    name: str
    birthdate: date
    risk: str

# ------------------- Repository Interface -------------------
class PatientRepository(Protocol):
    """Abstraktion für Persistenz: egal ob CSV, DB oder In-Memory."""
    def add(self, patient: Patient) -> None: ...
    def all(self) -> Iterable[Patient]: ...

# ------------------- Konkrete Implementierung -------------------
class CsvPatientRepository(PatientRepository):
    def __init__(self, path: Path):
        self.path = path

    def add(self, patient: Patient) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                patient.pid,
                patient.name,
                patient.birthdate.isoformat(),
                patient.risk
            ])

    def all(self) -> Iterable[Patient]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as f:
            for r in csv.reader(f):
                yield Patient(r[0], r[1], date.fromisoformat(r[2]), r[3])

# ------------------- Service (nutzt nur Interface) -------------------
class PatientService:
    """Nutzt Repository-Interface → leicht testbar & entkoppelt."""
    def __init__(self, repo: PatientRepository):
        self.repo = repo

    def register_patient(self, pid: str, name: str, birthdate_str: str, risk: str):
        y, m, d = map(int, birthdate_str.split("-"))
        p = Patient(pid, name, date(y, m, d), risk)
        self.repo.add(p)
        return f"Patient {p.name} gespeichert."

    def list_all(self):
        return list(self.repo.all())

# ------------------- Composition Root -------------------
def main():
    repo = CsvPatientRepository(Path("data/patients.csv"))
    service = PatientService(repo)

    print(service.register_patient("p002", "Erika Musterfrau", "1975-06-30", "medium"))
    for p in service.list_all():
        print(p)

if __name__ == "__main__":
    main()
