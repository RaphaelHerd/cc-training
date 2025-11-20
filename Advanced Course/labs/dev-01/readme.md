# 🚀 GitLab CI/CD Workshop – End-to-End DevOps with a Python App

## 🎯 Goal of the Workshop

In this lab you will walk through a **complete DevOps workflow** in GitLab using a real Python/Flask application:

- 🔄 Use a small **existing GitHub project** as reference application.
- 🧾 Track work with **issues** and a **sprint**.
- 🌿 Create and work on a **feature / fix branch**.
- ⚙️ Push multiple commits and run **GitLab CI pipelines**.
- 🧠 Add:
  - 🧪 Unit tests
  - 🧹 Code Quality
  - 🧰 SAST
  - 🧨 DAST
  - 📦 Dependency Scanning
  - ⚖️ License Compliance
- 👥 Use **Merge Requests with mandatory code review**.
- 🚀 Trigger a **fake deployment (CD)** via GitLab CI.

---

## 🏗 Base Application (Verified, Existing Project)

We use this real repo:

> 🌐 `./flask-todo` of this directory.

This project contains:

- `app.py` – Flask application
- `templates/` – HTML templates
- Uses Flask + SQLAlchemy + SQLite

You will **import this into GitLab** and build CI/CD around it.

---

## 🧩 Scenario

Your team maintains the **Flask Todo App**.  
A user reports a bug:

> ❗ When creating a TODO item **with an empty description**, the app behaves incorrectly:
> - It accepts empty items instead of showing an error message.
> - Sometimes this leads to confusing UI or potential errors downstream.

Your job:

1. 🐞 Track the bug in GitLab.
2. 🧑‍💻 Fix it in a feature branch.
3. 🧰 Protect quality using GitLab CI (tests + security + quality).
4. ✅ Get the fix reviewed and approved.
5. 🚀 Merge to `main` and trigger a **deployment**.

---

# 1️⃣ Project Setup in GitLab

### 🧱 Task 1.1 – Import the GitHub Project into GitLab

**Goal:** Have your own GitLab project with the Flask app.

**Steps:**

1. 🆕 In GitLab, create a **new project**:
   - Use **“Import project from repository by URL”**.
   - URL: `https://github.com/patrickloeber/flask-todo.git`
2. Name the project, e.g. `flask-todo-gitlab`.
3. ⏳ Wait until GitLab finishes importing.
4. ✅ Verify in the GitLab Repo:
   - `app.py` exists.
   - `templates/` folder exists.
   - `README.md` is present.

---

### 💻 Task 1.2 – Clone Locally and Run the App

**Goal:** Confirm the app works locally before doing CI/CD.

**Steps:**

1. 📥 Clone your **GitLab** repository locally:
    ```bash
    git clone <your-gitlab-project-clone-url>
    cd flask-todo-gitlab
    ```

2. 🐍 Create and activate a venv:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. 📦 Install dependencies (based on the original README):

   ```bash
   pip install Flask Flask-SQLAlchemy
   ```
4. ▶️ Run the app:

   ```bash
   export FLASK_APP=app.py
   export FLASK_ENV=development
   flask run
   ```
5. 🌐 Open `http://127.0.0.1:5000/` and confirm:

   * You can create TODO items.
   * They show up in the list.

---

# 2️⃣ Issue & Sprint Workflow in GitLab

### 🐞 Task 2.1 - Create a Bug Issue

**Goal:** Use GitLab Issues as the starting point of the DevOps flow.

**Steps:**

1. ➕ Create a new Issue. (If not familiar with it, look into the documentation)
2. Create a Bug report consisting of

   * a description of the bug 🧾,
   * a reproduction description 🔁,
   * and a definition of done ✅.
3. Set **Type**: **Issue** .

---

### 📆 Task 2.2 - Plan the Issue (Sprint / Iteration)

**Goal:** Show how issues are connected to planning.

**Steps:**

1. Create or pick an **Iteration/Sprint** in your GitLab project.
2. Assign the created issue to the current iteration/sprint.
3. 👤 Assign the issue to **yourself**.
4. 📅 Add a **due date**.

# 3️⃣ Branching & Local Development

### 🌿 Task 3.1 - Create a Feature/Bug Branch for the Issue

**Goal:** Use GitLab’s issue → branch workflow.

**Steps (Option A – via UI):**

1. Open the issue.
2. Use **“Create merge request”** or **“Create branch”** from issue sidebar.
3. Name the branch:

   * `bug/empty-todo-validation`

**Steps (Option B - via Git CLI):**

```bash
git checkout main
git pull origin main
git checkout -b bug/empty-todo-validation
git push -u origin bug/empty-todo-validation
```

---

### 🔍 Task 3.2 – Reproduce the Bug

**Goal:** Make sure the bug is understood.

**Steps:**

1. Ensure your app is running locally.
2. Try to submit a TODO with **no text**.
3. Observe:

   * The app allows it (bug).
   * Or any unexpected behavior.

Document your observation as a comment in the GitLab issue. Add also further questions. Add at least one comment to keep it as close as possible to the real world.

---

### 🛠 Task 3.3 - Implement the Fix

**Goal:** Add input validation in `app.py`.

---

### 🧪 Task 3.4 - Add Unit Tests

**Goal:** Introduce automated tests to verify the bug and the fix.

**Steps:**

1. Create a folder `tests/` in the repo.

2. Create a file `tests/test_app.py`.

3. In `test_app.py`, write tests using `pytest`, for example:

   * A test that ensures an empty TODO is **not added**.
   * A test that ensures a valid TODO **is** added.

4. Example skeleton:

   ```python
   import pytest
   from app import app, db

   @pytest.fixture
   def client():
       app.config["TESTING"] = True
       app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
       with app.test_client() as client:
           with app.app_context():
               db.create_all()
           yield client

   def test_cannot_create_empty_todo(client):
       response = client.post("/", data={"todo": ""}, follow_redirects=True)
       # adjust form field name to match template
       assert b"cannot be empty" in response.data.lower()
   ```

5. Run tests locally:

   ```bash
   pip install pytest
   pytest
   ```

---

### 💾 Task 3.5 - Make Multiple Commits & Pushes

**Goal:** Simulate realistic development with several pushes triggering CI.

**Steps:**

1. Commit in small increments, e.g.:

   ```bash
   git add app.py
   git commit -m "fix: add validation for empty todo description"
   git push origin bug/empty-todo-validation

   git add tests/test_app.py
   git commit -m "test: add tests for empty todo submission"
   git push origin bug/empty-todo-validation

   # maybe refactor or tweak UX
   git add app.py templates/
   git commit -m "refactor: improve error message and template"
   git push origin bug/empty-todo-validation
   ```

2. Create a `requirements.txt` file for all dependencies.

   ```text
   # requirements.txt
   # Flask Todo App - Dependencies

   # --- Core Application ---
   Flask==2.3.3
   Flask-SQLAlchemy==3.1.1

   # --- Testing & QA ---
   pytest==8.1.1
   pytest-cov==5.0.0
   coverage==7.6.1
   requests==2.32.0

   # --- Database Driver (used by SQLAlchemy) ---
   SQLAlchemy==2.0.25

   # --- Environment Utilities ---
   python-dotenv==1.0.1
   ```

2a. Add and push the changes to the remote branch as well.

Later, CI will run on each push once configured.

---

# 4️⃣ GitLab CI: Build, Test, and Security

Now you will configure `.gitlab-ci.yml` to implement a **full CI pipeline** with:

🧪 Unit tests • 🧹 Code Quality • 🧰 SAST • 🧨 DAST • 📦 Dependency Scanning • ⚖️ License Compliance • 🚀 Deployment

## 🧱 4.1 - Create `.gitlab-ci.yml`

**Goal:** Set up a pipeline using GitLab templates.

At the root of your repository, create a new file: `.gitlab-ci.yml` with the following content:

```yaml
# ----------------------------
# GitLab CI/CD for Flask Todo
# ----------------------------

include:
  - template: Code-Quality.gitlab-ci.yml
  - template: Jobs/SAST.gitlab-ci.yml
  - template: Jobs/Dependency-Scanning.v2.gitlab-ci.yml
  - template: Jobs/Dependency-Scanning.gitlab-ci.yml
  - template: DAST.gitlab-ci.yml

stages:
  - test
  - code_quality
  - sast
  - dependency_scanning
  - license_scanning
  - dast
  - deploy

variables:
  PYTHON_VERSION: "3.11"
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"
  DAST_WEBSITE: "https://example.com"

default:
  image: python:${PYTHON_VERSION}
  cache:
    paths:
      - .cache/pip

unit_tests:
  stage: test
  script:
    - python -m pip install --upgrade pip
    - if [ -f requirements.txt ]; then pip install -r requirements.txt; else pip install Flask Flask-SQLAlchemy; fi
    - pip install pytest
    - pytest --junitxml=report.xml
  artifacts:
    when: always
    reports:
      junit: report.xml

deploy_mock:
  stage: deploy
  script:
    - echo "Simulating deployment of Flask Todo App..."
    - echo "Project: $CI_PROJECT_PATH"
    - echo "Deployed commit: $CI_COMMIT_SHORT_SHA"
  when: manual
  environment:
    name: production
```

---

## 🚦 4.2 - Trigger the Pipeline

**Goal:** See CI in action.

**Steps:**

1. 💾 Commit and push `.gitlab-ci.yml` to your feature branch:

   ```bash
   git add .gitlab-ci.yml
   git commit -m "chore: add GitLab CI pipeline with tests and security scanning"
   git push
   ```
2. 🖥 In GitLab, open **CI/CD → Pipelines**.
3. 🔍 Observe the pipeline stages:

   * `test` (unit_tests)
   * `code_quality`
   * `sast`
   * `dependency_scanning`
   * `license_scanning`
   * `dast`
   * (optional manual) `deploy_mock`
4. 📊 Investigate job logs and artifacts (e.g. Code Quality report in MR widget).

# 5️⃣ Merge Request, Review & Quality Gates

### 🧭 5.1 - Create a Merge Request

**Goal:** Use MR as central integration point.

**Steps:**

1. 🔀 In GitLab: click **Merge Requests → New merge request**.
2. Select:

   * Source branch: `bug/empty-todo-validation`
   * Target branch: `main`
3. In MR description, link the issue:

   * e.g. `Closes #<issue-number>`
4. Save the MR.

---

### 🔒 5.2 - Configure Quality Gates (Project Settings)

**Goal:** Ensure that merging without review or failing CI is **not possible**.

**Steps (as Maintainer / Owner):**

1. ⚙️ Go to **Settings → General → Merge request approvals** (or **Settings → Merge requests** depending on GitLab version).
2. Configure:

   * **Approvals required:** `1`
3. Go to **Settings → Repository → Protected branches**:

   * Protect `main`:

     * Allow **no direct pushes** (developer must use MR).
     * Require **merge via MR**.
4. Go to **Settings → General → Merge requests**:

   * Enable: **“Pipelines must succeed”** before merge.

Now:

* At least **one reviewer** must approve.
* CI pipeline must pass.

---

### 👥 5.3 – Reviewer Workflow (Peer Review)

**Goal:** Practice MR review and approval.

**Steps for the reviewer (another participant or your trainer):**

1. Open the MR for `bug/empty-todo-validation`.
2. Review changes in **“Changes”** tab:

   * Does validation logic look correct?
   * Are tests meaningful?
   * Any obvious improvements?
3. 💬 Add at least one **discussion comment** (nitpick or suggestion).
4. ✅ Once satisfied, click **“Approve”**.

**Back to author:**

1. If there are requested changes, implement them:

   * Modify code.
   * Commit and push again.
2. Wait for CI to run again.
3. When:

   * All jobs **green**, and
   * At least one **approval** exists,
     then click **“Merge”**.

The feature branch is now merged into `main`.

---

### 🚀 5.4 – Verify Post-Merge Pipeline and Mock Deployment

**Goal:** See CI/CD on `main`.

**Steps:**

1. After merging, go to **CI/CD → Pipelines** again.
2. Locate the pipeline for branch `main`.
3. Confirm that:

   * All stages run again.
   * You can manually trigger `deploy_mock` from the UI.
4. ▶️ Trigger `deploy_mock`:

   * Confirm in job logs:

     ```text
     Simulating deployment of Flask Todo App...
     Project: <your-namespace>/<your-project>
     Deployed commit: <short-SHA>
     ```

This represents your **CD step**.

# 6️⃣ Iterative Improvement (Subtasks / Extensions)

These subtasks let you gradually deepen the scenario.

## 📈 6.1 – Extend Test Coverage

* Add tests for:

  * Updating an existing TODO.
  * Deleting a TODO.
  * Handling very long TODO descriptions.
* Visualize test results in GitLab:

  * Look at **CI/CD → Pipelines → unit_tests** job → **Tests** tab.


## 🧹 6.2 – Improve Code Quality

* Identify issues from the **code quality** report in the MR widget.
* Refactor `app.py`:

  * Extract DB logic into helper functions.
  * Reduce duplication.
* Commit changes and observe:

  * Code Quality comparison between `main` and your branch.

## 🕵️‍♂️ 6.3 – Experiment with DAST

Right now DAST scans `https://example.com`. For your workshop, this is fine to show the process. For extra points:

* Deploy the Flask app to a temporary environment (e.g. local tunnel, Docker, or test server).
* Change `DAST_WEBSITE` in `.gitlab-ci.yml` to that URL.
* Run the pipeline again and see how DAST behaves.

## ⚖️ 6.4 – License & Dependency Management

* Inspect the results of:

  * `dependency_scanning`
  * `license_scanning`
* Discuss:

  * What would you do if a vulnerable or forbidden dependency is reported?
  * How could you add a **policy** that fails the pipeline if certain licenses appear?

# 🏁 7️⃣ Summary of What Participants Learn

By the end of this workshop, participants will have:

* 📦 Imported a **real existing GitHub repo** into GitLab.
* 🧾 Used **Issues, Sprints/Iterations, and Branches** for planning work.
* 🧑‍💻 Implemented a **bug fix** in a structured way.
* 🧪 Written **pytest tests** and integrated them in CI.
* ⚙️ Configured a **full GitLab CI pipeline** with:

  * Unit tests
  * Code Quality
  * SAST
  * DAST
  * Dependency Scanning
  * License Scanning
* 🔒 Set up **Merge Request approvals** and protected `main`.
* 🚀 Executed a **mock deployment** as a CD step.

You now have a complete, realistic **GitLab DevSecOps workflow** around a small Python application.