# 🧪 Boundary Testing Exercise

## Objective

Learn how to identify and test **input boundaries** of a function based on its **specification**, not its implementation.
The focus is on analyzing limits, edge cases, and invalid input ranges.

---

## Function Specification

You are given the following function signature and description.
You **must not** look at its implementation. Design your tests purely from the interface and rules.

```python
def calculate_discount(price: float, customer_age: int, is_member: bool) -> float:
    """
    Calculates a final price after applying possible discounts.

    Rules:
      - Price must be between 0 and 1000 (inclusive).
      - Age must be between 0 and 120 (inclusive).
      - Members get an extra 10% discount.
      - Seniors (age >= 65) get an additional 5% discount.
      - The final price can never go below 0.

    Returns:
        The discounted price as a float.
    Raises:
        ValueError: If input values are out of valid ranges.
    """
```

---

## Task Steps

1. **Analyze the specification**

   * Identify which input parameters have **numeric limits**.
   * Note where discount rules **change behavior**.

2. **Define boundary cases**
   Create a table of test cases that cover:

   * **Lower and upper bounds** for `price` and `customer_age`.
   * **Just inside** and **just outside** the valid ranges.
   * **Critical transition points**, such as the senior threshold at age 65.
   * Both member and non-member cases.

3. **Design input–output pairs**
   Example structure for your test table:

   | # | Input (`price`, `age`, `is_member`) | Expected Behavior          | Reason                 |
   | - | ----------------------------------- | -------------------------- | ---------------------- |
   | 1 | `(0, 40, False)`                    | Valid → no discount → 0    | Lower price bound      |
   | 2 | `(1000, 40, False)`                 | Valid → no discount → 1000 | Upper price bound      |
   | 3 | `(-0.01, 40, False)`                | Invalid → ValueError       | Below lower bound      |
   | 4 | `(1000.01, 40, False)`              | Invalid → ValueError       | Above upper bound      |
   | 5 | `(100, 64, False)`                  | No discount → 100          | Below senior threshold |
   | 6 | `(100, 65, False)`                  | Senior discount (5%) → 95  | At senior threshold    |
   | 7 | `(100, 66, True)`                   | Member + senior (15%) → 85 | Above threshold        |
   | 8 | `(100, -1, True)`                   | Invalid → ValueError       | Below age lower bound  |
   | 9 | `(100, 121, True)`                  | Invalid → ValueError       | Above age upper bound  |

4. **Implement tests**

   * Use simple `assert` statements or print-based checks (no frameworks).
   * Focus on verifying boundary behaviors and error handling.

---

## Example Console Test Snippet

```python
def run_boundary_tests():
    print("[INFO] Starting boundary tests...")
    ok = True
    ok &= assert_equal(calculate_discount(0, 40, False), 0.0, "lower price bound")
    ok &= assert_equal(calculate_discount(1000, 40, False), 1000.0, "upper price bound")
    ok &= expect_value_error(lambda: calculate_discount(-0.01, 40, False), "price below lower bound")
    ok &= expect_value_error(lambda: calculate_discount(1000.01, 40, False), "price above upper bound")
    ok &= assert_equal(calculate_discount(100, 65, True), 85.0, "member + senior boundary")
    print("Boundary testing complete.")
```

*(Define `assert_equal` and `expect_value_error` like in earlier exercises.)*

---

## Evaluation Criteria

| Criterion         | Description                                                             |
| ----------------- | ----------------------------------------------------------------------- |
| **Coverage**      | All relevant boundaries (valid and invalid) are tested.                 |
| **Correctness**   | Expected results align with the specification.                          |
| **Clarity**       | Tests are easy to read and labeled clearly.                             |
| **Encapsulation** | Tests rely only on the function’s public interface, not internal logic. |

---

## Optional Extensions

* Add floating-point edge tests (`price=0.001`, `price=999.999`).
* Test combinations of discounts and limits (e.g., senior members at price boundaries).
* Discuss which boundaries are *open* vs. *closed* intervals (inclusive vs. exclusive).

---

Run from console:

```bash
python test_calculate_discount_boundaries.py
```

Expected output:

```
[PASS] lower price bound
[PASS] upper price bound
[PASS] price below lower bound
[PASS] price above upper bound
[PASS] member + senior boundary
Boundary testing complete.
```
