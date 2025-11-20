# mod_good.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Iterable, Protocol, Dict, Any, List

# ------------------ DOMÄNE (rein, ohne I/O) ------------------

@dataclass(frozen=True)
class Patient:
    pid: str
    name: str
    birthdate: date
    risk: str  # "low"|"medium"|"high"

def is_high_risk(p: Patient) -> bool:
    return p.risk.lower() == "high"

def stats(patients: Iterable[Patient]) -> Dict[str, int]:
    ps = list(patients)
    return {
        "count": len(ps),
        "high": sum(is_high_risk(p) for p in ps),
        "medium": sum(p.risk == "medium" for p in ps),
        "low": sum(p.risk == "low" for p in ps),
    }

# ------------------ PORTS (kleine Protokolle) ----------------

class PatientRepository(Protocol):
    def save(self, p: Patient) -> None: ...
    def all(self) -> Iterable[Patient]: ...

class AlertSink(Protocol):
    def notify(self, subject: str, message: str) -> None: ...

class ReportWriter(Protocol):
    def write(self, stats: Dict[str, Any]) -> None: ...

# --------------- ADAPTER (einfach & in-memory) ----------------

class InMemoryPatientRepository(PatientRepository):
    def __init__(self, seed: Iterable[Patient] = ()) -> None:
        self._data: List[Patient] = list(seed)
    def save(self, p: Patient) -> None:
        self._data.append(p)
    def all(self) -> Iterable[Patient]:
        return list(self._data)

class PrintAlert(AlertSink):
    def __init__(self, to: str) -> None:
        self.to = to
    def notify(self, subject: str, message: str) -> None:
        print(f"[EMAIL to={self.to}] {subject} :: {message}")

class CsvLikeReportWriter(ReportWriter):
    """Schreibt nur auf die Konsole als 'csv-like' Zeile – schnell & IO-arm."""
    def write(self, s: Dict[str, Any]) -> None:
        print("count,high,medium,low")
        print(f"{s['count']},{s['high']},{s['medium']},{s['low']}")

# ------------------ USE-CASES (orchestrieren Ports) -----------

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

    def produce_report(self) -> Dict[str, int]:
        s = stats(self.repo.all())   # reine Domänenfunktion
        self.reporter.write(s)       # Ausgabe über Port/Adapter
        return s

# ------------------ CLI (Composition Root + UI) ----------------

def main():
    # Seed-Daten machen die Demo sofort nutzbar (kein Datei-Setup nötig)
    seed = [
        Patient("p001", "Max Mustermann", date(1980,1,12), "high"),
        Patient("p002", "Erika Musterfrau", date(1975,6,30), "medium"),
    ]
    repo = InMemoryPatientRepository(seed)
    alerts = PrintAlert("alerts@hospital.local")
    reporter = CsvLikeReportWriter()

    app = PatientUseCases(repo, alerts, reporter)

    while True:
        print("\n1) Patient anlegen  2) Report  3) Ende")
        c = input("> ").strip()
        if c == "1":
            pid = input("ID: ").strip()
            name = input("Name: ").strip()
            bd = input("Geburtsdatum (YYYY-MM-DD): ").strip()
            risk = input("Risiko (low/medium/high): ").strip()
            try:
                app.register_patient(pid, name, bd, risk)
                print("OK gespeichert.")
            except Exception as e:
                print("Fehler:", e)
        elif c == "2":
            s = app.produce_report()
            print("Report erstellt:", s)
        elif c == "3":
            break
        else:
            print("Ungültig")

if __name__ == "__main__":
    main()
