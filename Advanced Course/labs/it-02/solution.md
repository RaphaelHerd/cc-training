# 🧪 Exercise: Top-Down Testing with **Bare-Minimum Manual Mocks**

## 🎯 Goal

Demonstrate **manual mocking** with the simplest possible setup.
No mocking frameworks, no logging, no extras — just tiny classes that return **static text** (or raise) so you can see the technique clearly.

---

## ☄️ Scenario (Super Simple)

We have a **MessageSender** that:

1. Asks a `FormatterService` to produce a message string from a template and data.
2. Asks a `TransportService` to send that message to a recipient and returns the `message_id`.

You’ll:

* Write **top-down tests first** using **manual mocks** (tiny classes with hardcoded behavior),
* Then implement the real `MessageSender` to satisfy the tests.

---

## 🧱 Interfaces

### `interfaces.py`

```python
# interfaces.py
from typing import Protocol, Mapping, Any

class FormatterService(Protocol):
    def format(self, template: str, data: Mapping[str, Any]) -> str: ...

class TransportService(Protocol):
    def send(self, recipient: str, message: str) -> str: ...
```

---

## 🔼 Tests (Top-Down, Manual Mocks with Static Behavior)

### `test_message_sender_minimal_manual.py`

```python
# test_message_sender_minimal_manual.py
# Run with: pytest -q --cov=. --cov-report=term-missing

import pytest
from typing import Mapping, Any
from interfaces import FormatterService, TransportService
from message_sender import MessageSender

# ------------------------
# Minimal manual mocks
# ------------------------

class StaticFormatter(FormatterService):
    """Always returns the same string regardless of inputs."""
    def __init__(self, text: str | Exception):
        self.text = text
    def format(self, template: str, data: Mapping[str, Any]) -> str:
        if isinstance(self.text, Exception):
            raise self.text
        return str(self.text)

class StaticTransport(TransportService):
    """Always returns the same message_id, ignores inputs."""
    def __init__(self, message_id: str | Exception):
        self.message_id = message_id
        self.last_call = None  # store last (recipient, message) for a tiny assertion if desired
    def send(self, recipient: str, message: str) -> str:
        self.last_call = (recipient, message)
        if isinstance(self.message_id, Exception):
            raise self.message_id
        return str(self.message_id)

# ------------------------
# Top-down tests
# ------------------------

def test_happy_path_uses_formatter_and_transport_returns_message_id():
    # Arrange: static doubles
    formatter = StaticFormatter("STATIC-MESSAGE")
    transport = StaticTransport("MSG-001")
    sender = MessageSender(formatter, transport)

    # Act
    result = sender.send_message("alice@example.com", "welcome", {"name": "ignored"})

    # Assert
    assert result == {"recipient": "alice@example.com", "message_id": "MSG-001"}
    # (Optional tiny check that transport got the exact static message)
    assert transport.last_call == ("alice@example.com", "STATIC-MESSAGE")

def test_formatter_failure_prevents_sending():
    # Arrange: formatter throws, transport would succeed (but must not be called)
    formatter = StaticFormatter(RuntimeError("boom"))
    transport = StaticTransport("MSG-IGNORED")
    sender = MessageSender(formatter, transport)

    # Act / Assert
    with pytest.raises(RuntimeError):
        sender.send_message("bob@example.com", "any", {})

    # Since we keep mocks minimal, we only check that last_call is still None
    assert transport.last_call is None
```

---

## ✅ Implementation (driven by tests)

### `message_sender.py`

```python
# message_sender.py
from typing import Mapping, Any
from interfaces import FormatterService, TransportService

class MessageSender:
    """
    Minimal orchestrator: format then send. Manual mocks in tests provide static behavior.
    """
    def __init__(self, formatter: FormatterService, transport: TransportService):
        self._formatter = formatter
        self._transport = transport

    def send_message(self, recipient: str, template: str, data: Mapping[str, Any]):
        message = self._formatter.format(template, data)
        message_id = self._transport.send(recipient, message)
        return {"recipient": recipient, "message_id": message_id}
```

---

## ▶️ How to Run

```bash
pip install -r requirements.txt
pytest -q --cov=. --cov-report=term-missing
```

Expected output (abbreviated):

```
..                                                                  [100%]
----------- coverage: platform ... -----------
Name                                 Stmts   Miss  Cover
--------------------------------------------------------
interfaces.py                            5      0   100%
message_sender.py                        9      0   100%
test_message_sender_minimal_manual.py   39      0   100%
```

---

## 📦 requirements.txt

```txt
pytest>=7.0
pytest-cov>=4.0
```