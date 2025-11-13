# Szenario:
#   Das Mentcare-System soll den Blutdruck eines Patienten abrufen.
#   Es existieren jedoch zwei verschiedene externe Anbieter (Vendor A und B),
#   die die Werte in unterschiedlichen Formaten liefern.
#
# Problem:
#   Die aktuelle Implementierung kennt die Details beider Anbieter
#   und verzweigt vendor-spezifisch. Dadurch ist der Code schlecht wartbar,
#   nicht erweiterbar und kaum testbar.
#
# Aufgabe:
#   Refaktorieren Sie den Code mithilfe des Adapter Patterns.
#   Ziel ist ein einheitliches Interface `VitalProvider` mit der Methode
#   `fetch_bp(patient_id) -> BloodPressure`.
#
#   Implementieren Sie:
#     - Eine Klasse `VendorAAdapter` für Vendor A
#     - Eine Klasse `VendorBAdapter` für Vendor B
#     - Einen Service `VitalService`, der nur gegen das Interface programmiert.
#
# Erwartetes Verhalten:
#   Beide Adapter liefern denselben Datentyp `BloodPressure`.
# ============================================================

from dataclasses import dataclass

@dataclass
class BloodPressure:
    systolic: int
    diastolic: int
    unit: str = "mmHg"

# --- Vendor APIs (unveränderbar) ---
def vendor_a_get_bp(patient_id: str):
    return {"sys": 120, "dia": 78}  # Format Dict

def vendor_b_query(patient_id: str):
    return (16.0, 10.5)  # Format Tuple (kPa), 1 kPa ≈ 7.5 mmHg

# --- Schlechte Implementierung (zu refaktorisieren) ---
class VitalService:
    def fetch_bp_for_patient(self, patient_id: str, vendor: str) -> BloodPressure:
        if vendor == "A":
            raw = vendor_a_get_bp(patient_id)
            return BloodPressure(raw["sys"], raw["dia"])
        elif vendor == "B":
            s_kpa, d_kpa = vendor_b_query(patient_id)
            return BloodPressure(int(s_kpa * 7.5), int(d_kpa * 7.5))
        else:
            raise ValueError("Unknown vendor")

if __name__ == "__main__":
    svc = VitalService()
    print(svc.fetch_bp_for_patient("p001", "A"))
    print(svc.fetch_bp_for_patient("p001", "B"))
