# 🧪 Task: Black-Box Testing with an Informal Interface (No pytest)

## Objective

Design and execute black-box tests for a Python class that classifies triangles based on side lengths.
You will test the class **only through its public interface**, using **plain Python functions** and the **console** (no testing frameworks).

---

## Project Structure

Your project should have the following files:

```
triangle_project/
├── interface_triangle_classifier.py
├── triangle_classifier.py
├── test_triangle_classifier.py
└── TASK_DESCRIPTION.md
```

---

## 1. `interface_triangle_classifier.py`

Defines an **informal interface** describing the expected public method.

```python
# interface_triangle_classifier.py

class ITriangleClassifier:
    """
    Informal interface for triangle classification.

    Any class implementing this interface must provide:
        - classify(a, b, c): returns a string describing the triangle type.
    """

    def classify(self, a, b, c):
        raise NotImplementedError("Implement the 'classify' method.")
```

---

## 2. `triangle_classifier.py`

Implements the interface.
This file contains the **real behavior** but hides internal logic behind private methods.

```python
# triangle_classifier.py
from interface_triangle_classifier import ITriangleClassifier

class TriangleClassifier(ITriangleClassifier):
    """Concrete implementation of ITriangleClassifier."""

    def classify(self, a, b, c):
        if not self._is_valid_triangle(a, b, c):
            return "not a triangle"

        if a == b == c:
            return "equilateral"
        if a == b or b == c or a == c:
            return "isosceles"
        return "scalene"

    def _is_valid_triangle(self, a, b, c):
        """Private helper, not visible to black-box testers."""
        if a <= 0 or b <= 0 or c <= 0:
            return False
        return a + b > c and a + c > b and b + c > a
```

---

## 3. `test_triangle_classifier.py`

Implements **black-box tests** without any framework — only functions and console output.

```python
# test_triangle_classifier.py
from triangle_classifier import TriangleClassifier

def assert_equal(actual, expected, label):
    if actual == expected:
        print(f"[PASS] {label}")
        return True
    else:
        print(f"[FAIL] {label}: expected {expected!r}, got {actual!r}")
        return False

def run_tests():
    clf = TriangleClassifier()
    results = []

    # Valid triangles
    results.append(assert_equal(clf.classify(5, 5, 5), "equilateral", "equilateral 5,5,5"))
    results.append(assert_equal(clf.classify(5, 5, 3), "isosceles", "isosceles 5,5,3"))
    results.append(assert_equal(clf.classify(4, 5, 6), "scalene", "scalene 4,5,6"))

    # Invalid triangles
    results.append(assert_equal(clf.classify(1, 2, 3), "not a triangle", "boundary 1,2,3"))
    results.append(assert_equal(clf.classify(0, 4, 5), "not a triangle", "zero side 0,4,5"))
    results.append(assert_equal(clf.classify(-1, 5, 5), "not a triangle", "negative side -1,5,5"))

    passed = sum(results)
    total = len(results)
    print(f"\nSummary: {passed}/{total} tests passed")
    return passed == total

if __name__ == "__main__":
    import sys
    all_ok = run_tests()
    sys.exit(0 if all_ok else 1)
```

---

## 4. Running the Tests

From the console, run:

```bash
python test_triangle_classifier.py
```

Example output:

```
[PASS] equilateral 5,5,5
[PASS] isosceles 5,5,3
[PASS] scalene 4,5,6
[PASS] boundary 1,2,3
[PASS] zero side 0,4,5
[PASS] negative side -1,5,5

Summary: 6/6 tests passed
```

---

## Evaluation Criteria

| Criterion             | Description                                                      |
| --------------------- | ---------------------------------------------------------------- |
| **Correctness**       | Test cases match the behavior defined in the interface contract. |
| **Encapsulation**     | Tests only call the public `classify()` method.                  |
| **Coverage**          | Includes all valid and invalid input cases.                      |
| **No External Tools** | Test execution uses only Python and console output.              |
