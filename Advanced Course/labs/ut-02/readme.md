# 🧪 Exercise: Slow & Interactive Tests - Diagnose & Refactor

## 🎯 Goal

Spot unit tests that **violate core testing rules** and refactor them so they are:

* **Small & fast** (entire suite runs before each check-in)
* **Fully automated & non-interactive**
* **Simple to run** (works out-of-the-box in an IDE/terminal)
* **Measurable** (coverage/KPIs collected)

---

## 🔎 Description (What’s wrong here?)

The following **bad example** bakes in slowness, interactivity, and hard-to-run behavior:

* Uses **`time.sleep`** and real **network calls** → slow, flaky.
* Prompts the user with **`input()`** during tests → not automated.
* Requires manual **env var** setup and writes to disk in tests → fragile.
* No **coverage** or KPIs → unmeasurable quality.

You’ll refactor it to a design with dependency injection, mocks, and fast unit tests.

---

## ❌ Bad Implementation + Non-Compliant Tests

### `exchange_rates.py` (bad)

```python
# exchange_rates.py
import os
import time
import json
from urllib.request import urlopen

_CACHE_FILE = "rates_cache.json"

def fetch_usd_to_eur() -> float:
    """
    Fetches USD→EUR exchange rate from a remote endpoint, simulates latency,
    persists to disk cache. Requires an API key either via env or input().
    """
    api_key = os.getenv("EXR_API_KEY")
    if not api_key:
        # ❌ Interactivity: blocks automation and CI
        api_key = input("Enter API key for exchange service: ").strip()

    # ❌ Artificial slowness
    time.sleep(2.5)

    # ❌ Real network call in unit-tested path (slow/flaky/offline failures)
    with urlopen(f"https://example.com/exchange?pair=USD_EUR&key={api_key}") as resp:
        data = resp.read().decode("utf-8")

    # write to a cache file (disk IO in unit tests)
    with open(_CACHE_FILE, "w", encoding="utf-8") as f:
        f.write(data)

    parsed = json.loads(data)
    return float(parsed.get("rate", 0.0))


def convert_usd_to_eur(amount_usd: float) -> float:
    if amount_usd < 0:
        raise ValueError("amount must be non-negative")
    rate = fetch_usd_to_eur()  # tightly coupled to slow IO
    return round(amount_usd * rate, 2)
```

### `test_exchange_rates_bad.py` (bad)

```python
# test_exchange_rates_bad.py
# ❌ These tests are slow, interactive, and order-/environment-dependent.

import os
import time
import builtins
from exchange_rates import fetch_usd_to_eur, convert_usd_to_eur

def test_fetch_prompts_for_key_and_hits_network(monkeypatch):
    # ❌ Interactivity: requires human input
    # ❌ Real network: can't run offline, flaky
    monkeypatch.delenv("EXR_API_KEY", raising=False)
    monkeypatch.setattr(builtins, "input", lambda _: "MANUAL-KEY-FROM-USER")
    rate = fetch_usd_to_eur()
    assert rate > 0.0

def test_convert_is_slow_because_fetch_sleeps(monkeypatch):
    start = time.time()
    _ = convert_usd_to_eur(10.0)
    elapsed = time.time() - start
    # ❌ Test assumes/depends on slow behavior
    assert elapsed >= 2.5

def test_convert_depends_on_previous_cache_file():
    # ❌ Order dependency: assumes prior test created cache file with data
    # (No setup; if run in isolation, likely fails or uses stale file)
    amount = 20.0
    eur = convert_usd_to_eur(amount)
    assert eur > 0.0
```

> Run these and you’ll see: **slow**, **interactive**, **order-dependent**, and **flaky**.

---

## 🧩 Your Task

1. **Identify violations** of:

   * Small & fast tests
   * Fully automated & non-interactive
   * Simple to run
   * Measurable (coverage)

2. **Refactor the code** to isolate side effects:

   * Use **dependency injection** (pass in fetcher/clock/storage).
   * No user prompts or real network in unit paths.
   * No disk writes in unit tests.

3. **Refactor the tests**:

   * Use **Arrange–Act–Assert**.
   * **Mock** external deps (network/clock/storage).
   * Keep tests **fast** and **deterministic**.
   * Add a **coverage** command in the run instructions.

---

## ▶️ How to Run (with Coverage)

```bash
# Install pytest + coverage (simple to run in IDE or terminal)
pip install pytest pytest-cov

# Run fast, automated unit tests with coverage
pytest -q --cov=. --cov-report=term-missing
```
