# bad_hex_mentcare.py
# ============================================================
# ÜBUNG: Hexagonale Architektur (Ports & Adapters)
#
# ZIELE
# 1) Fachlogik (Domäne + Use-Cases) von Infrastruktur (I/O) entkoppeln.
# 2) Abhängigkeiten über Ports (Interfaces) invertieren.
# 3) Testbarkeit erreichen via austauschbare Adapter (Repo, Notifier, Clock).
#
# AUFGABEN
# A) Identifiziere Vermischungen: CLI, Zeit, Storage, Benachrichtigung in einer Klasse.
# B) Extrahiere Ports: AppointmentRepository, Notifier, Clock.
# C) Baue Anwendungsfälle:
#    - schedule_appointment(pid, when_iso, reason)
#    - send_imminent_reminders()  (Reminder < 24h)
# D) Implementiere einfache In-Memory-Adapter + Print-Notifier.
# ============================================================

from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import os

DATA_FILE = "appointments.json"  # harte Infrastruktur-Abhängigkeit

@dataclass
class Appointment:
    patient_id: str
    when: datetime
    reason: str

class MentcareApp:  # macht alles: Domäne, Persistenz, Zeit, UI, Notifier
    def __init__(self):
        self.storage = DATA_FILE
        if not os.path.exists(self.storage):
            with open(self.storage, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _now(self):
        return datetime.now()  # harter Zeitbezug -> schwer testbar

    def _load(self):
        with open(self.storage, "r", encoding="utf-8") as f:
            raw = json.load(f)
        appts = []
        for a in raw:
            appts.append(Appointment(a["patient_id"], datetime.fromisoformat(a["when"]), a["reason"]))
        return appts

    def _save(self, appts):
        with open(self.storage, "w", encoding="utf-8") as f:
            json.dump([{"patient_id": a.patient_id, "when": a.when.isoformat(), "reason": a.reason} for a in appts], f)

    def schedule_and_maybe_notify(self, patient_id: str, when_iso: str, reason: str):
        # Use-Case + Zeit + Persistenz + Benachrichtigung vermischt
        appts = self._load()
        when_dt = datetime.fromisoformat(when_iso)
        appts.append(Appointment(patient_id, when_dt, reason))
        self._save(appts)
        print("OK gespeichert.")  # "Notifier" ist implizit die Konsole

        # Reminder-Logik sofort (statt separater Use-Case)
        if 0 <= (when_dt - self._now()).total_seconds() <= 24 * 3600:
            print(f"[REMINDER] Patient {patient_id}: Termin in <24h ({when_iso}) - {reason}")

    def list_appointments(self):
        for a in self._load():
            print(f"{a.patient_id} @ {a.when.isoformat()} - {a.reason}")

def main():
    app = MentcareApp()
    while True:
        print("\n1) Termin anlegen  2) Termine anzeigen  3) Ende")
        c = input("> ").strip()
        if c == "1":
            pid = input("Patient-ID: ").strip()
            when_iso = input("Zeitpunkt (YYYY-MM-DDTHH:MM): ").strip()
            reason = input("Grund: ").strip()
            app.schedule_and_maybe_notify(pid, when_iso, reason)
        elif c == "2":
            app.list_appointments()
        elif c == "3":
            break
        else:
            print("Ungültig")

if __name__ == "__main__":
    main()
