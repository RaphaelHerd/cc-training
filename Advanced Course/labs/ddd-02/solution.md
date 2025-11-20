# Hexagonal Architecture — ClinicCare (Ultra-Minimal, 30-Minute Kata)

> **Context:** Starting from your DDD prototype, refactor to a **tiny hexagonal slice**.
> You’ll implement **one use case**, **one domain event**, **one projection**, and **in-memory adapters**.
> The goal is to finish in ~30 minutes with clean boundaries and runnable code.

---

## 🎯 Scope (intentionally tiny)

* **Single Use Case:** `RegisterPatient`
* **Single Event:** `PatientRegistered`
* **Single Projection:** `MonthlyNewPatientsProjection` (counts new patients per month)
* **In-Memory Adapters:** patient repo, event bus, system clock
* **CLI Demo:** end-to-end run

---

## 🗂️ Folder Structure (copy/paste friendly)

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

## ✅ Acceptance Criteria

* Core (domain + application + ports) has **no** imports from adapters.
* `RegisterPatient` publishes one `PatientRegistered` event.
* Projection counts **monthly** new patients (no PII).
* CLI prints the count for **this month**.

---

## 💡 Minimal Reference Code

> Paste files as shown. These are deliberately short and dependency-free (besides `pytest` for the test).

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
        p = cls(patient_id=PatientId(pid), name=name, date_of_birth=dob)
        p._events.append(PatientRegistered(id=new_event_id(), occurred_at=at, patient_id=pid))
        return p

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
        if self.repo.get(PatientId(patient_id)):
            raise DomainError("Patient already exists")
        p = Patient.register(patient_id, name, dob, at=self.clock.now())
        self.repo.save(p)
        for e in p.pull_events():
            self.events.publish(e)
        return p
```

---

### `adapters/driven/in_memory_repo.py`

```python
from typing import Dict, Optional
from clinicare_hex_min.core.domain.patients import Patient, PatientId
from clinicare_hex_min.core.ports.repositories import PatientRepository

class InMemoryPatientRepository(PatientRepository):
    def __init__(self):
        self._store: Dict[str, Patient] = {}

    def get(self, pid: PatientId) -> Optional[Patient]:
        return self._store.get(pid.value)

    def save(self, patient: Patient) -> None:
        self._store[patient.patient_id.value] = patient
```

### `adapters/driven/in_memory_event_bus.py`

```python
from typing import Callable, Dict, List, Type
from clinicare_hex_min.core.domain.events import DomainEvent
from clinicare_hex_min.core.ports.events import EventPublisher

class SimpleEventBus(EventPublisher):
    def __init__(self):
        self._subs: Dict[Type[DomainEvent], List[Callable]] = {}

    def subscribe(self, event_type: Type[DomainEvent], handler: Callable[[DomainEvent], None]):
        self._subs.setdefault(event_type, []).append(handler)

    def publish(self, event: DomainEvent) -> None:
        for et, hs in self._subs.items():
            if isinstance(event, et):
                for h in hs:
                    h(event)
```

### `adapters/driven/system_clock.py`

```python
from datetime import datetime, timezone
from clinicare_hex_min.core.ports.clock import Clock

class SystemClock(Clock):
    def now(self) -> datetime:
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
        self._data[self._key(e.occurred_at)].new_patients += 1

    def count_for(self, year: int, month: int) -> int:
        return self._data[(year, month)].new_patients
```

---

### `adapters/driver/cli_demo.py`

```python
# Minimal wiring demo: register one patient, print this month's count.
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

    projection = MonthlyNewPatientsProjection()
    bus.subscribe(PatientRegistered, projection.on_patient_registered)

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

## 🚀 Run It

```bash
# from the project root
python -m clinicare_hex_min.adapters.driver.cli_demo
# -> New patients this month: 1

pytest -q
# -> 1 passed
```

---

## 📝 What You’ve Practiced

* **Hexagonal boundary** via `Ports` (`Repository`, `EventPublisher`, `Clock`)
* **One event** published from the domain, consumed by a **projection**
* **Adapters** are swappable; the core is framework-agnostic

> This single file contains everything you need to copy into your lab and complete the kata in ~30 minutes.
