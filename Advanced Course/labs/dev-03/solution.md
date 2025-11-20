# 🚀 GitLab CI/CD Workshop – End-to-End DevOps with a Python App
## 🧩 Handling Secrets & Environment Configuration (Build Once, Deploy Many)

**Goal:**  
Make your pipeline **production-grade** by properly handling **secrets** and **environment-specific configuration** for the Flask application’s database, following the DevOps principle:

> **“Build once, deploy many.”**  
> (The same artifact should be deployable to Develop, QA, and Production, only configuration changes.)

You will:

1. Analyze how the Flask app currently handles database configuration.
2. Research **best practices** for secret management and environment config in:
   - GitLab CI/CD
   - Python / Flask
3. Implement **at least one** solution that:
   - Moves database credentials **out of the code**.
   - Uses environment-specific configuration (e.g. different DB for Develop, QA, Production).
   - Keeps the build artifact the same across environments.

---

### 🧠 Why This Matters

Hardcoding credentials (DB user, password, host) in code or in the repo is:

- ❌ Insecure (secrets end up in Git history).
- ❌ Not portable (difficult to change config per environment).
- ❌ Against DevOps best practices (build artifact tightly coupled to one environment).

Instead, we want:

- ✅ **Secrets stored outside of the repo** (e.g. GitLab CI Variables, Vault, etc.).
- ✅ **Environment variables** for configuration (Flask reads from `os.environ`).
- ✅ **One build artifact**, but different deployment configs for:
  - `develop`
  - `quality-assurance`
  - `production`

---

### 🧱 Step 1 – Analyze the Current Database Configuration

1. Open `app.py` in your repo.
2. Locate how the database is configured. Typical patterns:
   - Hardcoded URI, e.g.:  
     ```python
     app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"
     ```
   - Or some hardcoded username/password or path.
3. Answer (in a comment or notes):
   - Where is the DB configuration defined?
   - Is it environment-aware? (Develop vs QA vs Prod?)
   - Are there any secrets or connection strings in plain text?

---

### 🧱 Step 2 – Research Best Practices for Secrets & Config

> 🕵️ **This step is intentionally “research-driven.”  
> Participants must search the internet and documentation.**

Create a small note or markdown file (e.g. `docs/secrets-research.md`) and capture findings.

#### 🔍 Subtask 2.1 – Search for Flask Configuration Best Practices

Search the internet for:

- “Flask configuration via environment variables”
- “Flask SQLALCHEMY_DATABASE_URI environment variable”
- “Flask config.py pattern”

Document:

- At least **one recommended pattern** for:
  - Loading configuration from environment variables.
  - Using a `config.py` or class-based config.
- Example snippet(s) you find.

#### 🔍 Subtask 2.2 – Search for GitLab Secret Management

Search for:

- “GitLab CI/CD variables”
- “GitLab protected variables”
- “GitLab environment-specific variables”

Document:

- How to create **CI/CD variables** in GitLab (including masked/protected).
- How to define **environment-scoped variables** (e.g. different values for `develop` vs `production`).
- How to access them in `.gitlab-ci.yml` and in the running container/environment.

---

### 🧱 Step 3 – Design Your Configuration Strategy

Based on your research, design a small configuration strategy for the Flask Todo app:

- The **application** should read its DB connection string from an environment variable, for example:
  - `DATABASE_URL`
- Your **CI/CD pipeline** should set different values depending on the environment:
  - `DATABASE_URL` for **Develop** (e.g. SQLite or dev DB).
  - `DATABASE_URL` for **Quality-Assurance** (e.g. separate QA DB).
  - `DATABASE_URL` for **Production** (e.g. production DB).

Write down (in `docs/secrets-research.md` or similar):

1. Which environment variables you will use.
2. Which mechanism you’ll use in Flask to read them.
3. Which mechanism you’ll use in GitLab to set them (e.g. CI Variables, environment-scoped variables).

---

### 🧱 Step 4 – Implement Environment-Based DB Config in Flask

Modify the Flask app to use environment variables instead of hardcoded DB config.

1. In `app.py`, adjust the configuration, e.g.:

   ```python
   import os
   from flask import Flask
   from flask_sqlalchemy import SQLAlchemy

   app = Flask(__name__)

   # Read DB URL from environment, with a sane default for local dev
   app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
       "DATABASE_URL",
       "sqlite:///todo.db"  # fallback for local development
   )
   ```

2. (Optional) Introduce a `config.py` file with config classes (Dev, QA, Prod) if you found that pattern useful.
3. Test locally:

   ```bash
   export DATABASE_URL="sqlite:///todo-dev.db"
   flask run
   ```

   * Confirm that the app still works.
   * Optionally check that a different DB file is used.

---

### 🧱 Step 5 – Configure Secrets in GitLab CI/CD

Now move secrets out of code and into **GitLab CI/CD variables**.

#### Subtask 5.1 – Add CI/CD Variables in GitLab

1. In your GitLab project, go to:
   **Settings → CI/CD → Variables**.

2. Add variables for your DB credentials / URLs, e.g.:

   * `DATABASE_URL_DEVELOP`
   * `DATABASE_URL_QA`
   * `DATABASE_URL_PROD`

3. Mark them as **masked** and/or **protected** if appropriate.

#### Subtask 5.2 – Use Environment-Scoped Variables (Optional but Recommended)

If your GitLab supports environment-scoped variables:

* Create a variable named `DATABASE_URL` scoped to environment `develop`.
* Create another `DATABASE_URL` scoped to `quality-assurance`.
* Create another `DATABASE_URL` scoped to `production`.

This way, the same variable name is used, but GitLab automatically chooses the correct value depending on which environment job is running.

---

### 🧱 Step 6 – Wire Environment Config into the Pipeline

Update your multi-stage deployment jobs so they **reuse the same build** but apply different configurations per environment.

If you use environment-scoped `DATABASE_URL`, you might not have to change much — the environment variable will just be present when the job runs.

For clarity, you can also echo (but not expose secrets) some context:

```yaml
deploy_develop:
  stage: deploy_develop
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
  script:
    - echo "Deploying to DEVELOP..."
    - echo "Using environment-specific DATABASE_URL (value is secret)."
    - echo "Simulated deploy using this config."
  environment:
    name: develop
    url: https://develop.example.com/flask-todo
```

Do the same for `deploy_qa` and `deploy_prod` steps.

💡 **Key Point:**
The **build** (code + package) is the same.
What changes is **only the configuration** injected via environment variables.

---

### 🧱 Step 7 – Verify “Build Once, Deploy Many”

To validate that you’ve achieved “build once, deploy many”:

1. Confirm that:

   * There is **no DB password/URL** in your Git repository.
   * All DB-related credentials live in **GitLab CI/CD variables**.
2. Run a full pipeline (`main` branch with a change).
3. Check that:

   * Develop deployment uses the **Develop DB**.
   * QA deployment uses the **QA DB**.
   * (Optionally) Production deployment uses the **Prod DB**.

You can simulate this by:

* Echoing which DB file or host is used (without printing full credentials).
* Writing a small `/env` route in Flask (only in dev) that shows which DB is configured (for the workshop).

---

### ✅ Expected Outcome

By the end of this task, the participants will:

* Understand why **secrets must never be committed** to the repo.
* Know how to use **environment variables** with Flask for configuration.
* Know how to use **GitLab CI/CD variables** (and environment-scoped variables) for secrets.
* Have implemented at least one working solution where:

  * The same build artifact can be **deployed to Develop, QA, and Production**.
  * Each environment uses **different DB credentials**, provided through secure configuration.