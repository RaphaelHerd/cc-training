# 🧪 TDD Exercise: Order Total Calculator

**Goal:** Practice the TDD cycle.
You’ll create a small function that calculates the total cost of an order with discounts and taxes.

---

## Feature (Specification)

Implement:

```python
def calculate_order_total(items: list[dict], discount_rate: float = 0.0, tax_rate: float = 0.0) -> float:
    """
    Calculates the total order cost after applying discount and tax.

    Each item is a dictionary like:
      {"name": "Book", "price": 12.99, "quantity": 2}

    Rules:
      - The subtotal = sum(price * quantity) for all items.
      - discount_rate is a percentage between 0 and 1 (e.g. 0.1 = 10%).
      - tax_rate is a percentage between 0 and 1 (e.g. 0.2 = 20%).
      - Apply discount first, then tax.
      - Round the final total to two decimals.
      - Raise ValueError if any price, quantity, or rate is negative.
    """
```

---

## Project Layout

```
order_total_tdd/
├─ order_total.py             # implementation (Green)
└─ test_order_total.py        # console tests (Red → Green → Refactor)
```

---

## 1️⃣ Write Tests First (RED)

Create `test_order_total.py`:

```python
# test_order_total.py
# Run: python test_order_total.py
from order_total import calculate_order_total

def assert_equal(actual, expected, label):
    if abs(actual - expected) < 1e-2:
        print(f"[PASS] {label}")
        return True
    print(f"[FAIL] {label}: expected {expected:.2f}, got {actual:.2f}")
    return False

def run_tests():
    ok = True

    # 1. basic subtotal
    items = [{"name": "Pen", "price": 2.0, "quantity": 3}]
    ok &= assert_equal(calculate_order_total(items), 6.00, "single item")

    # 2. multiple items
    items = [
        {"name": "Book", "price": 10.0, "quantity": 2},
        {"name": "Notebook", "price": 5.0, "quantity": 1},
    ]
    ok &= assert_equal(calculate_order_total(items), 25.00, "multiple items")

    # 3. discount
    ok &= assert_equal(calculate_order_total(items, discount_rate=0.1), 22.50, "10% discount")

    # 4. discount + tax (apply discount first)
    ok &= assert_equal(calculate_order_total(items, discount_rate=0.1, tax_rate=0.2), 27.00, "discount + tax")

    # 5. invalid input
    try:
        calculate_order_total([{"name": "Bad", "price": -1.0, "quantity": 1}])
        print("[FAIL] negative price: expected ValueError")
        ok = False
    except ValueError:
        print("[PASS] negative price")

    print("\nSummary:", "PASS" if ok else "FAIL")
    return ok

if __name__ == "__main__":
    import sys
    sys.exit(0 if run_tests() else 1)
```

Run it — it should fail (**Red**) because `calculate_order_total` doesn’t exist yet.

---

## 2️⃣ Implement Minimum to Pass (GREEN)

Create `order_total.py`:

```python
# order_total.py

def calculate_order_total(items: list[dict], discount_rate: float = 0.0, tax_rate: float = 0.0) -> float:
    if discount_rate < 0 or tax_rate < 0:
        raise ValueError("Rates cannot be negative")

    subtotal = 0.0
    for item in items:
        price = item.get("price", 0)
        qty = item.get("quantity", 0)

        if price < 0 or qty < 0:
            raise ValueError("Price and quantity must be non-negative")

        subtotal += price * qty

    discounted = subtotal * (1 - discount_rate)
    taxed = discounted * (1 + tax_rate)

    return round(taxed, 2)
```

Re-run the tests — all should now pass (**Green**).

---

## 3️⃣ Refactor (While Keeping Tests Green)

Possible improvements:

* Extract subtotal calculation into a helper.
* Validate inputs more explicitly.
* Add type hints and docstrings.

```python
# order_total.py (refactored example)

def calculate_order_total(items: list[dict], discount_rate: float = 0.0, tax_rate: float = 0.0) -> float:
    _validate_rates(discount_rate, tax_rate)
    subtotal = _calculate_subtotal(items)
    total = subtotal * (1 - discount_rate)
    total *= (1 + tax_rate)
    return round(total, 2)

def _calculate_subtotal(items: list[dict]) -> float:
    subtotal = 0.0
    for item in items:
        price = item.get("price", 0)
        qty = item.get("quantity", 0)
        if price < 0 or qty < 0:
            raise ValueError("Negative price or quantity not allowed")
        subtotal += price * qty
    return subtotal

def _validate_rates(discount_rate: float, tax_rate: float):
    if not (0 <= discount_rate <= 1 and 0 <= tax_rate <= 1):
        raise ValueError("Rates must be between 0 and 1 inclusive")
```

Run the tests again — if still green, you’ve completed the TDD loop.

---

## ✅ Learning Goals

| Step         | Description                                                    |
| ------------ | -------------------------------------------------------------- |
| **Red**      | Write a small test describing expected behavior before coding. |
| **Green**    | Implement the simplest code that makes the test pass.          |
| **Refactor** | Clean up code while keeping tests passing.                     |
| **Repeat**   | Extend behavior one small test at a time.                      |

---

Run from console:

```bash
python test_order_total.py
```

Example output:

```
[PASS] single item
[PASS] multiple items
[PASS] 10% discount
[PASS] discount + tax
[PASS] negative price
Summary: PASS
```
