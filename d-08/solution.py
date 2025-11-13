# good_builder_mentcare.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

# ---------- Zielobjekt ----------
@dataclass
class PatientRecord:
    """Repräsentiert eine vollständige Patientenakte."""
    pid: str
    name: str
    diagnosis: str = ""
    medications: List[str] = field(default_factory=list)
    appointments: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        meds = ", ".join(self.medications) if self.medications else "Keine"
        return (
            f"Patient {self.name} ({self.pid})\n"
            f"- Diagnose: {self.diagnosis or 'n/a'}\n"
            f"- Medikamente: {meds}\n"
            f"- Termine: {len(self.appointments)} geplant"
        )

# ---------- Builder ----------
class PatientRecordBuilder:
    """Ermöglicht den schrittweisen Aufbau einer komplexen Patientenakte."""
    def __init__(self, pid: str, name: str) -> None:
        self._pid = pid
        self._name = name
        self._diagnosis: str = ""
        self._medications: List[str] = []
        self._appointments: List[str] = []

    def with_diagnosis(self, diagnosis: str) -> PatientRecordBuilder:
        self._diagnosis = diagnosis
        return self

    def add_medication(self, med: str) -> PatientRecordBuilder:
        self._medications.append(med)
        return self

    def add_appointment(self, appt: str) -> PatientRecordBuilder:
        self._appointments.append(appt)
        return self

    def build(self) -> PatientRecord:
        return PatientRecord(
            pid=self._pid,
            name=self._name,
            diagnosis=self._diagnosis,
            medications=self._medications,
            appointments=self._appointments,
        )

# ---------- Demo / Anwendung ----------
if __name__ == "__main__":
    builder = PatientRecordBuilder("p001", "Max Mustermann")

    patient = (
        builder
        .with_diagnosis("Depression, F32.1")
        .add_medication("Sertralin 50mg")
        .add_medication("Vitamin D")
        .add_appointment("2025-11-01: Intake")
        .add_appointment("2025-11-15: Kontrolle")
        .build()
    )

    print("=== Mentcare Patientenakte ===")
    print(patient)
