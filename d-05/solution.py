# good_observer_mentcare.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Protocol, Callable

# -------- Ereignisdefinition (Domain Event) --------
@dataclass(frozen=True)
class RiskChangedEvent:
    pid: str
    name: str
    old: str
    new: str

# -------- Observer-Vertrag --------
class RiskObserver(Protocol):
    def update(self, event: RiskChangedEvent) -> None: ...

# -------- Subject (Publisher) --------
class PatientRiskSubject:
    """Verwaltet Observer und benachrichtigt sie über RiskChangedEvent."""
    def __init__(self) -> None:
        self._observers: List[RiskObserver] = []

    def subscribe(self, obs: RiskObserver) -> None:
        self._observers.append(obs)

    def unsubscribe(self, obs: RiskObserver) -> None:
        self._observers = [o for o in self._observers if o is not obs]

    def notify(self, event: RiskChangedEvent) -> None:
        for o in list(self._observers):
            o.update(event)

# -------- Konkrete Observer --------
class AlertObserver:
    def update(self, event: RiskChangedEvent) -> None:
        print(f"[ALERT] {event.pid} {event.name}: {event.old} -> {event.new}")

class AuditObserver:
    def update(self, event: RiskChangedEvent) -> None:
        print(f"[AUDIT] Risk change for {event.pid}: {event.old} -> {event.new}")

class DashboardObserver:
    def update(self, event: RiskChangedEvent) -> None:
        print(f"[DASHBOARD] Update badge for {event.pid}: {event.new}")

# -------- Domäne (kennt nur das Subject, nicht die Observer) --------
@dataclass
class Patient:
    pid: str
    name: str
    risk: str = "low"

class PatientService:
    """Domänenservice: löst bei Riskoänderungen ein Event am Subject aus."""
    def __init__(self, risk_subject: PatientRiskSubject) -> None:
        self._risk_subject = risk_subject

    def set_risk(self, p: Patient, new_risk: str) -> None:
        old = p.risk
        if old == new_risk:
            return
        p.risk = new_risk
        self._risk_subject.notify(RiskChangedEvent(p.pid, p.name, old, new_risk))

# -------- Demo / Composition Root --------
if __name__ == "__main__":
    subject = PatientRiskSubject()
    subject.subscribe(AlertObserver())
    subject.subscribe(AuditObserver())
    subject.subscribe(DashboardObserver())

    svc = PatientService(subject)

    p1 = Patient("p001", "Max Mustermann", "low")
    svc.set_risk(p1, "high")    # löst Benachrichtigungen aus
    subject.unsubscribe(AuditObserver())  # Hinweis: nur gleiche Instanz würde entfernt
