# good_composite_total_cost.py
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

# -------- Component: einheitlicher Vertrag nur für Gesamtkosten --------
class CareItem(ABC):
    @abstractmethod
    def total_cost(self) -> float:
        """Gesamtkosten dieses Elements (rekursiv für Gruppen)."""
        ...

# --------------------------- Leaves ---------------------------
@dataclass(frozen=True)
class Medication(CareItem):
    name: str
    cost: float
    def total_cost(self) -> float:
        return self.cost

@dataclass(frozen=True)
class Session(CareItem):
    name: str
    rate_per_session: float
    def total_cost(self) -> float:
        return self.rate_per_session

@dataclass(frozen=True)
class Measurement(CareItem):
    name: str
    cost: float
    def total_cost(self) -> float:
        return self.cost

# --------------------------- Composite ---------------------------
class CareGroup(CareItem):
    def __init__(self, name: str, items: List[CareItem] | None = None) -> None:
        self.name = name
        self._items: List[CareItem] = list(items or [])
    def add(self, item: CareItem) -> None:
        self._items.append(item)
    def total_cost(self) -> float:
        return sum(i.total_cost() for i in self._items)

# --------------------------- Beispiel ---------------------------
def build_sample_plan() -> CareItem:
    monitoring = CareGroup("Monitoring-Woche", [
        Measurement("PHQ-9", 10.0),
        Session("Gruppentherapie", 60.0),
    ])
    return CareGroup("Depressionsplan", [
        Medication("Sertralin 50mg", 49.90),
        Session("CBT Einzel", 80.0),
        monitoring,
    ])

if __name__ == "__main__":
    plan = build_sample_plan()
    print(f"Gesamtkosten: {plan.total_cost():.2f} €")
