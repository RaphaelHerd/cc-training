# good_command_mentcare_minimal.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, Dict, List

# ---------- Receiver ----------
class AppointmentBook:
    """Fachlogik zur Terminverwaltung (in-memory)."""
    def __init__(self) -> None:
        self._appts: Dict[str, Dict[str, object]] = {}

    def schedule(self, pid: str, when: datetime, reason: str) -> None:
        self._appts[pid] = {"when": when, "reason": reason}
        print(f"[BOOK] Termin angelegt: {pid} @ {when.isoformat()} ({reason})")

    def cancel(self, pid: str) -> None:
        if pid in self._appts:
            del self._appts[pid]
            print(f"[BOOK] Termin gelöscht: {pid}")

    def all(self) -> Dict[str, Dict[str, object]]:
        return dict(self._appts)

# ---------- Command Interface ----------
class Command(Protocol):
    def execute(self) -> None: ...

# ---------- Concrete Commands ----------
@dataclass
class ScheduleAppointment(Command):
    book: AppointmentBook
    pid: str
    when_iso: str
    reason: str

    def execute(self) -> None:
        self.book.schedule(self.pid, datetime.fromisoformat(self.when_iso), self.reason)
        print(f"[CMD] schedule({self.pid})")

@dataclass
class CancelAppointment(Command):
    book: AppointmentBook
    pid: str

    def execute(self) -> None:
        self.book.cancel(self.pid)
        print(f"[CMD] cancel({self.pid})")

# ---------- Invoker ----------
class CommandBus:
    """Führt beliebige Commands über eine gemeinsame Schnittstelle aus."""
    def __init__(self) -> None:
        self._history: List[str] = []  # nur zur Demo

    def dispatch(self, cmd: Command) -> None:
        cmd.execute()
        self._history.append(cmd.__class__.__name__)

# ---------- Demo ----------
if __name__ == "__main__":
    book = AppointmentBook()
    bus = CommandBus()

    bus.dispatch(ScheduleAppointment(book, "p001", "2025-11-01T09:00", "Intake"))
    bus.dispatch(CancelAppointment(book, "p001"))

    print("Termine:", book.all())
