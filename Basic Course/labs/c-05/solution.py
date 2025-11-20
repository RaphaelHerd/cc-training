# good_cqrs.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Iterable, Dict, Protocol, Any
import csv
from pathlib import Path

# ---------------- Domain ----------------
@dataclass(frozen=True)
class Patient:
    pid: str
    name: str
    birthdate: date
    risk: str

# ---------------- Ports ----------------
class PatientWriteRepository(Protocol):
    def save(self, p: Patient) -> None: ...

class PatientReadRepository(Protocol):
    def all(self) -> Iterable[Patient]: ...

# ---------------- Adapters ----------------
class CsvPatientWriteRepo(PatientWriteRepository):
    def __init__(self, path: Path):
        self.path = path
    def save(self, p: Patient) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([p.pid, p.name, p.birthdate.isoformat(), p.risk])

class CsvPatientReadRepo(PatientReadRepository):
    def __init__(self, path: Path):
        self.path = path
    def all(self) -> Iterable[Patient]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as f:
            for r in csv.reader(f):
                yield Patient(r[0], r[1], date.fromisoformat(r[2]), r[3])

# ---------------- Command Handler ----------------
class RegisterPatientCommand:
    def __init__(self, pid: str, name: str, birthdate: str, risk: str):
        self.pid = pid
        self.name = name
        self.birthdate = birthdate
        self.risk = risk

class RegisterPatientHandler:
    def __init__(self, write_repo: PatientWriteRepository):
        self.write_repo = write_repo

    def handle(self, cmd: RegisterPatientCommand) -> Patient:
        y, m, d = map(int, cmd.birthdate.split("-"))
        p = Patient(cmd.pid, cmd.name, date(y, m, d), cmd.risk)
        self.write_repo.save(p)
        return p

# ---------------- Query Handler ----------------
class PatientStatsQuery:
    pass  # hier wäre Platz für Filterkriterien etc.

class PatientStatsHandler:
    def __init__(self, read_repo: PatientReadRepository):
        self.read_repo = read_repo

    def handle(self, _: PatientStatsQuery) -> Dict[str, Any]:
        pts = list(self.read_repo.all())
        return {
            "total": len(pts),
            "high": sum(p.risk == "high" for p in pts),
            "medium": sum(p.risk == "medium" for p in pts),
            "low": sum(p.risk == "low" for p in pts),
        }

# ---------------- Composition Root ----------------
def main():
    path = Path("data/patients.csv")
    write_repo = CsvPatientWriteRepo(path)
    read_repo = CsvPatientReadRepo(path)

    # Commands (Write)
    cmd = RegisterPatientCommand("p004", "Sabine Schulz", "1985-02-14", "high")
    RegisterPatientHandler(write_repo).handle(cmd)

    # Queries (Read)
    stats = PatientStatsHandler(read_repo).handle(PatientStatsQuery())
    print("Aktuelle Statistik:", stats)

if __name__ == "__main__":
    main()
