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

# ---- Domain Event Model ------------------------------------------------------
# In DDD, domain events represent *facts that have happened* in the domain.
# They are immutable records, produced by aggregates and consumed by handlers.
# Keeping events simple data structures helps cross-context communication.

@dataclass(frozen=True)
class DomainEvent:
    """
    Base class for all domain events.

    IMPLEMENTATION GUIDE:
    - No changes required; this is a value carrier.
    - When adding new fields to events, ensure they are non-sensitive and minimal.
    - Keep events immutable (frozen dataclass).

    Why: Enforces "happened-in-the-past" semantics and prevents mutation.
    """
    id: str
    occurred_at: datetime


# ---- Concrete Events ---------------------------------------------------------
# These events are intentionally minimal. They carry just enough information
# for downstream consumers (projections, policies) to do their job without
# leaking private/sensitive data.

@dataclass(frozen=True)
class PatientRegistered(DomainEvent):
    """Emitted when a new patient is registered."""
    patient_id: str

@dataclass(frozen=True)
class CaseOpened(DomainEvent):
    """Emitted when a treatment case is opened for a patient."""
    case_id: str
    patient_id: str

@dataclass(frozen=True)
class MedicationPrescribed(DomainEvent):
    """
    Emitted when a medication is prescribed within a case.
    For the training exercise, we keep this to a single 'medication' string.
    """
    case_id: str
    medication: str


# ---- Event Bus ---------------------------------------------------------------
# A minimal in-memory Pub/Sub bus for domain events.
# Aggregates publish events; handlers subscribe to event types and react.

class EventBus:
    def __init__(self):
        """
        IMPLEMENTATION GUIDE:
        - Initialize any in-memory structures needed for subscription management.
        - Keep it simple: dict of event_type -> [handlers].
        - Avoid persistence here.

        Why: Keeps infra minimal and predictable for unit tests.
        """
        # implement here

    def subscribe(self, event_type, handler):
        """
        Register a handler for a specific event type.

        IMPLEMENTATION GUIDE:
        1) Validate inputs (optional): ensure handler is callable.
        2) Use dict.setdefault(event_type, []).append(handler) to store.
        3) Document handler signature: def handler(event: EventType) -> None.

        Why: Allows projections/policies to react to event publications.
        """
        # implement here

    def publish(self, event):
        """
        Publish an event to all handlers that subscribed to its type.

        IMPLEMENTATION GUIDE:
        1) Iterate self._handlers.items().
        2) For each (etype, handlers), check isinstance(event, etype).
        3) If yes, call each handler(event).
        4) Keep handlers fast; do not swallow exceptions silently for training.
           (Optionally wrap and re-raise to surface failing handlers in tests.)

        Why: Decouples event producers from consumers; enables read models.
        """
        # implement here

def new_event_id():
    """
    Generate a unique event id.

    IMPLEMENTATION GUIDE:
    - Return a UUID4 string.
    - If you need deterministic ids during tests, monkeypatch this function.

    Why: Stable pattern for event identification and debugging.
    """
    return str(uuid.uuid4())

```

```python
# clinicare/domain/patients.py

from dataclasses import dataclass, field
from datetime import date, datetime
from .events import PatientRegistered, new_event_id
from .exceptions import DomainError

# ---- Value Objects -----------------------------------------------------------

@dataclass(frozen=True)
class PatientId:
    """
    Unique identity for a Patient aggregate.

    IMPLEMENTATION GUIDE:
    - Keep this immutable and comparable by value.
    - Add basic validation if needed (e.g., non-empty string).
    """
    value: str


# ---- Aggregate Root ----------------------------------------------------------

@dataclass
class Patient:
    """
    Patient aggregate root.

    IMPLEMENTATION GUIDE:
    - Hold only domain-relevant attributes (name, patient_id, date_of_birth).
    """
    #implement here

    # Internal, transient event buffer. Not persisted; drained by pull_events().
    _events: list = field(default_factory=list, init=False, repr=False)

    def __post_init__(self):
        """
        Enforce domain invariants at construction time.

        IMPLEMENTATION GUIDE:
        1) Check that date_of_birth < today; else raise DomainError.
        2) Add any further invariants relevant to Patient (optional), e.g.:
           - Non-empty name
           - Minimum age logic (if required by exercise)
        3) Keep this method free of side effects (no event emission here).

        Why: Invariants belong in the domain, not in the application layer.
        """
        #implement here

    @classmethod
    def register(cls, patient_id: str, name: str, dob: date):
        """
        Factory method to create a Patient and emit PatientRegistered.

        IMPLEMENTATION GUIDE:
        1) Construct the Patient instance with given data (will run __post_init__).
        2) Append a PatientRegistered event to the _events buffer with:
           - id=new_event_id()
           - occurred_at=datetime.utcnow()
           - patient_id=patient_id
        3) Return the aggregate (do not publish here; app layer does that).

        Why: Ensures event emission is part of the entity lifecycle.
        """
        p = cls(patient_id=PatientId(patient_id), name=name, date_of_birth=dob)
        p._events.append(
            PatientRegistered(
                id=new_event_id(),
                occurred_at=datetime.utcnow(),
                patient_id=patient_id
            )
        )
        return p

    def pull_events(self):
        """
        Return and clear the aggregate's unpublished events.

        IMPLEMENTATION GUIDE:
        1) Copy the current _events list into a local variable.
        2) Reset self._events to [] to avoid duplicate publications.
        3) Return the copied list.

        Why: Lets the application layer publish only after persistence succeeds.
        """
        ev, self._events = self._events, []
        return ev

```

```python
# clinicare/infrastructure/repositories.py

# Minimal in-memory repository implementation.
# In real systems, repositories wrap persistence details (DB/ORM) and translate between domain objects and storage representations. Here we keep it simple.

class InMemoryPatientRepository:
    def __init__(self):
        # Internal store keyed by patient_id string
        self._store = {}

    def get(self, pid):
        return self._store.get(pid.value)

    def save(self, patient):
        self._store[patient.patient_id.value] = patient

```

```python
# clinicare/application/use_cases.py

# Application services orchestrate domain objects, enforce application workflow,
# coordinate repositories and publish domain events. They should *not* contain
# business rules—that belongs in the domain layer.

from clinicare.domain.patients import Patient, PatientId
from clinicare.domain.events import EventBus

class RegisterPatient:
    def __init__(self, repo, bus: EventBus):
        self.repo, self.bus = repo, bus

    def __call__(self, patient_id, name, dob):
        """
        Execute the "register patient" use case.

        IMPLEMENTATION GUIDE:
        1) Check repository for existing patient via repo.get(PatientId(patient_id)).
           - If exists, raise ValueError("Patient already exists").
        2) Create the aggregate via Patient.register(patient_id, name, dob).
        3) Persist the new aggregate with repo.save(patient).
        4) Publish domain events:
           - Iterate patient.pull_events()
           - For each event, call self.bus.publish(event)
        5) Return the newly created Patient aggregate for further use (optional).

        Why:
        - Keeps orchestration and IO here.
        - Leaves invariants to the domain.
        - Publishes events *after* persistence to avoid ghost events.
        """

        # implement 1) to 3). Rest is already implemented
        
        for e in p.pull_events():
            self.bus.publish(e)

        return p

```

```python
# clinicare/infrastructure/projections.py

# Projections (a.k.a. read models) consume domain events and build a
# query-optimized view for reporting. They should not contain sensitive data
# from the domain; only what's needed for the read side.

from collections import defaultdict
from dataclasses import dataclass

@dataclass
class MonthlyReport:
    new_patients: int = 0
    cases_opened: int = 0
    meds_prescribed: int = 0

class ReportingProjection:
    def __init__(self):
        # (year, month) -> MonthlyReport
        self._reports = defaultdict(MonthlyReport)

    def _key(self, dt):
        return (dt.year, dt.month)

    # The following methods are intended to be subscribed as event handlers
    # on the EventBus: bus.subscribe(EventType, projection.on_...)

    def on_patient_registered(self, e):
        self._reports[self._key(e.occurred_at)].new_patients += 1

    def on_case_opened(self, e):
        self._reports[self._key(e.occurred_at)].cases_opened += 1

    def on_medication_prescribed(self, e):
        self._reports[self._key(e.occurred_at)].meds_prescribed += 1

    def get_report(self, year, month):
        """
        Query API for the read model.

        IMPLEMENTATION GUIDE:
        1) Return self._reports[(year, month)].
        2) Thanks to defaultdict, missing months return a zeroed MonthlyReport.
        3) Do not mutate the internal state here (read-only behavior).

        Why: Simple and predictable reporting API for CLI/tests.
        """
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

# add more unit tests here
```
