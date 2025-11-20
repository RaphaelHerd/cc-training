# 🧪 Fictional Task: Split Bill with Tip - TDD + pytest (Arrange–Act–Assert)

## Task (User Story)

As a diner, I want to **split a restaurant bill** (including tip) among *N* people so that:

* Everyone’s share is rounded to a fixed number of decimals,
* The **sum of all shares equals the total**, and
* Any rounding “leftover” is **fairly distributed** (earliest people get the extra unit).

---

## Acceptance Criteria

Implement:

```python
def split_bill(amount: float, tip_rate: float, people: int, round_to: int = 2) -> list[float]:
    """
    Returns a list of per-person shares such that:
      - total = amount * (1 + tip_rate)
      - shares are rounded to `round_to` decimals
      - sum(shares) == round(total, round_to)
      - any rounding remainder is distributed starting from the first person

    Constraints:
      - amount >= 0
      - 0 <= tip_rate <= 1
      - people >= 1
      - 0 <= round_to <= 4
    Raises:
      - ValueError if constraints are violated
    """
```

## Tests (pytest, Arrange–Act–Assert) — `test_split_bill.py`

```python
# test_split_bill.py
# Run with:  pytest -q

import pytest
from split_bill import split_bill

def test_even_split_no_tip():
    # Arrange
    amount = 24.00
    tip_rate = 0.0
    people = 3

    # Act
    shares = split_bill(amount, tip_rate, people)

    # Assert
    assert shares == [8.0, 8.0, 8.0]
    assert round(sum(shares), 2) == 24.00


def test_rounding_distribution_with_tip():
    # Arrange
    amount = 10.00
    tip_rate = 0.10   # total = 11.00
    people = 3

    # Act
    shares = split_bill(amount, tip_rate, people)

    # Assert
    # Expect two people to get 3.67 and one to get 3.66 (first get the extra cent)
    assert shares == [3.67, 3.67, 3.66]
    assert round(sum(shares), 2) == 11.00


def test_invalid_inputs_raise_value_error():
    # Arrange
    invalid_cases = [
        (-1.0, 0.1, 2, 2),     # negative amount
        (10.0, -0.01, 2, 2),   # tip < 0
        (10.0, 1.01, 2, 2),    # tip > 1
        (10.0, 0.1, 0, 2),     # people < 1
        (10.0, 0.1, 2, -1),    # round_to < 0
        (10.0, 0.1, 2, 5),     # round_to > 4
    ]

    # Act / Assert
    for amount, tip, people, round_to in invalid_cases:
        with pytest.raises(ValueError):
            split_bill(amount, tip, people, round_to)


def test_custom_round_to_zero_decimals():
    # Arrange
    amount = 10.00
    tip_rate = 0.00
    people = 4
    round_to = 0  # whole currency units

    # Act
    shares = split_bill(amount, tip_rate, people, round_to)

    # Assert
    # total = 10; base = 2 each; remainder = 2 → first two get 3
    assert shares == [3.0, 3.0, 2.0, 2.0]
    assert sum(shares) == 10.0
```
## Code (Implementation) — `split_bill.py`

```python
# split_bill.py

from typing import List

def split_bill(amount: float, tip_rate: float, people: int, round_to: int = 2) -> List[float]:
    # Validate inputs
    if amount < 0:
        raise ValueError("amount must be non-negative")
    if not (0 <= tip_rate <= 1):
        raise ValueError("tip_rate must be between 0 and 1 inclusive")
    if people < 1:
        raise ValueError("people must be >= 1")
    if not (0 <= round_to <= 4):
        raise ValueError("round_to must be between 0 and 4 inclusive")

    # Work in integer units to avoid floating-point drift
    scale = 10 ** round_to
    total_units = int(round((amount * (1.0 + tip_rate)) * scale))

    base = total_units // people
    remainder = total_units % people

    # Distribute remainder to the earliest participants
    shares_units = [(base + 1 if i < remainder else base) for i in range(people)]
    # Convert back to floats with the correct rounding
    shares = [units / scale for units in shares_units]
    return shares
```


## How to Run

```bash
pip install pytest
pytest -q
```

Expected output (abbreviated):

```
....                                                                   [100%]
4 passed in 0.XXs
```

---

## Notes for Participants

* Keep the **TDD loop** tight: write one failing test (🔴), implement the minimal code to pass (🟢), then **refactor** while keeping tests green (♻️).
* This example highlights: numeric validation, floating-point safety via integer scaling, and **fair remainder distribution**, all common in real-world billing scenarios.
