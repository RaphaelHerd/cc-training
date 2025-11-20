# 🧪 Exercise: Top-Down Unit Testing - Drive Design with Mocks

## 🎯 Goal

Practice **top-down unit testing** by:

* Writing high-level tests **first** against a coordinating component,
* **Mocking** lower-level services that are not ready yet,
* Driving the design of collaborator interfaces via tests,
* Keeping tests **fast, automated, and measurable**.

---

## ☄️ Fictional Use Case

A minimal **Checkout Orchestrator** coordinates three services:

* `PricingService`: computes a cart **subtotal** from line items.
* `InventoryService`: **reserves** stock for the requested items.
* `PaymentGateway`: **charges** the customer and returns a `payment_id`.

Your job: implement `CheckoutOrchestrator` top-down.
Start by testing the orchestrator’s behavior while **mocking** the three collaborators (not implemented yet). Only after the orchestrator’s tests pass, add tiny stub implementations to make the module importable (no real logic needed).

---

## 🧩 Your Task

1. Define collaborator **interfaces** (types / protocols).
2. Write **top-down unit tests** for `CheckoutOrchestrator` using **mocks** for collaborators:

   * Happy path: pricing → inventory → payment (in that order).
   * Inventory failure: payment is **not** invoked.
   * Payment failure: inventory reservation is **not** leaked (verify orchestrator raises).
3. Implement `CheckoutOrchestrator` to satisfy those tests.
4. Provide minimal placeholder implementations of collaborators (no logic).
5. Run tests with coverage.

---

## 🧱 Interfaces (Collaborator Contracts)

### `interfaces.py`

```python
# interfaces.py
from dataclasses import dataclass
from typing import Protocol, Iterable

@dataclass(frozen=True)
class LineItem:
    sku: str
    unit_price: float
    qty: int

class PricingService(Protocol):
    def compute_subtotal(self, items: Iterable[LineItem]) -> float: ...

class InventoryService(Protocol):
    def reserve(self, items: Iterable[LineItem]) -> None: ...

class PaymentGateway(Protocol):
    def charge(self, amount: float) -> str: ...

@dataclass(frozen=True)
class Receipt:
    subtotal: float
    payment_id: str
```

---

## 🔼 Top-Down Tests (Mocks first)

### `test_checkout_orchestrator_topdown.py`

```python
# test_checkout_orchestrator_topdown.py
# Run with: pytest -q --cov=. --cov-report=term-missing

import pytest
from unittest.mock import Mock, call

from interfaces import LineItem, Receipt
from orchestrator import CheckoutOrchestrator

def test_happy_path_calls_services_in_order_and_returns_receipt():
    # Arrange
    items = [LineItem("A", 10.0, 2), LineItem("B", 5.0, 1)]
    pricing = Mock()
    inventory = Mock()
    payment = Mock()

    pricing.compute_subtotal.return_value = 25.0
    payment.charge.return_value = "PAY-123"

    # System under test
    sut = CheckoutOrchestrator(pricing=pricing, inventory=inventory, payment=payment)

    # Act
    receipt = sut.checkout(items)

    # Assert (output)
    assert isinstance(receipt, Receipt)
    assert receipt.subtotal == 25.0
    assert receipt.payment_id == "PAY-123"

    # Assert (interaction)
    pricing.compute_subtotal.assert_called_once_with(items)
    inventory.reserve.assert_called_once_with(items)
    payment.charge.assert_called_once_with(25.0)

    # Optional: coarse call ordering
    assert pricing.method_calls[0] == call.compute_subtotal(items)
    assert inventory.method_calls[0] == call.reserve(items)
    assert payment.method_calls[0] == call.charge(25.0)


def test_inventory_failure_prevents_payment():
    # Arrange
    items = [LineItem("X", 3.0, 10)]
    pricing = Mock()
    inventory = Mock()
    payment = Mock()

    pricing.compute_subtotal.return_value = 30.0
    inventory.reserve.side_effect = RuntimeError("no stock")

    sut = CheckoutOrchestrator(pricing, inventory, payment)

    # Act / Assert
    with pytest.raises(RuntimeError):
        sut.checkout(items)

    # Payment must not be attempted
    payment.charge.assert_not_called()


def test_payment_failure_bubbles_up():
    # Arrange
    items = [LineItem("C", 12.0, 1)]
    pricing = Mock()
    inventory = Mock()
    payment = Mock()

    pricing.compute_subtotal.return_value = 12.0
    payment.charge.side_effect = RuntimeError("declined")

    sut = CheckoutOrchestrator(pricing, inventory, payment)

    # Act / Assert
    with pytest.raises(RuntimeError):
        sut.checkout(items)

    # Inventory reserve was performed before payment attempt
    inventory.reserve.assert_called_once_with(items)
```

> These tests **define** how the orchestrator should behave and interact, even though collaborators aren’t implemented yet.

---

## ✅ Orchestrator Implementation (driven by tests)

### `orchestrator.py`

```python
# orchestrator.py
from typing import Iterable
from interfaces import LineItem, PricingService, InventoryService, PaymentGateway, Receipt

class CheckoutOrchestrator:
    """
    Top-down: Orchestrates the checkout flow by calling collaborators.
    Leaves are mocked in unit tests; this class holds the real coordination logic.
    """
    def __init__(self, pricing: PricingService, inventory: InventoryService, payment: PaymentGateway) -> None:
        self._pricing = pricing
        self._inventory = inventory
        self._payment = payment

    def checkout(self, items: Iterable[LineItem]) -> Receipt:
        subtotal = self._pricing.compute_subtotal(items)
        self._inventory.reserve(items)
        payment_id = self._payment.charge(subtotal)
        return Receipt(subtotal=subtotal, payment_id=payment_id)
```

---

## 🧰 Minimal Placeholders (not used by the top-down tests)

> These exist only to make the repository importable and to clarify interfaces.
> They are **not** exercised by the top-down unit tests (which use mocks).

### `pricing_impl.py`

```python
# pricing_impl.py
from typing import Iterable
from interfaces import LineItem, PricingService

class SimplePricing(PricingService):  # type: ignore[misc]
    def compute_subtotal(self, items: Iterable[LineItem]) -> float:
        # Placeholder: naïve sum; real logic can come later.
        return round(sum(it.unit_price * it.qty for it in items), 2)
```

### `inventory_impl.py`

```python
# inventory_impl.py
from typing import Iterable
from interfaces import LineItem, InventoryService

class NoopInventory(InventoryService):  # type: ignore[misc]
    def reserve(self, items: Iterable[LineItem]) -> None:
        # Placeholder: does nothing (assumes stock exists).
        return None
```

### `payment_impl.py`

```python
# payment_impl.py
from interfaces import PaymentGateway

class DummyPayment(PaymentGateway):  # type: ignore[misc]
    def charge(self, amount: float) -> str:
        # Placeholder: returns a static id
        return "DUMMY-PAY"
```

---

## 🧠 Why This Is Top-Down

* Tests were written **at the top** (orchestrator) **before** lower services existed.
* Collaborators were **mocked**, letting you specify orchestration behavior early.
* Interfaces and method shapes were **discovered by tests** (design by tests).
* Later, concrete implementations can replace mocks without changing the orchestrator tests.

---

## ▶️ How to Run (with Coverage)

```bash
pip install -r requirements.txt
pytest -q --cov=. --cov-report=term-missing
```

Expected (abbreviated):

```
...                                                                [100%]
----------- coverage: platform ... -----------
Name                             Stmts   Miss  Cover   Missing
--------------------------------------------------------------
interfaces.py                       11      0   100%
orchestrator.py                     14      0   100%
test_checkout_orchestrator_topdown.py
                                    45      0   100%
...
```

---

## 📦 requirements.txt

```txt
# requirements.txt

pytest>=7.0
pytest-cov>=4.0
```

*(Mocks are from Python’s standard library `unittest.mock`, so no extra deps.)*
