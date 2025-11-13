# Szenario:
#   Das Mentcare-System verwaltet verschiedene Arten von Patienten:
#     - StandardPatient
#     - EmergencyPatient
#     - Outpatient
#
#   Je nach Typ unterscheiden sich Behandlungspriorität und Gebührenmodell.
#
# Problem:
#   Der aktuelle Code erstellt Objekte mit if/else-Logik direkt im Hauptprogramm.
#   Neue Patiententypen erfordern Änderungen an allen Stellen, die Objekte erzeugen.
#
# Ziel:
#   Refaktorieren Sie auf das Factory Pattern:
#     1️⃣ Definieren Sie eine gemeinsame Basisklasse `Patient`.
#     2️⃣ Implementieren Sie konkrete Subklassen (`StandardPatient`, `EmergencyPatient`, `Outpatient`).
#     3️⃣ Erstellen Sie eine `PatientFactory`, die anhand eines Typs das passende Objekt zurückgibt.
#     4️⃣ Der Client-Code soll keine if/else-Logik mehr enthalten.
# ============================================================

class Patient:
    def __init__(self, pid, name, priority, billing):
        self.pid = pid
        self.name = name
        self.priority = priority
        self.billing = billing

    def __str__(self):
        return f"{self.name} ({self.priority}, {self.billing})"

def create_patient(ptype, pid, name):
    # schlechte Lösung: direkte if/else-Logik
    if ptype == "standard":
        return Patient(pid, name, "normal", "basic")
    elif ptype == "emergency":
        return Patient(pid, name, "high", "insurance-covered")
    elif ptype == "outpatient":
        return Patient(pid, name, "low", "per-visit")
    else:
        raise ValueError("Unbekannter Patiententyp")

if __name__ == "__main__":
    patients = [
        create_patient("standard", "p001", "Max Mustermann"),
        create_patient("emergency", "p002", "Erika Musterfrau"),
        create_patient("outpatient", "p003", "Anna Schmidt"),
    ]

    for p in patients:
        print(p)
