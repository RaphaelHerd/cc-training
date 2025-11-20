# Szenario:
#   Das System verwaltet Patiententermine. Die aktuelle Implementierung
#   ruft die Logik direkt auf und verzweigt per if/else.
#
# Ziel:
#   Refaktorieren Sie mit dem Command Pattern:
#     1) Definieren Sie ein Interface `Command` mit `execute()`.
#     2) Implementieren Sie Commands:
#          - `ScheduleAppointment`
#          - `CancelAppointment`
#     3) Implementieren Sie einen `CommandBus` (Invoker), der Commands ausführt.
#     4) Implementieren Sie `AppointmentBook` (Receiver) mit der eigentlichen Logik.
#
# ============================================================

from datetime import datetime

APPTS = {}  # pid -> {"when": datetime, "reason": str}

def handle(action: str, pid: str, when: str | None = None, reason: str | None = None):
    print(f"[ACTION] {action} für {pid}")
    if action == "schedule":
        APPTS[pid] = {"when": datetime.fromisoformat(when), "reason": reason or ""}
        print("[LOG] Termin erstellt")
    elif action == "cancel" and pid in APPTS:
        del APPTS[pid]
        print("[LOG] Termin gelöscht")

if __name__ == "__main__":
    handle("schedule", "p001", "2025-11-01T09:00", "Intake")
    handle("cancel", "p001")
    print("Termine:", APPTS)
