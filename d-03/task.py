# Szenario:
#   Das Mentcare-System soll einen neuen Patienten aufnehmen.
#   Dabei müssen mehrere Teilsysteme (Validierung, Speicherung,
#   Log-Schreiben und Benachrichtigung) aufgerufen werden.
#
# Problem:
#   Der aktuelle Code ruft alle Subsysteme direkt auf, wodurch die
#   Hauptlogik unnötig komplex und stark gekoppelt ist.
#
# Ziel:
#   Fassen Sie die Aufrufe in einer zentralen Fassade (z. B. `MentcareFacade`)
#   zusammen, sodass das Hauptprogramm nur noch eine einzige Methode
#   aufrufen muss.
#
# ============================================================

class PatientValidator:
    def validate(self, name: str, age: int, email: str) -> bool:
        if not name or age <= 0 or "@" not in email:
            raise ValueError("Ungültige Patientendaten")
        return True

class PatientRepository:
    def save(self, name: str, age: int, email: str) -> None:
        print(f"[DB] Patient gespeichert: {name}, {age}, {email}")

class Logger:
    def write_log(self, message: str) -> None:
        print(f"[LOG] {message}")

class Mailer:
    def send_mail(self, to: str, subject: str, body: str) -> None:
        print(f"[MAIL an {to}] {subject} – {body}")

# --- Anti-Pattern: Hauptlogik ruft alles manuell auf ---
if __name__ == "__main__":
    validator = PatientValidator()
    repo = PatientRepository()
    logger = Logger()
    mailer = Mailer()

    name, age, email = "Max Mustermann", 35, "max@example.com"

    # Zu viele direkte Aufrufe:
    if validator.validate(name, age, email):
        repo.save(name, age, email)
        logger.write_log(f"Neuer Patient registriert: {name}")
        mailer.send_mail(email, "Willkommen bei Mentcare", "Ihre Registrierung war erfolgreich!")
