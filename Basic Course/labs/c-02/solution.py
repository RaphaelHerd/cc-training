# good_mentcare.py  (Refaktoriere nach SOLID)
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Protocol, Iterable, runtime_checkable, Dict, Any
import csv
import json
from pathlib import Path

# --- SRP: klare Domäne -----------------------------------------

@dataclass(frozen=True)
class Patient:
    pid: str
    name: str
    birthdate: date
    risk: str  # "low" | "medium" | "high"

# Reine Geschäftsregel (testbar, kein IO)
def is_high_risk(p: Patient) -> bool:
    return p.risk.lower() == "high"

# --- ISP & DIP: kleine, fokussierte Ports ----------------------

@runtime_checkable
class PatientRepository(Protocol):
    def save(self, p: Patient) -> None: ...
    def get_all(self) -> Iterable[Patient]: ...

@runtime_checkable
class AlertSink(Protocol):
    def notify(self, subject: str, message: str) -> None: ...

@runtime_checkable
class ReportWriter(Protocol):
    def write(self, stats: Dict[str, Any]) -> None: ...

# --- Infra-Adapter (OCP: austauschbar über Ports) ---------------

class CsvPatientRepository(PatientRepository):
    def __init__(self, path: Path = Path("patients.csv")) -> None:
        self.path = path

    def save(self, p: Patient) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([p.pid, p.name, p.birthdate.isoformat(), p.risk])

    def get_all(self) -> Iterable[Patient]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as f:
            for row in csv.reader(f):
                yield Patient(pid=row[0], name=row[1], birthdate=date.fromisoformat(row[2]), risk=row[3])

class EmailAlert(AlertSink):
    # hier nur Demo -> reines Print steht im Adapter, nicht in der Domäne
    def __init__(self, to: str = "alerts@hospital.local") -> None:
        self.to = to
    def notify(self, subject: str, message: str) -> None:
        print(f"[EMAIL to={self.to}] {subject} :: {message}")

class CsvReportWriter(ReportWriter):
    def __init__(self, path: Path = Path("report.csv")) -> None:
        self.path = path
    def write(self, stats: Dict[str, Any]) -> None:
        with self.path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["count", "high", "medium", "low"])
            w.writerow([stats["count"], stats["high"], stats["medium"], stats["low"]])

class JsonReportWriter(ReportWriter):
    def __init__(self, path: Path = Path("report.json")) -> None:
        self.path = path
    def write(self, stats: Dict[str, Any]) -> None:
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)

# --- Application (DIP: hängt nur an Ports) ----------------------

class PatientApplication:
    def __init__(self, repo: PatientRepository, alert: AlertSink, reporter: ReportWriter) -> None:
        self.repo = repo
        self.alert = alert
        self.reporter = reporter

    # SRP: Anwendungsfall "Patient registrieren"
    def register_patient(self, p: Patient) -> None:
        if is_high_risk(p):
            self.alert.notify(subject=f"High Risk: {p.pid}", message=f"Patient {p.name} is HIGH risk")
        self.repo.save(p)

    # SRP: Anwendungsfall "Monatsbericht erzeugen"
    def produce_report(self) -> Dict[str, int]:
        patients = list(self.repo.get_all())  # erwartungstreu: Iterable[Patient]
        stats = {
            "count": len(patients),
            "high": sum(is_high_risk(p) for p in patients),
            "medium": sum(p.risk == "medium" for p in patients),
            "low": sum(p.risk == "low" for p in patients),
        }
        self.reporter.write(stats)
        return stats

# --- Komposition (Composition Root) -----------------------------

if __name__ == "__main__":
    repo = CsvPatientRepository(Path("data/patients.csv"))
    alert = EmailAlert("alerts@hospital.local")
    # OCP: wähle zur Laufzeit ein anderes Ausgabeformat, ohne den Service zu ändern
    reporter: ReportWriter = CsvReportWriter(Path("out/report.csv"))
    # reporter = JsonReportWriter(Path("out/report.json"))

    app = PatientApplication(repo, alert, reporter)

    app.register_patient(Patient("p001", "Max Mustermann", date(1980, 1, 12), "high"))
    app.register_patient(Patient("p002", "Erika Musterfrau", date(1972, 5, 3), "low"))
    app.produce_report()
