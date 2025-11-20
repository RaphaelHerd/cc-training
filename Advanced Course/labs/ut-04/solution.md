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

---

## ✅ Solution - Validation with Positive & Negative Tests

### `registration_ref.py`

```python
# registration_ref.py
import re
from dataclasses import dataclass

@dataclass(frozen=True)
class User:
    username: str
    email: str

USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,20}$")

def _validate_username(username: str) -> None:
    if not isinstance(username, str) or not USERNAME_RE.fullmatch(username or ""):
        raise ValueError("invalid username")

def _validate_email(email: str) -> None:
    if not isinstance(email, str) or "@" not in email:
        raise ValueError("invalid email")
    local, _, domain = email.partition("@")
    if not local or "." not in domain or domain.startswith(".") or domain.endswith("."):
        raise ValueError("invalid email")

def _validate_password(password: str) -> None:
    if not isinstance(password, str) or len(password) < 8:
        raise ValueError("weak password: too short")
    if not any(c.isdigit() for c in password):
        raise ValueError("weak password: missing digit")
    if not any(c.isalpha() for c in password):
        raise ValueError("weak password: missing letter")

def register_user(username: str, email: str, password: str) -> User:
    """
    Returns a User if valid, otherwise raises ValueError.
    """
    _validate_username(username)
    _validate_email(email)
    _validate_password(password)
    return User(username=username, email=email)
```

---

### `test_registration_ref.py`

```python
# test_registration_ref.py
# Run with: pytest -q --cov=. --cov-report=term-missing

import pytest
from registration_ref import register_user, User

# -----------------------
# Positive (Happy Path)
# -----------------------

def test_register_success_happy_path():
    # Arrange
    username = "alice_01"
    email = "alice@example.com"
    password = "abc12345"

    # Act
    user = register_user(username, email, password)

    # Assert
    assert isinstance(user, User)
    assert user.username == username
    assert user.email == email


def test_register_different_valid_cases():
    # Arrange / Act / Assert
    assert isinstance(register_user("Bob99", "bob99@test.org", "Password9"), User)
    assert isinstance(register_user("charlie", "charlie@sub.domain.com", "mixItUp7"), User)
    assert isinstance(register_user("Eve_2", "eve@something.net", "Strong123"), User)


def test_email_case_is_accepted_but_preserved():
    # Arrange
    user = register_user("CaseTest", "USER@EXAMPLE.COM", "ValidPass9")

    # Assert
    assert user.email == "USER@EXAMPLE.COM"  # preserved case
    assert isinstance(user, User)

# -----------------------
# Negative Tests
# -----------------------

def test_rejects_empty_fields():
    with pytest.raises(ValueError):
        register_user("", "user@example.com", "abc12345")
    with pytest.raises(ValueError):
        register_user("user", "", "abc12345")
    with pytest.raises(ValueError):
        register_user("user", "user@example.com", "")


def test_rejects_invalid_usernames():
    for bad in ["ab", "this_is_way_too_long_for_the_rule", "no-dash", "bad space"]:
        with pytest.raises(ValueError):
            register_user(bad, "user@example.com", "abc12345")


def test_rejects_invalid_emails():
    for bad in ["noatsymbol.com", "user@", "@nodomain.com", "user@nodot", "user@.com"]:
        with pytest.raises(ValueError):
            register_user("valid_user", bad, "abc12345")


def test_rejects_weak_passwords():
    with pytest.raises(ValueError):
        register_user("user", "user@example.com", "short7")     # too short
    with pytest.raises(ValueError):
        register_user("user", "user@example.com", "abcdefgh")   # missing digit
    with pytest.raises(ValueError):
        register_user("user", "user@example.com", "12345678")   # missing letter
```

---

## 🧠 Why This Works

| Category         | Description                                       |
| ---------------- | ------------------------------------------------- |
| ✅ Positive tests | Confirm function works for valid, realistic data. |
| ❌ Negative tests | Ensure invalid data raises `ValueError`.          |
| ⚡ Fast           | Pure functions, no I/O.                           |
| 🧩 Deterministic | No randomness or external dependencies.           |
| 📈 Measurable    | All branches covered via `pytest-cov`.            |

---

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

Expected (abbreviated):

```
...........                                                     [100%]
----------- coverage: platform ... -----------
Name                     Stmts   Miss  Cover   Missing
------------------------------------------------------
registration_ref.py         33      0   100%
test_registration_ref.py    43      0   100%
```

## 📦 requirements.txt

```txt
# requirements.txt

pytest>=7.0
pytest-cov>=4.0
```

*(Fully automated - runs out of the box in any IDE or terminal.)*
