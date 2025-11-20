# good_proxy_mentcare_service.py
from __future__ import annotations
from typing import Protocol, Optional, Dict
import time

# ------------------- Service Interface (Subject) -------------------
class PatientService(Protocol):
    """Definiert die gemeinsame Schnittstelle für RealService und Proxy."""
    def get_patient(self, pid: str) -> Optional[dict]: ...

# ------------------- Real Subject -------------------
class RealPatientService(PatientService):
    """Der echte Service, der (simuliert) langsam arbeitet."""
    _DB: Dict[str, dict] = {
        "p001": {"pid": "p001", "name": "Max Mustermann", "risk": "high"},
        "p002": {"pid": "p002", "name": "Erika Musterfrau", "risk": "low"},
    }

    def get_patient(self, pid: str) -> Optional[dict]:
        time.sleep(0.3)  # simuliert langsame externe Abfrage
        return self._DB.get(pid)

# ------------------- Proxy -------------------
class PatientServiceProxy(PatientService):
    """
    Der Proxy steht zwischen Client und RealPatientService.
    Er übernimmt:
    - Authentifizierung (Tokenprüfung)
    - Caching von Patientendaten
    - Logging der Zugriffe
    """
    def __init__(self, real_service: PatientService, valid_token: str):
        self._real_service = real_service
        self._valid_token = valid_token
        self._cache: Dict[str, dict] = {}

    def get_patient(self, pid: str, token: Optional[str] = None) -> Optional[dict]:
        # 1) Authentifizierung
        if token != self._valid_token:
            print("[PROXY:AUTH] Zugriff verweigert")
            return None

        # 2) Cache prüfen
        if pid in self._cache:
            print("[PROXY:CACHE] Treffer:", pid)
            return self._cache[pid]

        # 3) Zugriff an echten Service weiterleiten
        print("[PROXY] Weiterleitung an RealPatientService:", pid)
        patient = self._real_service.get_patient(pid)
        if patient:
            self._cache[pid] = patient
            print("[PROXY:LOG] Zugriff auf", pid)
        return patient

# ------------------- Client -------------------
if __name__ == "__main__":
    real_service = RealPatientService()
    proxy = PatientServiceProxy(real_service, valid_token="secret123")

    # gültiger Zugriff
    print(proxy.get_patient("p001", token="secret123"))
    print(proxy.get_patient("p001", token="secret123"))  # Cache-Treffer

    # ungültiger Zugriff
    print(proxy.get_patient("p002", token="wrong"))
