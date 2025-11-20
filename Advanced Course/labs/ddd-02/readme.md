# Hexagonal Architecture — ClinicCare (30-Minute Kata with TODOs)

> **Goal:** Give developers a small, **hands-on** slice of Hexagonal Architecture + DDD.
> You’ll wire **one use case**, **one domain event**, **one projection**, and **in-memory adapters** but several method bodies are **left for you to implement** (marked with `# TODO:`).
> Finish by completing the TODOs and running the demo/tests.

---

## 🎯 Scope (tiny on purpose)

* **Use Case:** `RegisterPatient`
* **Event:** `PatientRegistered`
* **Projection:** `MonthlyNewPatientsProjection` (counts new patients per month)
* **Adapters:** in-memory repository, in-memory event bus, system clock
* **Driver:** CLI demo

---

## 🗂️ Folder Structure

```
clinicare_hex_min/
  core/
    domain/
      patients.py
      events.py
      exceptions.py
    application/
      use_cases.py
    ports/
      repositories.py
      events.py
      clock.py
  adapters/
    driven/
      in_memory_repo.py
      in_memory_event_bus.py
      system_clock.py
      projection.py
    driver/
      cli_demo.py
  tests/
    test_min.py
```

---

## ✅ What You’ll Implement (TODO Map)

* `Patient.register(...)` → create entity + append `PatientRegistered` event.
* `InMemoryPatientRepository.get/save(...)` → basic dictionary store.
* `SimpleEventBus.subscribe/publish(...)` → minimal pub/sub by event type.
* `MonthlyNewPatientsProjection.on_patient_registered(...)` → increment monthly count.
* `RegisterPatient.__call__(...)` → orchestrate repo + event publication.
* (Test) Assertions already provided; they’ll pass when your TODOs are done.

---

## 💡 Minimal Reference Skeleton (with TODOs)

> Copy files as shown. Complete the TODOs where indicated.

### `core/domain/events.py`

```python
from dataclasses import dataclass
from datetime import datetime
import uuid

@dataclass(frozen=True)
class DomainEvent:
    id: str
    occurred_at: datetime

@dataclass(frozen=True)
class PatientRegistered(DomainEvent):
    patient_id: str

def new_event_id() -> str:
    # Provided for you (used when creating domain events)
    return str(uuid.uuid4())
```

### `core/domain/exceptions.py`

```python
class DomainError(Exception):
    pass
```

### `core/domain/patients.py`

```python
from dataclasses import dataclass, field
from datetime import date, datetime
from .exceptions import DomainError
from .events import PatientRegistered, new_event_id

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
    def register(cls, pid: str, name: str, dob: date, at: datetime) -> "Patient":
        """
        TODO:
        1) Create the Patient instance (Aggregate Root).
        2) Append a PatientRegistered event to _events with:
           - id = new_event_id()
           - occurred_at = at
           - patient_id = pid
        3) Return the created Patient.
        """
        # HINT:
        # p = cls(patient_id=PatientId(pid), name=name, date_of_birth=dob)
        # p._events.append(PatientRegistered(id=new_event_id(), occurred_at=at, patient_id=pid))
        # return p
        raise NotImplementedError("Implement Patient.register")

    def pull_events(self):
        ev, self._events = self._events, []
        return ev
```

### `core/ports/repositories.py`

```python
from typing import Protocol, Optional
from clinicare_hex_min.core.domain.patients import Patient, PatientId

class PatientRepository(Protocol):
    def get(self, pid: PatientId) -> Optional[Patient]: ...
    def save(self, patient: Patient) -> None: ...
```

### `core/ports/events.py`

```python
from typing import Protocol
from clinicare_hex_min.core.domain.events import DomainEvent

class EventPublisher(Protocol):
    def publish(self, event: DomainEvent) -> None: ...
```

### `core/ports/clock.py`

```python
from typing import Protocol
from datetime import datetime

class Clock(Protocol):
    def now(self) -> datetime: ...
```

### `core/application/use_cases.py`

```python
from datetime import date
from clinicare_hex_min.core.domain.patients import Patient, PatientId
from clinicare_hex_min.core.domain.exceptions import DomainError
from clinicare_hex_min.core.ports.repositories import PatientRepository
from clinicare_hex_min.core.ports.events import EventPublisher
from clinicare_hex_min.core.ports.clock import Clock

class RegisterPatient:
    def __init__(self, repo: PatientRepository, events: EventPublisher, clock: Clock):
        self.repo, self.events, self.clock = repo, events, clock

    def __call__(self, patient_id: str, name: str, dob: date):
        """
        TODO:
        1) If a patient with patient_id already exists (repo.get), raise DomainError("Patient already exists").
        2) Create a Patient via Patient.register(..., at=self.clock.now()).
        3) Save the patient via repo.save(...).
        4) Publish all events from patient.pull_events() via self.events.publish(e).
        5) Return the patient.
        """
        raise NotImplementedError("Implement RegisterPatient.__call__")
```

---

### `adapters/driven/in_memory_repo.py`

```python
from typing import Dict, Optional
from clinicare_hex_min.core.domain.patients import Patient, PatientId
from clinicare_hex_min.core.ports.repositories import PatientRepository

class InMemoryPatientRepository(PatientRepository):
    def __init__(self):
        # TODO: initialize a simple dict[str, Patient] store
        self._store: Dict[str, Patient] = {}  # OK to keep this line

    def get(self, pid: PatientId) -> Optional[Patient]:
        """
        TODO: return a patient by id from the in-memory store.
        HINT: key is pid.value
        """
        raise NotImplementedError("Implement InMemoryPatientRepository.get")

    def save(self, patient: Patient) -> None:
        """
        TODO: save/overwrite patient by id into the in-memory store.
        HINT: key is patient.patient_id.value
        """
        raise NotImplementedError("Implement InMemoryPatientRepository.save")
```

### `adapters/driven/in_memory_event_bus.py`

```python
from typing import Callable, Dict, List, Type
from clinicare_hex_min.core.domain.events import DomainEvent
from clinicare_hex_min.core.ports.events import EventPublisher

class SimpleEventBus(EventPublisher):
    def __init__(self):
        # maps event class -> list of handlers
        self._subs: Dict[Type[DomainEvent], List[Callable]] = {}

    def subscribe(self, event_type: Type[DomainEvent], handler: Callable[[DomainEvent], None]):
        """
        TODO:
        1) Add handler to the list for the event_type key in self._subs.
           Use setdefault to initialize the list.
        """
        raise NotImplementedError("Implement SimpleEventBus.subscribe")

    def publish(self, event: DomainEvent) -> None:
        """
        TODO:
        1) For each (etype, handlers) pair in self._subs, if isinstance(event, etype),
           call each handler(event).
        """
        raise NotImplementedError("Implement SimpleEventBus.publish")
```

### `adapters/driven/system_clock.py`

```python
from datetime import datetime, timezone
from clinicare_hex_min.core.ports.clock import Clock

class SystemClock(Clock):
    def now(self) -> datetime:
        # Provided for you
        return datetime.now(timezone.utc)
```

### `adapters/driven/projection.py`

```python
from collections import defaultdict
from dataclasses import dataclass
from clinicare_hex_min.core.domain.events import PatientRegistered

@dataclass
class MonthlyCount:
    new_patients: int = 0

class MonthlyNewPatientsProjection:
    def __init__(self):
        self._data = defaultdict(MonthlyCount)

    @staticmethod
    def _key(dt): return (dt.year, dt.month)

    def on_patient_registered(self, e: PatientRegistered):
        """
        TODO:
        1) Increment the MonthlyCount.new_patients for the e.occurred_at year/month.
        HINT:
            key = self._key(e.occurred_at)
            self._data[key].new_patients += 1
        """
        raise NotImplementedError("Implement MonthlyNewPatientsProjection.on_patient_registered")

    def count_for(self, year: int, month: int) -> int:
        return self._data[(year, month)].new_patients
```

---

### `adapters/driver/cli_demo.py`

```python
# After completing TODOs, run:
#   python -m clinicare_hex_min.adapters.driver.cli_demo
from datetime import date
from clinicare_hex_min.adapters.driven.in_memory_repo import InMemoryPatientRepository
from clinicare_hex_min.adapters.driven.in_memory_event_bus import SimpleEventBus
from clinicare_hex_min.adapters.driven.system_clock import SystemClock
from clinicare_hex_min.adapters.driven.projection import MonthlyNewPatientsProjection
from clinicare_hex_min.core.application.use_cases import RegisterPatient
from clinicare_hex_min.core.domain.events import PatientRegistered

def main():
    repo = InMemoryPatientRepository()
    bus = SimpleEventBus()
    clock = SystemClock()

    # Projection subscribes to the bus
    projection = MonthlyNewPatientsProjection()
    # TODO: Subscribe the projection handler to PatientRegistered events
    # HINT: bus.subscribe(PatientRegistered, projection.on_patient_registered)
    # Implement here:
    # --------------------------------
    # bus.subscribe(PatientRegistered, projection.on_patient_registered)
    # --------------------------------

    register = RegisterPatient(repo, bus, clock)
    register("p1", "Alice", date(1990, 5, 2))

    now = clock.now()
    print("New patients this month:", projection.count_for(now.year, now.month))

if __name__ == "__main__":
    main()
```

---

### `tests/test_min.py`

```python
# Run with: pytest -q
from datetime import date
from clinicare_hex_min.adapters.driven.in_memory_repo import InMemoryPatientRepository
from clinicare_hex_min.adapters.driven.in_memory_event_bus import SimpleEventBus
from clinicare_hex_min.adapters.driven.system_clock import SystemClock
from clinicare_hex_min.adapters.driven.projection import MonthlyNewPatientsProjection
from clinicare_hex_min.core.application.use_cases import RegisterPatient
from clinicare_hex_min.core.domain.events import PatientRegistered

def test_register_patient_increments_projection():
    repo, bus, clock = InMemoryPatientRepository(), SimpleEventBus(), SystemClock()
    proj = MonthlyNewPatientsProjection()
    bus.subscribe(PatientRegistered, proj.on_patient_registered)

    register = RegisterPatient(repo, bus, clock)
    register("p1", "Alice", date(1990, 5, 2))

    now = clock.now()
    assert proj.count_for(now.year, now.month) == 1
```

---

## 🧪 Acceptance Criteria

* Core has **no adapter imports**.
* `RegisterPatient`:

  * prevents duplicates,
  * creates `Patient` via domain method,
  * persists via repo,
  * publishes **exactly one** `PatientRegistered` event.
* Projection counts new patients per (year, month) only; **no PII**.
* CLI prints a non-zero count after registration.
* Test passes.

---

## 🚀 How to Run

1. Complete all `# TODO:` items.
2. Run the CLI:

   ```
   python -m clinicare_hex_min.adapters.driver.cli_demo
   ```

   Expected:

   ```
   New patients this month: 1
   ```
3. Run tests:

   ```
   pytest -q
   ```

   Expected:

   ```
   1 passed
   ```