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

