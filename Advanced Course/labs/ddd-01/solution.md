# Domain-Driven Design (DDD) - ClinicCare Use Case

> **Context:** You are developing **ClinicCare**, a simplified patient management system for a small outpatient clinic.
> The system must register patients, open treatment cases, prescribe medications, and record basic alerts (e.g., medication conflicts or risk flags).
> It should support **event-driven reporting** for monthly summaries and follow **DDD principles**.
> Privacy and correctness of domain rules are key, but the technical setup should stay minimal and runnable from the command line.

---

## 🎯 Your Goal

Build a minimal **DDD-based Python prototype** of ClinicCare.
You’ll identify **bounded contexts**, model **aggregates and value objects**, emit **domain events**, and build a small **reporting projection**.
Focus on code readability and clear separation of domain and application layers.

---

## 📦 Deliverables

* 📁 A Python package `clinicare/` with `domain`, `application`, and `infrastructure` layers.
* ⚙️ A CLI script or simple demo to run a basic use case.
* 🧪 A few `pytest` tests to prove key domain rules.
* 📝 A `README.md` explaining your design briefly.

---

## 🗂️ Suggested Folder Structure

```
clinicare/
  domain/
    patients.py
    cases.py
    events.py
    exceptions.py
  application/
    use_cases.py
  infrastructure/
    repositories.py
    event_bus.py
    projections.py
  cli/
    demo.py
tests/
  test_domain_patients.py
  test_use_cases.py
```

---

## 🗣️ Ubiquitous Language

* **Patient** 🧍: a registered person receiving care.
* **Case** 📋: a treatment episode (open/closed).
* **MedicationOrder** 💊: a prescribed medication.
* **Alert** ⚠️: triggered by specific domain events (e.g., risky medication combination).
* **Report** 📊: monthly summary for clinic administration.

---

# 🧩 Tasks

## 🧱 Task 1 - Define Bounded Contexts

Keep it simple:

* **Patient Management** — register and update patient info.
* **Treatment** — open/close cases and prescribe medication.
* **Reporting** — count monthly admissions and prescriptions.

Model it first by drawing it on a paper or whiteboard or draw a quick context map (ASCII or text) and note relationships.

**Output:** `CONTEXT_MAP.md`

---

## 🧬 Task 2 - Model the Core Domain

Model the main entities and value objects with domain rules:

* `Patient` (aggregate root)
* `Case` (aggregate root, references patient)
* `MedicationOrder` (value object, inside Case)

Invariants:

* Patient’s birth date must be in the past.
* A case must be *open* before medications are prescribed.
* A case cannot be discharged twice.

Model it first by drawing it on a paper or whiteboard.

After that use Python `dataclasses` or `pydantic`.

**Output:** `clinicare/domain/*.py` + tests ✅

---

## 📢 Task 3 - Domain Events

Emit events such as:

* `PatientRegistered`
* `CaseOpened`
* `MedicationPrescribed`

Build a minimal **in-memory event bus** and subscribe a handler that raises a simple `Alert` if two conflicting medications are prescribed.

**Output:** `domain/events.py`, `infrastructure/event_bus.py`, and tests.

---

## 🧰 Task 4 - Application Layer

Implement simple use cases that orchestrate the domain:

* `register_patient(...)`
* `open_case(patient_id, ...)`
* `prescribe_medication(case_id, ...)`
* `close_case(case_id, ...)`

Use repositories and publish domain events through the event bus.

**Output:** `application/use_cases.py` + tests.

---

## 📊 Task 5 - Reporting Projection

Subscribe to domain events and keep simple monthly counters:

* Number of new patients.
* Number of cases opened.
* Number of medications prescribed.

Provide a method like `get_report(month)` to print a monthly summary.

**Output:** `infrastructure/projections.py` + CLI demo.

---

## 🔒 Task 6 - Privacy Rule (Simplified)

Ensure that the report does **not** include sensitive fields (like patient names).
Write a small test verifying that reports only contain counts and totals.

---

# ✅ Acceptance Criteria

* Business rules are enforced inside domain entities (not just app code).
* Domain events trigger alerts and reports.
* Tests prove invariants and projections.
* No personal data leaks into reporting models.
* Code is clean, modular, and separated by context.

---

# 💡 Example Implementation

```python
# clinicare/domain/events.py
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, List, Type
import uuid

@dataclass(frozen=True)
class DomainEvent:
    id: str
    occurred_at: datetime

@dataclass(frozen=True)
class PatientRegistered(DomainEvent):
    patient_id: str

@dataclass(frozen=True)
class CaseOpened(DomainEvent):
    case_id: str
    patient_id: str

@dataclass(frozen=True)
class MedicationPrescribed(DomainEvent):
    case_id: str
    medication: str

class EventBus:
    def __init__(self):
        self._handlers: Dict[Type[DomainEvent], List[Callable]] = {}

    def subscribe(self, event_type, handler):
        self._handlers.setdefault(event_type, []).append(handler)

    def publish(self, event):
        for etype, handlers in self._handlers.items():
            if isinstance(event, etype):
                for h in handlers:
                    h(event)

def new_event_id():
    return str(uuid.uuid4())
```

```python
# clinicare/domain/patients.py
from dataclasses import dataclass, field
from datetime import date, datetime
from .events import PatientRegistered, new_event_id
from .exceptions import DomainError

@dataclass(frozen=True)
class PatientId:
    value: str

@dataclass
class Patient:
    patient_id: PatientId
    name: str
    date_of_birth: date
    _events: list = field(default_factory=list, init=False, repr=False)

    def __post_init__(self):
        if self.date_of_birth >= date.today():
            raise DomainError("Date of birth must be in the past")

    @classmethod
    def register(cls, patient_id: str, name: str, dob: date):
        p = cls(patient_id=PatientId(patient_id), name=name, date_of_birth=dob)
        p._events.append(
            PatientRegistered(id=new_event_id(), occurred_at=datetime.utcnow(), patient_id=patient_id)
        )
        return p

    def pull_events(self):
        ev, self._events = self._events, []
        return ev
```

```python
# clinicare/infrastructure/repositories.py
class InMemoryPatientRepository:
    def __init__(self):
        self._store = {}

    def get(self, pid):
        return self._store.get(pid.value)

    def save(self, patient):
        self._store[patient.patient_id.value] = patient
```

```python
# clinicare/application/use_cases.py
from clinicare.domain.patients import Patient, PatientId
from clinicare.domain.events import EventBus

class RegisterPatient:
    def __init__(self, repo, bus: EventBus):
        self.repo, self.bus = repo, bus

    def __call__(self, patient_id, name, dob):
        if self.repo.get(PatientId(patient_id)):
            raise ValueError("Patient already exists")
        p = Patient.register(patient_id, name, dob)
        self.repo.save(p)
        for e in p.pull_events():
            self.bus.publish(e)
        return p
```

```python
# clinicare/infrastructure/projections.py
from collections import defaultdict
from dataclasses import dataclass

@dataclass
class MonthlyReport:
    new_patients: int = 0
    cases_opened: int = 0
    meds_prescribed: int = 0

class ReportingProjection:
    def __init__(self):
        self._reports = defaultdict(MonthlyReport)

    def _key(self, dt): return (dt.year, dt.month)

    def on_patient_registered(self, e): 
        self._reports[self._key(e.occurred_at)].new_patients += 1

    def on_case_opened(self, e): 
        self._reports[self._key(e.occurred_at)].cases_opened += 1

    def on_medication_prescribed(self, e):
        self._reports[self._key(e.occurred_at)].meds_prescribed += 1

    def get_report(self, year, month):
        return self._reports[(year, month)]
```

---

# 🧪 Example Test

```python
def test_patient_dob_must_be_in_past():
    from datetime import date, timedelta
    import pytest
    from clinicare.domain.patients import Patient

    with pytest.raises(Exception):
        Patient.register("p1", "Alice", date.today() + timedelta(days=1))
```

---

# 🧭 Simplified Reference Solution

**Contexts:**

* Patient Management → publishes `PatientRegistered`
* Treatment → publishes `CaseOpened`, `MedicationPrescribed`
* Reporting → subscribes to both and counts events

**Aggregates:**

* Patient
* Case (with medications)

**Events Drive:**

* Alerts (e.g., medication conflicts)
* Monthly report projection

**Privacy:**

* Reports only contain counts — no patient names or identifiers.
