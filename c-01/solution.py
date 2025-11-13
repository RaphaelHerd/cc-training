# good_soc.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Iterable, Protocol, Dict, Any
from pathlib import Path
import csv
import json

# ------------- domain.py (rein) -----------------
@dataclass(frozen=True)
class Patient:
    pid: str
    name: str
    birthdate: date
    risk: str  # "low" | "medium" | "high"

def is_high_risk(p: Patient) -> bool:
    return p.risk.lower() == "high"

def stats_for(patients: Iterable[Patient]) -> Dict[str, int]:
    pts = list(patients)
    return {
        "count": len(pts),
        "high": sum(is_high_risk(p) for p in pts),
        "medium": sum(p.risk == "medium" for p in pts),
        "low": sum(p.risk == "low" for p in pts),
    }

# ------------- ports.py -------------------------
class PatientRepository(Protocol):
    def save(self, p: Patient) -> None: ...
    def all(self) -> Iterable[Patient]: ...

class AlertSink(Protocol):
    def notify(self, subject: str, message: str) -> None: ...

class ReportWriter(Protocol):
    def write(self, stats: Dict[str, Any]) -> None: ...

# ------------- infra_csv.py ---------------------
class CsvPatientRepository(PatientRepository):
    def __init__(self, path: Path) -> None:
        self.path = path

    def save(self, p: Patient) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([p.pid, p.name, p.birthdate.isoformat(), p.risk])

    def all(self) -> Iterable[Patient]:
        if not self.path.exists(): 
            return []
        with self.path.open("r", encoding="utf-8") as f:
            for row in csv.reader(f):
                yield Patient(row[0], row[1], date.fromisoformat(row[2]), row[3])

class EmailAlert(AlertSink):
    def __init__(self, to: str) -> None:
        self.to = to
    def notify(self, subject: str, message: str) -> None:
        print(f"[EMAIL to={self.to}] {subject} :: {message}")

class CsvReportWriter(ReportWriter):
    def __init__(self, path: Path) -> None:
        self.path = path
    def write(self, stats: Dict[str, Any]) -> None:
        with self.path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["count", "high", "medium", "low"])
            w.writerow([stats["count"], stats["high"], stats["medium"], stats["low"]])

class JsonReportWriter(ReportWriter):
    def __init__(self, path: Path) -> None:
        self.path = path
    def write(self, stats: Dict[str, Any]) -> None:
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)

# ------------- usecases.py ----------------------
class PatientUseCases:
    def __init__(self, repo: PatientRepository, alerts: AlertSink, reporter: ReportWriter) -> None:
        self.repo = repo
        self.alerts = alerts
        self.reporter = reporter

    def register_patient(self, pid: str, name: str, birthdate_str: str, risk: str) -> None:
        y, m, d = map(int, birthdate_str.split("-"))
        p = Patient(pid, name, date(y, m, d), risk)
        if is_high_risk(p):
            self.alerts.notify(f"High Risk: {p.pid}", f"Patient {p.name} is HIGH risk")
        self.repo.save(p)

    def build_and_write_report(self) -> Dict[str, int]:
        s = stats_for(self.repo.all())          # reine Domänenfunktion
        self.reporter.write(s)                  # I/O im Adapter
        return s

# ------------- cli.py (nur UI + Composition Root) ---------------
def main():
    repo = CsvPatientRepository(Path("data/patients.csv"))
    alerts = EmailAlert("alerts@hospital.local")
    # Reporter ist austauschbar (CSV/JSON), ohne Use-Case zu ändern:
    # reporter = JsonReportWriter(Path("out/report.json"))
    reporter = CsvReportWriter(Path("out/report.csv"))

    app = PatientUseCases(repo, alerts, reporter)

    while True:
        print("\n1) Patient anlegen\n2) Monatsreport\n3) Ende")
        c = input("> ").strip()
        if c == "1":
            pid = input("ID: ")
            name = input("Name: ")
            bd = input("Geburtsdatum (YYYY-MM-DD): ")
            risk = input("Risiko (low/medium/high): ")
            try:
                app.register_patient(pid, name, bd, risk)
                print("OK gespeichert.")
            except Exception as e:
                print("Fehler:", e)
        elif c == "2":
            stats = app.build_and_write_report()
            print("Report geschrieben:", stats)
        elif c == "3":
            break
        else:
            print("Ungültig")

if __name__ == "__main__":
    main()
