# bad_mentcare.py  (ABSICHTLICH SCHLECHT)
# Verstöße:
# - SRP: PatientService macht alles (persistieren, Risiko berechnen, Berichte schreiben, "Mail" versenden, CLI).
# - OCP: if/elif für Ausgabeformate und Notifier-Typen -> bei neuen Formaten/Typen Code anpassen.
# - LSP: FilePatientRepository.save() erwartet bestimmte Felder; CachedPatientRepository bricht Verhalten (wirft bei leerem Namen),
#        und get_all() liefert je nach Cache None statt Liste.
# - ISP: Mega-"Notifier" mit E-Mail UND SMS, obwohl Implementierungen nur eines wirklich können.
# - DIP: PatientService hängt an konkreten Klassen (FilePatientRepository, SmtpClient) statt an Abstraktionen.

import csv
import json
from dataclasses import dataclass, asdict
from datetime import date

# --- Domain -----------------------------------------------------

@dataclass
class Patient:
    pid: str
    name: str
    birthdate: date
    risk: str  # "low" | "medium" | "high"

# --- Infrastructure (konkret & vermischt) ----------------------

class FilePatientRepository:
    def __init__(self, path="patients.csv"):
        self.path = path

    def save(self, p: Patient):
        # Erwartet alle Felder gesetzt, sonst Exception (starre Vorbedingung)
        if not p.pid or not p.name:
            raise ValueError("Missing pid or name")
        with open(self.path, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([p.pid, p.name, p.birthdate.isoformat(), p.risk])

    def get_all(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                rows = list(csv.reader(f))
            result = []
            for r in rows:
                result.append(
                    Patient(pid=r[0], name=r[1], birthdate=date.fromisoformat(r[2]), risk=r[3])
                )
            return result
        except FileNotFoundError:
            return []


class CachedPatientRepository(FilePatientRepository):
    """Pseudo-Cache, verletzt LSP: get_all kann None liefern, save verweigert bestimmte Daten."""
    def __init__(self, path="patients.csv"):
        super().__init__(path)
        self._cache = None

    def save(self, p: Patient):
        if not p.name.strip():  # strengere Bedingung als Basisklasse -> LSP-Verstoß
            raise RuntimeError("Empty name not allowed here")
        super().save(p)
        self._cache = None

    def get_all(self):
        if self._cache is None:
            # absichtlicher Fehler: manchmal None
            if self.path.endswith(".tmp"):
                return None
            self._cache = super().get_all()
        return self._cache


class SmtpClient:
    def send(self, to, subject, body):
        print(f"[SMTP] to={to} subj={subject} body={body}")


# "Fettes" Interface (ISP-Verstoß)
class Notifier:
    def send_email(self, to, subject, body): ...
    def send_sms(self, number, text): ...


class EmailNotifier(Notifier):
    def __init__(self):
        self.smtp = SmtpClient()

    def send_email(self, to, subject, body):
        self.smtp.send(to, subject, body)

    def send_sms(self, number, text):  # kann es nicht wirklich
        print("[WARN] SMS not supported via EmailNotifier")


# --- Application Service (Gottobjekt) --------------------------

class PatientService:
    def __init__(self):
        self.repo = CachedPatientRepository()  # DIP-Verstoß: konkrete Klasse
        self.notifier = EmailNotifier()        # DIP/ISP-Verstoß

    def register_patient(self, pid, name, birthdate, risk):
        p = Patient(pid, name, birthdate, risk)
        # Geschäftsregel inline:
        if risk == "high":
            self.notifier.send_email(
                to="alerts@hospital.local",
                subject=f"High Risk: {p.pid}",
                body=f"Patient {p.name} is HIGH risk"
            )
        self.repo.save(p)

    def monthly_report(self, fmt="csv"):
        all_patients = self.repo.get_all()
        if all_patients is None:  # wegen LSP-Verstoß oben nötig
            all_patients = []
        stats = {
            "count": len(all_patients),
            "high": sum(1 for p in all_patients if p.risk == "high"),
            "medium": sum(1 for p in all_patients if p.risk == "medium"),
            "low": sum(1 for p in all_patients if p.risk == "low"),
        }
        # OCP-Verstoß: Format-Schalter
        if fmt == "csv":
            with open("report.csv", "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["count", "high", "medium", "low"])
                w.writerow([stats["count"], stats["high"], stats["medium"], stats["low"]])
        elif fmt == "json":
            with open("report.json", "w", encoding="utf-8") as f:
                json.dump(stats, f)
        else:
            print("Unsupported format; printing:", stats)


# --- "CLI" zusammen mit Service-Logik --------------------------

if __name__ == "__main__":
    svc = PatientService()
    svc.register_patient("p001", "Max Mustermann", date(1980, 1, 12), "high")
    svc.register_patient("p002", "Erika Musterfrau", date(1972, 5, 3), "low")
    svc.monthly_report(fmt="csv")
