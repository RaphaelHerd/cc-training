# 🧪 Exercise: Bad Unit Tests (Not Independent) - Diagnose & Refactor

## 🎯 Goal

Learn to identify **test interdependence** (tests that pass only when run in a certain order due to shared state), then **refactor** both code and tests to make them **isolated and deterministic**.

---

## 🔎 Description (What’s wrong here?)

Below is a **bad example**: business logic uses **module-level global state**, and the tests **rely on previous tests** to set up that state. These tests appear to pass when run together in a specific order, but will **flake** if executed individually or in random order.

---

## ❌ Bad Implementation + Non-Independent Tests

### `shopping_cart.py` (bad)

```python
# shopping_cart.py
# Global mutable state (anti-pattern for testability)
_items = []

def add_item(name: str, price: float) -> None:
    if price < 0:
        raise ValueError("price must be non-negative")
    _items.append({"name": name, "price": float(price)})

def total() -> float:
    return round(sum(i["price"] for i in _items), 2)
```

### `test_shopping_cart_bad.py` (bad)

```python
# test_shopping_cart_bad.py
# These tests depend on each other (hidden order dependency).

from shopping_cart import add_item, total

def test_adds_first_item():
    # Assumes clean state — passes if this runs first
    add_item("Book", 10.00)
    assert total() == 10.00

def test_accumulates_across_tests():
    # RELIES on test_adds_first_item having already added "Book"
    add_item("Pen", 2.00)
    assert total() == 12.00   # Fails if run in isolation!

def test_more_items_changes_total():
    # RELIES on both previous tests
    add_item("Notebook", 5.00)
    assert total() == 17.00   # Fails if test order changes
```

> Try running a single test (e.g., `pytest -q test_shopping_cart_bad.py::test_accumulates_across_tests`). It **fails** because it depends on a prior test’s side effects.

---

## 🧩 Your Task

1. **Find the smells**

   * Global mutable state used by production code (`_items`).
   * Tests that rely on previous tests to mutate that shared state.
   * Hidden coupling to execution order.

2. **Refactor goals**

   * Make business logic **stateless** or encapsulate state in an **instance**.
   * Ensure each test creates its **own fresh state**.
   * Use the **Arrange–Act–Assert** testing pattern.
   * Tests must pass **individually** and in **any order**.

3. **Deliverables**

   * A refactored test file with **independent** tests.

---

## ✅ Solution A (Recommended): Encapsulate State in a Class

### `shopping_cart_ref.py` (good)

```python
# shopping_cart_ref.py

from dataclasses import dataclass

@dataclass(frozen=True)
class Item:
    name: str
    price: float

class ShoppingCart:
    def __init__(self) -> None:
        self._items: list[Item] = []

    def add_item(self, name: str, price: float) -> None:
        if price < 0:
            raise ValueError("price must be non-negative")
        self._items.append(Item(name=name, price=float(price)))

    def total(self) -> float:
        return round(sum(i.price for i in self._items), 2)

    def __len__(self) -> int:
        return len(self._items)
```

### `test_shopping_cart_ref.py` (good; independent, AAA)

```python
# test_shopping_cart_ref.py

from shopping_cart_ref import ShoppingCart

def test_adds_single_item_and_totals():
    # Arrange
    cart = ShoppingCart()

    # Act
    cart.add_item("Book", 10.00)
    amount = cart.total()

    # Assert
    assert len(cart) == 1
    assert amount == 10.00


def test_adding_multiple_items_isolated_from_other_tests():
    # Arrange
    cart = ShoppingCart()

    # Act
    cart.add_item("Book", 10.00)
    cart.add_item("Pen", 2.00)
    cart.add_item("Notebook", 5.00)
    amount = cart.total()

    # Assert
    assert len(cart) == 3
    assert amount == 17.00


def test_rejects_negative_price():
    # Arrange
    cart = ShoppingCart()

    # Act / Assert
    try:
        cart.add_item("Bad", -1.0)
        raised = False
    except ValueError:
        raised = True

    assert raised is True
```

**Why this fixes it**

* Each test constructs a **fresh `ShoppingCart`** instance (no shared state).
* Running any test alone yields the same result as running the entire suite.
* The Arrange–Act–Assert pattern clarifies intention and phases.

---

## ✅ Solution B (Alternative): Keep Module Functions but Reset State per Test

If you must keep the module-level API, add a **reset hook** and use a fixture to clear state before each test.

### `shopping_cart_modular.py` (improved but with reset)

```python
# shopping_cart_modular.py
_items = []

def reset() -> None:
    """Test-only helper to clear module state."""
    _items.clear()

def add_item(name: str, price: float) -> None:
    if price < 0:
        raise ValueError("price must be non-negative")
    _items.append({"name": name, "price": float(price)})

def total() -> float:
    return round(sum(i["price"] for i in _items), 2)
```

### `test_shopping_cart_modular.py` (independent via per-test reset)

```python
# test_shopping_cart_modular.py

import pytest
from shopping_cart_modular import add_item, total, reset

@pytest.fixture(autouse=True)
def _clear_state():
    # Arrange (environment): ensure clean slate before each test
    reset()

def test_adds_first_item_is_independent():
    # Act
    add_item("Book", 10.00)

    # Assert
    assert total() == 10.00

def test_accumulates_only_current_test_items():
    # Act
    add_item("Pen", 2.00)
    add_item("Notebook", 5.00)

    # Assert
    assert total() == 7.00
```

**Trade-offs**

* Still uses **global state**, but tests are isolated through **automatic reset**.
* Prefer **Solution A** for better design and testability.

---

## 🧠 Refactoring Checklist

* [ ] No **global mutable state** in production code (or reliably reset between tests).
* [ ] Each test **creates its own subject** (instance or fresh state).
* [ ] Tests follow **Arrange–Act–Assert**.
* [ ] Tests **do not depend** on execution order or prior side effects.
* [ ] Running any test **in isolation** yields the same result as running the suite.

---

## ▶️ How to Run

```bash
# Run bad example (observe flakiness if you select tests individually)
pytest -q test_shopping_cart_bad.py

# Run good examples
pytest -q test_shopping_cart_ref.py
pytest -q test_shopping_cart_modular.py
```

> Tip: Add `-k` to select individual tests and verify independence, e.g.
> `pytest -q test_shopping_cart_bad.py -k accumulates_across_tests`
