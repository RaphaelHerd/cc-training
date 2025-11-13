# Szenario:
#   Das Mentcare-System muss vollständige Patientenakten erzeugen.
#   Eine Akte enthält:
#     - Patientenstammdaten
#     - Diagnosen
#     - Medikamente
#     - geplante Termine
#
# Problem:
#   Der aktuelle Code erzeugt die Akte über einen Konstruktor mit vielen
#   Parametern. Das ist fehleranfällig, schlecht lesbar und kaum erweiterbar.
#
# Ziel:
#   Refaktorieren Sie mit dem Builder Pattern:
#     1️⃣ Definieren Sie eine Klasse `PatientRecord`, die alle relevanten
#         Felder enthält.
#     2️⃣ Implementieren Sie eine Builder-Klasse (`PatientRecordBuilder`),
#         die das Objekt schrittweise aufbaut.
#     3️⃣ Der Builder soll Methoden für einzelne Schritte bieten, z. B.:
#         - `with_diagnosis(d)`
#         - `add_medication(m)`
#         - `add_appointment(a)`
#     4️⃣ `build()` liefert das fertige Objekt zurück.
# ============================================================

class PatientRecord:
    def __init__(self, pid, name, diagnosis, medications, appointments):
        self.pid = pid
        self.name = name
        self.diagnosis = diagnosis
        self.medications = medications
        self.appointments = appointments

    def __str__(self):
        return f"{self.name} ({self.pid}): {self.diagnosis}, {len(self.medications)} Medikamente"

# Schlechter Code: viele Parameter und schwer lesbar
p = PatientRecord(
    "p001",
    "Max Mustermann",
    "Depression, F32.1",
    ["Sertralin 50mg", "Vitamin D"],
    ["2025-11-01: Intake", "2025-11-15: Kontrolle"]
)

print(p)
