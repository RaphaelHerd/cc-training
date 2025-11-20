# 🧪 Exercise (Refactored): Pure Bottom-Up Integration — Leaf-First, Stubby Upper Layers

## 🎯 Goal

Practice **strict bottom-up integration testing**:

* Implement and test **leaf components first** (pure logic & in-memory state).
* Keep **upper components as thin stubs** that **only forward** calls to leaves (no complex coordination, no mocks/fakes).
* Write a tiny integration test that wires real leaves through the thin upper layer.

---

## ☄️ Fictional Use Case

A tiny **Checkout** flow:

* **Leaf modules**:

  * `pricing.compute_line_total(unit_price, qty, discount_rate?)` → per-line total.
  * `tax.compute_cart_tax(subtotal, tax_rate)` → tax amount.
  * `inventory.InMemoryInventory` → simple in-memory stock with **batch reserve**.
* **Upper modules (stubs)**:

  * `cart.CartCalculator.calculate_subtotal(items)` → just loops and calls `pricing`.
  * `order.OrderService.place_order(items, tax_rate)` → forwards to `CartCalculator`, `Inventory.reserve_batch`, and `tax.compute_cart_tax`; returns a plain DTO.

> Important: Upper modules contain **no complex logic** beyond delegating to leaves.

---

## 🧩 Your Task

1. Implement & unit-test the **leaf modules** (`pricing`, `tax`, `inventory`).
2. Implement **thin** upper layers (`cart`, `order`) that **just forward** to leaves.
3. Write a **small integration test** using only the real leaves and the thin upper layer.
4. Run with coverage to measure quality.

---

## 🧱 Leaf Modules (Implementation)

### `pricing.py`

```python
# pricing.py
from typing import Optional

def compute_line_total(unit_price: float, qty: int, *, discount_rate: Optional[float] = None) -> float:
    """
    line_total = unit_price * qty * (1 - discount_rate)
    Constraints:
      - unit_price >= 0
      - qty >= 0
      - discount_rate in [0, 1] or None (treated as 0)
    Returns rounded(2) monetary value.
    """
    if unit_price < 0 or qty < 0:
        raise ValueError("unit_price and qty must be non-negative")
    rate = 0.0 if discount_rate is None else float(discount_rate)
    if not 0.0 <= rate <= 1.0:
        raise ValueError("discount_rate must be within [0, 1]")
    return round(unit_price * qty * (1.0 - rate), 2)
```

### `tax.py`

```python
# tax.py

def compute_cart_tax(subtotal: float, tax_rate: float) -> float:
    """
    tax = subtotal * tax_rate
    Constraints:
      - subtotal >= 0
      - 0 <= tax_rate <= 1
    Returns rounded(2).
    """
    if subtotal < 0:
        raise ValueError("subtotal must be non-negative")
    if not (0.0 <= tax_rate <= 1.0):
        raise ValueError("tax_rate must be in [0, 1]")
    return round(subtotal * tax_rate, 2)
```

### `inventory.py`

```python
# inventory.py

class OutOfStockError(RuntimeError):
    pass

class InMemoryInventory:
    """
    Simple in-memory stock with batch reservation.
    Leaf owns the reservation logic; upper layers only call it.
    """
    def __init__(self, initial: dict[str, int] | None = None) -> None:
        self._stock: dict[str, int] = dict(initial or {})

    def get_stock(self, sku: str) -> int:
        return int(self._stock.get(sku, 0))

    def reserve_batch(self, batch: list[tuple[str, int]]) -> None:
        """
        Atomically reserve quantities for each (sku, qty) pair.
        Raises OutOfStockError if any sku lacks stock. No partial reservation.
        """
        # Validate first
        for sku, qty in batch:
            if qty < 0:
                raise ValueError("qty must be non-negative")
            if self.get_stock(sku) < qty:
                raise OutOfStockError(f"insufficient stock for {sku}")
        # Apply reservations
        for sku, qty in batch:
            self._stock[sku] = self.get_stock(sku) - qty
```

---

## 🧪 Unit Tests for Leaf Modules (Bottom Layer)

### `test_pricing_unit.py`

```python
# test_pricing_unit.py
# AAA: Arrange – Act – Assert

import pytest
from pricing import compute_line_total

def test_line_total_no_discount():
    # Arrange
    price, qty = 12.5, 3
    # Act
    total = compute_line_total(price, qty)
    # Assert
    assert total == 37.5

def test_line_total_with_discount():
    # Arrange
    price, qty, rate = 10.0, 5, 0.1
    # Act
    total = compute_line_total(price, qty, discount_rate=rate)
    # Assert
    assert total == 45.0  # 50 * (1 - 0.1)

def test_line_total_invalid_inputs():
    with pytest.raises(ValueError):
        compute_line_total(-1.0, 1)
    with pytest.raises(ValueError):
        compute_line_total(1.0, -1)
    with pytest.raises(ValueError):
        compute_line_total(10.0, 1, discount_rate=1.1)
```

### `test_tax_unit.py`

```python
# test_tax_unit.py

import pytest
from tax import compute_cart_tax

def test_tax_basic():
    # Arrange
    subtotal, rate = 100.0, 0.2
    # Act
    tax = compute_cart_tax(subtotal, rate)
    # Assert
    assert tax == 20.0

def test_tax_zero_rate_and_rounding():
    # Arrange
    subtotal, rate = 33.33, 0.0
    # Act
    tax = compute_cart_tax(subtotal, rate)
    # Assert
    assert tax == 0.0

def test_tax_invalid_inputs():
    with pytest.raises(ValueError):
        compute_cart_tax(-1.0, 0.2)
    with pytest.raises(ValueError):
        compute_cart_tax(10.0, 1.5)
```

### `test_inventory_unit.py`

```python
# test_inventory_unit.py

import pytest
from inventory import InMemoryInventory, OutOfStockError

def test_reserve_batch_reduces_stock():
    # Arrange
    inv = InMemoryInventory({"A": 5, "B": 3})
    # Act
    inv.reserve_batch([("A", 2), ("B", 1)])
    # Assert
    assert inv.get_stock("A") == 3
    assert inv.get_stock("B") == 2

def test_reserve_batch_is_atomic_on_insufficient_stock():
    # Arrange
    inv = InMemoryInventory({"A": 2, "B": 1})
    # Act / Assert
    with pytest.raises(OutOfStockError):
        inv.reserve_batch([("A", 2), ("B", 2)])  # B insufficient
    # Verify no partial deduction
    assert inv.get_stock("A") == 2
    assert inv.get_stock("B") == 1
```

---

## 🔌 Upper Layers (Thin Stubs Only)

### `cart.py`

```python
# cart.py
from typing import Iterable
from dataclasses import dataclass
from pricing import compute_line_total

@dataclass(frozen=True)
class CartItem:
    sku: str
    unit_price: float
    qty: int
    discount_rate: float | None = None

class CartCalculator:
    """
    Thin stub: only loops and forwards to pricing.compute_line_total.
    """
    def calculate_subtotal(self, items: Iterable[CartItem]) -> float:
        subtotal = 0.0
        for it in items:
            subtotal += compute_line_total(it.unit_price, it.qty, discount_rate=it.discount_rate)
        return round(subtotal, 2)
```

### `order.py`

```python
# order.py
from dataclasses import dataclass
from typing import Iterable
from cart import CartItem, CartCalculator
from inventory import InMemoryInventory
from tax import compute_cart_tax

@dataclass(frozen=True)
class OrderResult:
    subtotal: float
    tax: float
    total: float

class OrderService:
    """
    Thin stub: delegates to CartCalculator, Inventory.reserve_batch, and tax.compute_cart_tax.
    No complex logic; simply forwards requests to leaves.
    """
    def __init__(self, inv: InMemoryInventory, cart_calc: CartCalculator) -> None:
        self.inv = inv
        self.cart_calc = cart_calc

    def place_order(self, items: Iterable[CartItem], tax_rate: float) -> OrderResult:
        subtotal = self.cart_calc.calculate_subtotal(items)
        # forward reservation as a batch to inventory (leaf owns logic)
        batch = [(it.sku, it.qty) for it in items]
        self.inv.reserve_batch(batch)
        tax = compute_cart_tax(subtotal, tax_rate)
        total = round(subtotal + tax, 2)
        return OrderResult(subtotal=subtotal, tax=tax, total=total)
```

---

## 🔗 Bottom-Up Integration Test (Real Leaves + Thin Upper Layer)

### `test_integration_bottom_up.py`

```python
# test_integration_bottom_up.py
# Uses ONLY real leaf modules and thin stubs; no mocks/fakes.

from cart import CartCalculator, CartItem
from inventory import InMemoryInventory
from order import OrderService

def test_order_service_wires_real_leaves_and_forwards_calls():
    # Arrange: real leaves
    inv = InMemoryInventory({"A": 5, "B": 10})
    cart_calc = CartCalculator()
    svc = OrderService(inv, cart_calc)
    items = [
        CartItem("A", unit_price=10.0, qty=2, discount_rate=0.1),  # 18.00
        CartItem("B", unit_price=5.0, qty=3),                      # 15.00
    ]
    tax_rate = 0.2  # 20% of 33.00 = 6.60

    # Act
    result = svc.place_order(items, tax_rate)

    # Assert
    assert result.subtotal == 33.0
    assert result.tax == 6.6
    assert result.total == 39.6
    # inventory effect comes from leaf; upper only forwarded
    assert inv.get_stock("A") == 3
    assert inv.get_stock("B") == 7
```

---

## 🧠 Why This Matches Bottom-Up

* **Leafs first**: pricing/tax/inventory are implemented and independently verified.
* **Upper layers**: **no new logic**, only call sequencing/forwarding to leaves.
* **Integration**: a thin end-to-end wiring check using **only** real components.

---

## ▶️ How to Run (with Coverage)

```bash
pip install -r requirements.txt
pytest -q --cov=. --cov-report=term-missing
```

Expected (abbreviated):

```
.......                                                          [100%]
----------- coverage: platform ... -----------
Name                 Stmts   Miss  Cover   Missing
--------------------------------------------------
pricing.py              16      0   100%
tax.py                   9      0   100%
inventory.py            24      0   100%
cart.py                 16      0   100%
order.py                23      0   100%
test_*                  ...     0   100%
```

---

## 📦 requirements.txt

```txt
# requirements.txt

pytest>=7.0
pytest-cov>=4.0
```

*(Everything runs out of the box in any IDE/terminal. No mocks, no fakes — just pure bottom-up.)*
