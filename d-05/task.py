# Szenario:
#   Ändert sich der Risikostatus eines Patienten (low/high), sollen
#   mehrere Komponenten reagieren:
#     - Alerts (E-Mail/Push) versenden,
#     - ein Audit-Log schreiben,
#     - ein Dashboard aktualisieren.
#
# Problem:
#   Die aktuelle Implementierung koppelt die Domänenlogik direkt an
#   alle Empfänger. Jede neue Reaktion erfordert Änderungen an der
#   Kernlogik, Tests sind aufwendig.
#
# Aufgabe:
#   Refactorn Sie auf das Observer Pattern:
#     1) Definieren Sie einen Ereignistyp (z. B. RiskChangedEvent).
#     2) Definieren Sie ein Observer-Interface mit update(event).
#     3) Implementieren Sie ein Subject (z. B. PatientRiskSubject) mit
#        subscribe()/unsubscribe()/notify(event).
#     4) Implementieren Sie konkrete Observer (AlertObserver, AuditObserver,
#        DashboardObserver).
#     5) Die Domäne triggert nur noch ein Event (Verletzung Open/Close Prinzip (OCP)) – ohne Empfänger zu kennen.
# ============================================================

from dataclasses import dataclass

# Domäne + alle Reaktionen hart verdrahtet (ANTI-PATTERN)
@dataclass
class Patient:
    pid: str
    name: str
    risk: str = "low"

class PatientService:
    def __init__(self):
        pass

    def set_risk(self, p: Patient, new_risk: str) -> None:
        old = p.risk
        p.risk = new_risk

        # Direktaufrufe: starke Kopplung, kein OCP
        if old != new_risk:
            self._send_alert(p, old, new_risk)
            self._write_audit(p, old, new_risk)
            self._update_dashboard(p, old, new_risk)

    # „verstreute“ Reaktionslogik:
    def _send_alert(self, p, old, new):
        print(f"[ALERT] {p.pid} {p.name}: {old} -> {new}")

    def _write_audit(self, p, old, new):
        print(f"[AUDIT] Risk change for {p.pid}: {old} -> {new}")

    def _update_dashboard(self, p, old, new):
        print(f"[DASHBOARD] Update badge for {p.pid}: {new}")

if __name__ == "__main__":
    svc = PatientService()
    pat = Patient("p001", "Max Mustermann", "low")
    svc.set_risk(pat, "high")  # alle Reaktionen sind hart in der Domäne verdrahtet
