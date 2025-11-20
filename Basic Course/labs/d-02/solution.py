# good_adapter_mentcare_simple.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol

# --- Gemeinsames Domain-Modell ---
@dataclass(frozen=True)
class BloodPressure:
    systolic: int
    diastolic: int
    unit: str = "mmHg"

# --- Ziel-Interface (Port) ---
class VitalProvider(Protocol):
    def fetch_bp(self, patient_id: str) -> BloodPressure: ...

# --- Vendor APIs (unveränderbar) ---
def vendor_a_get_bp(patient_id: str):
    return {"sys": 120, "dia": 78}

def vendor_b_query(patient_id: str):
    return (16.0, 10.5)  # Einheit kPa

# --- Adapter für Vendor A ---
class VendorAAdapter(VitalProvider):
    def fetch_bp(self, patient_id: str) -> BloodPressure:
        raw = vendor_a_get_bp(patient_id)
        return BloodPressure(raw["sys"], raw["dia"])

# --- Adapter für Vendor B ---
class VendorBAdapter(VitalProvider):
    def fetch_bp(self, patient_id: str) -> BloodPressure:
        s_kpa, d_kpa = vendor_b_query(patient_id)
        return BloodPressure(int(s_kpa * 7.5), int(d_kpa * 7.5))

# --- Service, der nur das Interface kennt ---
class VitalService:
    def __init__(self, provider: VitalProvider):
        self.provider = provider

    def get_bp_snapshot(self, patient_id: str) -> BloodPressure:
        return self.provider.fetch_bp(patient_id)

# --- Demo ---
if __name__ == "__main__":
    for provider in [VendorAAdapter(), VendorBAdapter()]:
        service = VitalService(provider)
        bp = service.get_bp_snapshot("p001")
        print(f"{provider.__class__.__name__}: {bp.systolic}/{bp.diastolic} {bp.unit}")
