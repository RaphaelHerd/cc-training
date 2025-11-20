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