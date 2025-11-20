# bad_service_contract.py
# ============================================================
# ÜBUNG: SERVICE CONTRACTS / METHODENDEFINITIONEN
#
# ZIELE:
# 1) Erkenne, warum fehlende oder unklare Methodensignaturen
#    zu Fehlern, Missverständnissen und untestbarem Code führen.
# 2) Refaktoriere: definiere explizite Methoden mit klaren
#    Parametern, Rückgabewerten und Typannotationen.
# 3) Ziel: Jede Methode soll wie ein "Service Contract" wirken:
#    klar, testbar, verständlich.
#
# AUFGABEN:
# - Analysiere, was an diesem Code unklar ist.
# - Formuliere saubere Signaturen und Contracts.
# - Füge sinnvolle Rückgabewerte hinzu (z. B. Ergebnisobjekte oder Status).
# ============================================================

# --- Beispielkontext: Mentcare Mini-Service zur Risikobewertung ---

patients = []

def process(patient):
    # Was macht das? Unklar!
    if "risk" not in patient:
        patient["risk"] = "low"
    if patient.get("age", 0) > 65:
        patient["risk"] = "high"
    if patient["risk"] == "high":
        print(f"ALERT! {patient['name']} is high risk")
    patients.append(patient)

# Hauptlogik – aber ohne klaren Vertrag zwischen Funktionen
def main():
    while True:
        print("\n== Mentcare Risk Service ==")
        name = input("Name: ")
        age = input("Alter: ")
        if not name:
            break
        try:
            age = int(age)
        except:
            print("Ungültige Eingabe.")
            continue
        p = {"name": name, "age": age}
        process(p)

if __name__ == "__main__":
    main()
