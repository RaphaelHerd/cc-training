# bad_mvc_mentcare_minimal.py
# ============================================================
# ÜBUNG: MVC (Model-View-Controller) im Mentcare-Kontext (Kurzversion)
#
# ZIELE:
# 1) Verantwortlichkeiten trennen:
#    - Model: Patient + PatientList (Zustand & Geschäftslogik)
#    - View: ConsoleView (nur Darstellung & Eingabe)
#    - Controller: MentcareController (steuert die Use-Cases)
#
# AUFGABEN:
# A) Analysiere, warum hier Model, View und Controller vermischt sind.
# B) Refaktoriere in drei Klassen: Model, View, Controller.
# C) Implementiere nur:
#    - add_patient()
#    - list_patients()
# ============================================================

from dataclasses import dataclass

@dataclass
class Patient:
    pid: str
    name: str
    risk: str = "low"

def run():
    patients = []

    while True:
        print("\n== MENTCARE (anti-MVC) ==")
        print("1) Patient anlegen")
        print("2) Patient:innen anzeigen")
        print("3) Ende")
        choice = input("> ").strip()

        if choice == "1":
            pid = input("ID: ").strip()
            name = input("Name: ").strip()
            risk = input("Risiko (low/high): ").strip() or "low"
            if not pid or not name:
                print("Fehler: ID und Name sind erforderlich.")
                continue
            if risk not in ("low", "high"):
                print("Ungültiges Risiko, setze 'low'.")
                risk = "low"
            patient = Patient(pid, name, risk)
            patients.append(patient)
            if patient.risk == "high":
                print(f"[ALERT] High-Risk: {patient.pid} {patient.name}")
            print("OK gespeichert.")

        elif choice == "2":
            if not patients:
                print("(leer)")
            else:
                for p in patients:
                    mark = "!!!" if p.risk == "high" else "·"
                    print(f"[{p.pid}] {mark} {p.name} ({p.risk})")

        elif choice == "3":
            break
        else:
            print("Ungültig.")

if __name__ == "__main__":
    run()