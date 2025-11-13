# good_hex_mentcare.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol, Iterable, List

# ================== Domain ==================
@dataclass(frozen=True)
class Appointment:
    patient_id: str
    when: datetime
    reason: str

def is_imminent(appt: Appointment, now: datetime) -> bool:
    delta = appt.when - now
    return 0 <= delta.total_seconds() <= 24 * 3600  # < 24h

# ================== Ports (abstrakt) ==================
class AppointmentRepository(Protocol):
    def add(self, appt: Appointment) -> None: ...
    def all(self) -> Iterable[Appointment]: ...

class Notifier(Protocol):
    def notify(self, message: str) -> None: ...

class Clock(Protocol):
    def now(self) -> datetime: ...

# ================== Application (Use-Cases / Core) ==================
class AppointmentService:
    def __init__(self, repo: AppointmentRepository, notifier: Notifier, clock: Clock) -> None:
        self.repo = repo
        self.notifier = notifier
        self.clock = clock

    def schedule_appointment(self, patient_id: str, when_iso: str, reason: str) -> Appointment:
        appt = Appointment(patient_id, datetime.fromisoformat(when_iso), reason.strip())
        self.repo.add(appt)
        return appt

    def send_imminent_reminders(self) -> List[Appointment]:
        now = self.clock.now()
        due: List[Appointment] = [a for a in self.repo.all() if is_imminent(a, now)]
        for a in due:
            self.notifier.notify(f"[REMINDER] Patient {a.patient_id}: Termin {a.when.isoformat()} - {a.reason}")
        return due

# ================== Adapters (Infrastruktur) ==================
# In-Memory Repo für schnelle Übung/Tests
class InMemoryAppointmentRepo(AppointmentRepository):
    def __init__(self): self._data: List[Appointment] = []
    def add(self, appt: Appointment) -> None: self._data.append(appt)
    def all(self) -> Iterable[Appointment]: return list(self._data)

class PrintNotifier(Notifier):
    def notify(self, message: str) -> None: print(message)

class SystemClock(Clock):
    def now(self) -> datetime: return datetime.now()

# ================== Input Adapter (CLI) ==================
def main():
    repo = InMemoryAppointmentRepo()
    notifier = PrintNotifier()
    clock = SystemClock()
    app = AppointmentService(repo, notifier, clock)

    while True:
        print("\n1) Termin anlegen  2) Termine anzeigen  3) Reminders senden  4) Ende")
        c = input("> ").strip()
        if c == "1":
            pid = input("Patient-ID: ").strip()
            when_iso = input("Zeitpunkt (YYYY-MM-DDTHH:MM): ").strip()
            reason = input("Grund: ").strip()
            a = app.schedule_appointment(pid, when_iso, reason)
            print("OK gespeichert:", a)
        elif c == "2":
            for a in repo.all():
                print(f"{a.patient_id} @ {a.when.isoformat()} - {a.reason}")
        elif c == "3":
            due = app.send_imminent_reminders()
            print(f"Gesendet: {len(due)} Reminder")
        elif c == "4":
            break
        else:
            print("Ungültig")

if __name__ == "__main__":
    main()
