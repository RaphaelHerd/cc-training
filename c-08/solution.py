# good_service_contract.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

# ---------- Model ----------
@dataclass(frozen=True)
class Patient:
    name: str
    age: int
    risk: Literal["low", "high"]

# ---------- Service Contract ----------
def assess_risk(name: str, age: int) -> Patient:
    """
    Bewertet das Risiko einer Person anhand des Alters.

    SERVICE CONTRACT:
      Eingabeparameter:
        - name: Name der Person (nicht leer)
        - age: Alter in Jahren (>= 0)

      Rückgabe:
        - Patient-Objekt mit berechnetem Risikowert ("low" oder "high")

      Nebenwirkungen/Seiteneffekte:
        - Keine (reine Funktion)
    """
    if not name.strip():
        raise ValueError("Name darf nicht leer sein.")
    if age < 0:
        raise ValueError("Alter darf nicht negativ sein.")

    risk = "high" if age > 65 else "low"
    return Patient(name=name.strip(), age=age, risk=risk)

# ---------- Anwendungsschicht ----------
def print_result(patient: Patient) -> None:
    """Darstellung (keine Geschäftslogik)."""
    print(f"[{patient.risk.upper()}] {patient.name}, {patient.age} Jahre")
    if patient.risk == "high":
        print(f"ALERT: {patient.name} ist Hochrisiko-Patient!")

# ---------- Beispiel: Nutzung des Service Contracts ----------
def main():
    while True:
        print("\n== Mentcare Risk Assessment ==")
        name = input("Name: ")
        if not name:
            break
        try:
            age = int(input("Alter: "))
            patient = assess_risk(name, age)  # klarer Vertrag
            print_result(patient)
        except Exception as e:
            print("Fehler:", e)

if __name__ == "__main__":
    main()
