# good_factory_mentcare.py
from __future__ import annotations
from abc import ABC, abstractmethod

# ---------- Basisklasse ----------
class Patient(ABC):
    """Abstrakte Basisklasse für alle Patiententypen."""
    def __init__(self, pid: str, name: str) -> None:
        self.pid = pid
        self.name = name

    @abstractmethod
    def priority(self) -> str: ...
    @abstractmethod
    def billing_model(self) -> str: ...

    def __str__(self) -> str:
        return f"{self.name} ({self.priority()} | {self.billing_model()})"

# ---------- Konkrete Typen ----------
class StandardPatient(Patient):
    def priority(self) -> str:
        return "normal"
    def billing_model(self) -> str:
        return "basic"

class EmergencyPatient(Patient):
    def priority(self) -> str:
        return "high"
    def billing_model(self) -> str:
        return "insurance-covered"

class Outpatient(Patient):
    def priority(self) -> str:
        return "low"
    def billing_model(self) -> str:
        return "per-visit"

# ---------- Factory ----------
class PatientFactory:
    """Erzeugt Patient-Objekte anhand eines Typs (Factory Method)."""
    @staticmethod
    def create(ptype: str, pid: str, name: str) -> Patient:
        match ptype.lower():
            case "standard":
                return StandardPatient(pid, name)
            case "emergency":
                return EmergencyPatient(pid, name)
            case "outpatient":
                return Outpatient(pid, name)
            case _:
                raise ValueError(f"Unbekannter Patiententyp: {ptype}")

# ---------- Client ----------
if __name__ == "__main__":
    factory = PatientFactory()

    patients = [
        factory.create("standard", "p001", "Max Mustermann"),
        factory.create("emergency", "p002", "Erika Musterfrau"),
        factory.create("outpatient", "p003", "Anna Schmidt"),
    ]

    print("=== Mentcare Patientenliste ===")
    for p in patients:
        print(p)
