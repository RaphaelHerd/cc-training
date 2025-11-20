# 🧪 Exercise: Add Negative Tests - Diagnose & Refactor

## 🎯 Goal

Learn to design **negative tests** that verify correct handling of **invalid inputs and failure paths**, while also adding a few **realistic positive tests** for valid cases.
You’ll spot a codebase with only “happy path” tests, then add meaningful negative tests and improve validation.

---

## 🔎 Description (What’s wrong here?)

The following **bad example**:

* Accepts **invalid registration data** (weak validation / silent acceptance).
* Tests cover **only success cases** (no negative tests).
* Errors are returned as strings instead of raising exceptions (hard to test or trust).

You’ll refactor to raise exceptions on invalid inputs and add both **negative** and **positive** tests using the Arrange–Act–Assert pattern.

---

## ☄️ Fictional Use Case

A tiny **User Registration** module:

* `register_user(username, email, password)` should return a `User` object on success.
* Validation rules:

  * `username`: 3–20 chars, alphanumeric + `_` only.
  * `email`: must contain one `@` and a dot after it.
  * `password`: ≥ 8 chars, includes a digit **and** a letter.

---

## ❌ Bad Implementation + Tests (No Negative Coverage)

### `registration.py` (bad)

```python
# registration.py
from dataclasses import dataclass

@dataclass
class User:
    username: str
    email: str

def register_user(username: str, email: str, password: str):
    """
    BAD: Returns strings for errors and lacks validation.
    """
    if not username or not email or not password:
        return "missing fields"  # ❌ wrong error type
    if len(password) < 5:  # ❌ too weak
        return "weak password"
    return User(username=username, email=email)
```

### `test_registration_bad.py` (bad)

```python
# test_registration_bad.py
from registration import register_user, User

def test_register_success():
    user = register_user("alice", "alice@example.com", "abc12345")
    assert isinstance(user, User)
    assert user.username == "alice"
    assert user.email == "alice@example.com"
```

> These tests pass even when validation is broken - there are **no negative tests** and **no reliable assertions**.

---

## 🧩 Your Task

1. **Identify missing negative tests:**

   * Empty fields, invalid usernames, invalid emails, weak passwords.
2. **Refactor implementation:**

   * Raise `ValueError` on invalid inputs.
3. **Write tests:**

   * Include both **positive** and **negative** cases.
   * Follow **Arrange-Act-Assert**.
4. **Measure coverage** with `pytest-cov`.


## 🧠 Checklist

* [ ] Add **negative tests** for every validation rule.
* [ ] Keep tests **fast** and **independent**.
* [ ] Use **AAA** (Arrange–Act–Assert).
* [ ] Measure coverage to ensure negative branches are tested.

---

## ▶️ How to Run (with Coverage)

```bash
pip install -r requirements.txt
pytest -q --cov=. --cov-report=term-missing
```

## 📦 requirements.txt

```txt
# requirements.txt

pytest>=7.0
pytest-cov>=4.0
```

*(Fully automated - runs out of the box in any IDE or terminal.)*
