# 🧪 Exercise: Stubs vs. Mocks

## 🎯 Goal

Show the difference between **stubs** and **mocks** using Python’s built-in `unittest.mock`.

* **Stubs**: provide canned return values to drive code paths; assert on **outputs/state**.
* **Mocks**: verify **interactions** (who was called, with which args, how many times).

---

## ☄️ Scenario

An `AuthService` performs a login:

1. Fetches a user by username from `UserRepository`
2. Verifies the password with `PasswordHasher`
3. On success, calls `Notifier.send_login_alert(user_id, ip)`
4. Returns a `Session` token

You’ll first write tests that use **stubs** (return values only), then tests that use **mocks** (interaction assertions).

---

## 🧱 Interfaces & Models

### `interfaces.py`

```python
# interfaces.py
from dataclasses import dataclass
from typing import Protocol, Optional

@dataclass(frozen=True)
class User:
    user_id: str
    username: str
    password_hash: str

class UserRepository(Protocol):
    def get_by_username(self, username: str) -> Optional[User]: ...

class PasswordHasher(Protocol):
    def verify(self, plain: str, hashed: str) -> bool: ...

class Notifier(Protocol):
    def send_login_alert(self, user_id: str, ip: str) -> None: ...

@dataclass(frozen=True)
class Session:
    user_id: str
    token: str

class AuthError(RuntimeError):
    pass
```

---

## ✅ System Under Test

### `auth.py`

```python
# auth.py
from typing import Optional
from interfaces import UserRepository, PasswordHasher, Notifier, Session, AuthError, User

class AuthService:
    """
    Orchestrates repo -> hasher -> notifier.
    Token is deterministic for easy testing.
    """
    def __init__(self, repo: UserRepository, hasher: PasswordHasher, notifier: Notifier) -> None:
        self._repo = repo
        self._hasher = hasher
        self._notifier = notifier

    def login(self, username: str, password: str, ip: str) -> Session:
        user: Optional[User] = self._repo.get_by_username(username)
        if user is None:
            raise AuthError("unknown user")
        if not self._hasher.verify(password, user.password_hash):
            raise AuthError("invalid credentials")
        self._notifier.send_login_alert(user.user_id, ip)
        return Session(user_id=user.user_id, token=f"TOKEN-{user.user_id}")
```

---

## 🧪 Part 1 - **Stubs** with `unittest.mock`

> Use `Mock` to **stub** collaborator return values and assert on the **result** (not interactions).

### `test_auth_stubs_unittest_mock.py`

```python
# test_auth_stubs_unittest_mock.py
# Run: pytest -q --cov=. --cov-report=term-missing
# or:  python -m pytest -q

import pytest
from unittest.mock import Mock
from interfaces import User, Session, AuthError
from auth import AuthService

def test_login_success_returns_session():
    # Arrange (stubs)
    user = User(user_id="U1", username="alice", password_hash="HASH")
    # mock the 
        # repo =
        # hasher = 
        # notifier = 

    repo.get_by_username.return_value = user
    hasher.verify.return_value = True

    sut = AuthService(repo, hasher, notifier)

    # Act
    session = sut.login("alice", "secret", ip="1.2.3.4")

    # Assert (OUTPUTS/STATE)
    assert isinstance(session, Session)
    assert session.user_id == "U1"
    assert session.token == "TOKEN-U1"

def test_login_fails_when_user_missing():
    # Arrange
    
    # mock the 
        # repo =
        # hasher = 
        # notifier = 

    repo.get_by_username.return_value = None
    sut = AuthService(repo, hasher, notifier)

    # Act / Assert
    with pytest.raises(AuthError):
        sut.login("ghost", "anything", ip="0.0.0.0")

def test_login_fails_when_password_invalid():
    # Arrange
    user = User(user_id="U2", username="bob", password_hash="HASH")
    # mock the 
        # repo =
        # hasher = 
        # notifier = 

    repo.get_by_username.return_value = user
    hasher.verify.return_value = False
    sut = AuthService(repo, hasher, notifier)

    # Act / Assert
    with pytest.raises(AuthError):
        sut.login("bob", "wrong", ip="5.6.7.8")
```

---

## 🧪 Part 2 - **Mocks** with `unittest.mock`

> Use `Mock` to assert **interactions**: called, called once, with expected args.

### `test_auth_mocks_unittest_mock.py`

```python
# test_auth_mocks_unittest_mock.py

import pytest
from unittest.mock import Mock
from interfaces import User
from auth import AuthService

def test_success_triggers_notifier_once_with_expected_args():
    # Arrange
    user = User(user_id="U3", username="carol", password_hash="HASH")
    repo = Mock()
    hasher = Mock()
    notifier = Mock()

    repo.get_by_username.return_value = user
    hasher.verify.return_value = True

    sut = AuthService(repo, hasher, notifier)

    # Act
    sut.login("carol", "secret", ip="9.9.9.9")

    # Assert (INTERACTIONS)
    notifier.send_login_alert.assert_called_once_with("U3", "9.9.9.9")
    # assert one more method that has been called.
    # look into https://docs.python.org/3/library/unittest.mock.html 
    # search for assert_called_once_with and understand what else is possible

def test_failure_paths_do_not_call_notifier():
    # Arrange — A) user missing
    repo_none = Mock()
    hasher_ok = Mock()
    notifier = Mock()
    repo_none.get_by_username.return_value = None
    hasher_ok.verify.return_value = True
    sut_missing = AuthService(repo_none, hasher_ok, notifier)

    # Act / Assert
    with pytest.raises(Exception):
        sut_missing.login("missing", "x", ip="1.1.1.1")
    
    # assert that a method is not called
    # look into https://docs.python.org/3/library/unittest.mock.html 
    # search for assert_called_once_with, assert_not_called


def test_failure_paths_do_not_call_notifier_bad_password():
    # Arrange - B) bad password
    user = User(user_id="U4", username="dan", password_hash="HASH")
    repo_ok = Mock()
    hasher_bad = Mock()
    notifier2 = Mock()
    repo_ok.get_by_username.return_value = user
    hasher_bad.verify.return_value = False
    sut_badpwd = AuthService(repo_ok, hasher_bad, notifier2)

    # Act / Assert
    with pytest.raises(Exception):
        sut_badpwd.login("dan", "bad", ip="2.2.2.2")
    
    # assert that a method is not called
    # look into https://docs.python.org/3/library/unittest.mock.html 
    # search for assert_called_once_with, assert_not_called
```

---

## 🧠 What You’ve Demonstrated

| Technique    | How it’s used here                                                                              |
| ------------ | ----------------------------------------------------------------------------------------------- |
| **Stubs**    | `Mock().method.return_value = ...` to drive branches; assertions on return values / exceptions. |
| **Mocks**    | `assert_called_once_with`, `assert_not_called` to verify collaborator interactions.             |
| **Top-down** | You defined collaborator behavior via mocks before (or without) concrete implementations.       |

---

## ▶️ How to Run (with Coverage)

```bash
pip install -r requirements.txt
pytest -q --cov=. --cov-report=term-missing
```

Expected (abbreviated):

```
.....                                                             [100%]
----------- coverage: platform ... -----------
Name                              Stmts   Miss  Cover
-----------------------------------------------------
interfaces.py                        18      0   100%
auth.py                              17      0   100%
test_auth_stubs_unittest_mock.py     43      0   100%
test_auth_mocks_unittest_mock.py     44      0   100%
```

---

## 📦 requirements.txt

```txt
pytest>=7.0
pytest-cov>=4.0
```

> `unittest.mock` is part of Python’s standard library, so no extra mocking package is needed.
