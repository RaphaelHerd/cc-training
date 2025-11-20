# Szenario:
#   Im Mentcare-System sollen die Gesamtkosten eines Behandlungsplans berechnet werden.
#   Ein Plan kann sowohl einzelne Maßnahmen (z. B. Medikation, Sitzung, Messung)
#   als auch Untergruppen (z. B. Wochenabschnitte) enthalten, die wiederum
#   mehrere Maßnahmen umfassen.
#
# Ausgangslage:
#   Der bisherige Code berechnet die Gesamtkosten mit verschachtelten if/else-Zweigen
#   und Typprüfungen auf Dictionaries. Dies führt zu einer unübersichtlichen und
#   schlecht erweiterbaren Implementierung.
#
# Ziel:
#   Refaktorieren Sie die Logik mithilfe des **Composite Patterns**, sodass
#   Gruppen und Einzelmaßnahmen über eine gemeinsame Schnittstelle verarbeitet
#   werden können.

plan = {
    "type": "group",
    "name": "Depressionsplan",
    "items": [
        {"type": "med", "name": "Sertralin 50mg", "cost": 49.90},
        {"type": "session", "name": "CBT Einzel", "rate_per_session": 80.0},
        {
            "type": "group",
            "name": "Monitoring-Woche",
            "items": [
                {"type": "measure", "name": "PHQ-9", "cost": 10.0},
                {"type": "session", "name": "Gruppentherapie", "rate_per_session": 60.0}
            ]
        }
    ]
}

def total_cost(node):
    if node["type"] == "med":
        return node["cost"]
    elif node["type"] == "session":
        return node["rate_per_session"]
    elif node["type"] == "measure":
        return node["cost"]
    elif node["type"] == "group":
        return sum(total_cost(c) for c in node["items"])
    else:
        return 0.0

if __name__ == "__main__":
    print("Gesamtkosten:", f"{total_cost(plan):.2f} €")
