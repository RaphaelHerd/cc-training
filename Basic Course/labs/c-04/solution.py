# di_solution.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Protocol, Iterable, Dict, Any
import csv
from pathlib import Path

# ---------------- Domain ----------------
@dataclass(frozen=True)
class Patient:
    pid: str
    name: str
    birthdate: date
    risk: str  # "low"|"medium"|"high"

# ---------------- (Protokolle) ----------------
class PatientRepository(Protocol):
    def all(self) -> Iterable[Patient]: ...

class Mailer(Protocol):
    def send(self, to: str, subject: str, body: str) -> None: ...

# ---------------- Concrete Adapters ----------------
class CsvPatientRepository:
    def __init__(self, path: Path) -> None:
        self.path = path

    def all(self) -> Iterable[Patient]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as f:
            for row in csv.reader(f):
                yield Patient(row[0], row[1], date.fromisoformat(row[2]), row[3])

class SmtpMailer:
    def __init__(self, smtp_host: str = "localhost", from_addr: str = "noreply@local") -> None:
        import smtplib
        self._smtplib = smtplib
        self.smtp_host = smtp_host
        self.from_addr = from_addr

    def send(self, to: str, subject: str, body: str) -> None:
        # konkrete Implementierung bleibt am Rand; in Tests wird FakeMailer verwendet
        with self._smtplib.SMTP(self.smtp_host) as smtp:
            msg = f"Subject: {subject}\n\n{body}"
            smtp.sendmail(self.from_addr, to, msg)

# ---------------- Use-case / Service (hängt nur an Abstraktionen) ----------------
class ReportService:
    def __init__(self, repo: PatientRepository, mailer: Mailer, alert_to: str) -> None:
        self.repo = repo
        self.mailer = mailer
        self.alert_to = alert_to

    def create_report_and_alert(self) -> Dict[str, Any]:
        patients = list(self.repo.all())
        high = sum(1 for p in patients if p.risk == "high")
        if high > 0:
            self.mailer.send(self.alert_to, "High-risk patients", f"There are {high} high-risk patients.")
        return {"total": len(patients), "high": high}

# ---------------- Composition Root (nur hier werden konkrete Klassen verdrahtet) ----------------
def build_default_service() -> ReportService:
    repo = CsvPatientRepository(Path("data/patients.csv"))
    mailer = SmtpMailer("localhost", "noreply@local")
    return ReportService(repo, mailer, "alerts@hospital.local")

if __name__ == "__main__":
    svc = build_default_service()
    print(svc.create_report_and_alert())
