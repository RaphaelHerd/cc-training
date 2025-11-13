# not_testable.py
# =================================================
# ZIEL:
# - Erkenne, warum dieser Code schwer unit-testbar ist.
# - Refaktoriere so, dass Repository und Mailer injizierbar sind (Dependency Injection).
#
# AUFGABEN:
# 1) Identifiziere harte Abhängigkeiten (Datei I/O, SMTP).
# 2) Extrahiere Interfaces/Protokolle und injiziere Implementierungen.
# 3) Schreibe Tests, die Fake-Implementierungen verwenden.
# =================================================

import csv
from dataclasses import dataclass
from datetime import date
import smtplib

DATA_FILE = "data/patients.csv"
ALERT_EMAIL = "alerts@hospital.local"

@dataclass
class Patient:
    pid: str
    name: str
    birthdate: date
    risk: str  # "low"|"medium"|"high"

class ReportGenerator:
    """Dieses Klasse ist schwer testbar, weil sie Dateipfade und SMTP selbst nutzt."""
    def __init__(self):
        self.data_file = DATA_FILE
        self.alert_email = ALERT_EMAIL

    def _load_patients(self):
        rows = []
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                rows = list(csv.reader(f))
        except FileNotFoundError:
            return []
        pts = [Patient(r[0], r[1], date.fromisoformat(r[2]), r[3]) for r in rows]
        return pts

    def _send_alert(self, subject, body):
        # direkte Bindung an smtplib (schwer zu mokken)
        with smtplib.SMTP("localhost") as smtp:
            msg = f"Subject: {subject}\n\n{body}"
            smtp.sendmail("noreply@local", self.alert_email, msg)

    def create_report_and_alert(self):
        patients = self._load_patients()
        high = sum(1 for p in patients if p.risk == "high")
        if high > 0:
            self._send_alert("High-risk patients", f"There are {high} high-risk patients.")
        return {"total": len(patients), "high": high}

# Example usage (harter Codepfad beim Import)
if __name__ == "__main__":
    rg = ReportGenerator()
    print(rg.create_report_and_alert())
