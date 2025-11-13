# good_mvc_mentcare_minimal.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List

# ---------- Model (Zustand & Geschäftslogik) ----------
@dataclass(frozen=True)
class Patient:
    pid: str
    name: str
    risk: str = "low"

class PatientList:
    def __init__(self) -> None:
        self._patients: List[Patient] = []

    def add(self, pid: str, name: str, risk: str = "low") -> Patient:
        pid, name, risk = pid.strip(), name.strip(), (risk or "low").lower()
        if not pid or not name:
            raise ValueError("ID und Name sind erforderlich.")
        if risk not in ("low", "high"):
            risk = "low"
        p = Patient(pid, name, risk)
        self._patients.append(p)
        return p

    def all(self) -> List[Patient]:
        return list(self._patients)

# ---------- View (Darstellung & Eingabe) ----------
class ConsoleView:
    def show_menu(self) -> str:
        print("\n== MENTCARE (MVC) ==")
        print("1) Patient anlegen")
        print("2) Patient:innen anzeigen")
        print("3) Ende")
        return input("> ").strip()

    def prompt(self, label: str) -> str:
        return input(f"{label}: ").strip()

    def show_patients(self, patients: List[Patient]) -> None:
        if not patients:
            print("(leer)")
            return
        for p in patients:
            mark = "!!!" if p.risk == "high" else "·"
            print(f"[{p.pid}] {mark} {p.name} ({p.risk})")

    def alert_high_risk(self, p: Patient) -> None:
        print(f"[ALERT] High-Risk: {p.pid} {p.name}")

    def info(self, msg: str) -> None:
        print(msg)

    def error(self, msg: str) -> None:
        print(f"Fehler: {msg}")

# ---------- Controller (Use-Cases) ----------
class MentcareController:
    def __init__(self, model: PatientList, view: ConsoleView) -> None:
        self.model = model
        self.view = view

    def add_patient(self) -> None:
        pid = self.view.prompt("ID")
        name = self.view.prompt("Name")
        risk = self.view.prompt("Risiko (low/high)") or "low"
        try:
            p = self.model.add(pid, name, risk)
            if p.risk == "high":
                self.view.alert_high_risk(p)
            self.view.info("OK gespeichert.")
        except Exception as e:
            self.view.error(str(e))

    def list_patients(self) -> None:
        self.view.show_patients(self.model.all())

# ---------- Composition Root ----------
def main():
    model = PatientList()
    view = ConsoleView()
    ctrl = MentcareController(model, view)

    actions = {"1": ctrl.add_patient, "2": ctrl.list_patients, "3": lambda: None}
    choice = ""
    while choice != "3":
        choice = view.show_menu()
        action = actions.get(choice)
        if action:
            action()
        else:
            view.error("Ungültige Auswahl.")

if __name__ == "__main__":
    main()
