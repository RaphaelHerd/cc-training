# Szenario:
#   Das Mentcare-System bietet einen Service an, der Patientendaten
#   aus einer (simuliert) langsamen Quelle liefert.
#
# Problem:
#   Jeder Client muss sich selbst um:
#     - Authentifizierung,
#     - Caching und
#     - Logging kümmern.
#
#   Dadurch entstehen Redundanzen, Kopplung und geringe Wartbarkeit.
#
# Ziel:
#   Implementieren Sie das Proxy Pattern:
#     - Definieren Sie ein Interface `PatientService` mit `get_patient(pid)`.
#     - Implementieren Sie den echten Service (`RealPatientService`),
#       der langsam arbeitet.
#     - Implementieren Sie einen Proxy (`PatientServiceProxy`), der:
#         1️⃣ Authentifizierung prüft,
#         2️⃣ Caching nutzt und
#         3️⃣ Zugriffe loggt.
#     - Der Client soll nur mit dem Proxy arbeiten.
# ============================================================

import time

# --- langsamer „echter“ Service (Simulation) ---
_DB = {
    "p001": {"pid": "p001", "name": "Max Mustermann", "risk": "high"},
    "p002": {"pid": "p002", "name": "Erika Musterfrau", "risk": "low"},
}

def slow_service_call(pid: str):
    time.sleep(0.3)
    return _DB.get(pid)

# --- schlechter Client, alles vermischt ---
_CACHE = {}
AUTH_TOKEN = "secret123"

def get_patient(pid: str, token: str):
    if token != AUTH_TOKEN:
        print("[AUTH] Zugriff verweigert")
        return None
    if pid in _CACHE:
        print("[CACHE] Treffer:", pid)
        return _CACHE[pid]
    print("[SERVICE] Hole Patient:", pid)
    data = slow_service_call(pid)
    if data:
        _CACHE[pid] = data
        print("[LOG] Zugriff auf", pid)
    return data

if __name__ == "__main__":
    print(get_patient("p001", "secret123"))
    print(get_patient("p001", "secret123"))  # Cache-Treffer
    print(get_patient("p002", "wrong"))      # Auth-Fehler
