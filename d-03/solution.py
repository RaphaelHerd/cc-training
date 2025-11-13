# good_facade_mentcare.py
# ============================================================
# FACADE PATTERN – Mentcare Case Study
#
# Ziel:
#   Vereinfachung der Schnittstelle zum Patient-Registrierungsprozess.
#   Die Fassade kapselt mehrere Subsysteme (Validator, Repository, Logger, Mailer)
#   und bietet dem Client eine einzige Methode zur Interaktion an.
# ============================================================

class PatientValidator:
    def validate(self, name: str, age: int, email: str) -> None:
        if not name or age <= 0 or "@" not in email:
            raise ValueError("Ungültige Patientendaten")

class PatientRepository:
    def save(self, name: str, age: int, email: str) -> None:
        print(f"[DB] Patient gespeichert: {name}, {age}, {email}")

class Logger:
    def write_log(self, message: str) -> None:
        print(f"[LOG] {message}")

class Mailer:
    def send_mail(self, to: str, subject: str, body: str) -> None:
        print(f"[MAIL an {to}] {subject} – {body}")

# ---------- FACADE ----------
class MentcareFacade:
    """
    Vereinheitlicht die Schnittstelle zu mehreren Subsystemen und kapselt
    deren Interaktionen hinter einer klaren, einfach nutzbaren Methode.
    """

    def __init__(self):
        self.validator = PatientValidator()
        self.repo = PatientRepository()
        self.logger = Logger()
        self.mailer = Mailer()

    def register_patient(self, name: str, age: int, email: str) -> None:
        """Führt den gesamten Registrierungsprozess aus."""
        self.validator.validate(name, age, email)
        self.repo.save(name, age, email)
        self.logger.write_log(f"Neuer Patient registriert: {name}")
        self.mailer.send_mail(
            email,
            "Willkommen bei Mentcare",
            f"Hallo {name}, Ihre Registrierung war erfolgreich!"
        )

# ---------- Client-Code ----------
if __name__ == "__main__":
    mentcare = MentcareFacade()
    mentcare.register_patient("Max Mustermann", 35, "max@example.com")
