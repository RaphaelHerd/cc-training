# 🚀 GitLab CI/CD Workshop – End-to-End DevOps with a Python App
## 🧩 Extend the Pipeline with Multi-Stage Environments: Develop → QA → Production

**Goal:**  
Expand your existing single-deployment CI/CD pipeline into a **realistic three-environment workflow** that represents a common enterprise DevOps setup.

You will implement and understand the flow:
1. **Develop Environment** – automatically deploys after code merges into `main`.
2. **Quality Assurance Environment (QA)** – automatically deployed after Develop; runs **integration** and **load tests** on that deployed environment.
3. **Production Environment** – manually triggered deployment once QA validation succeeds.

---

### 🧠 Why This Matters

Real-world CI/CD pipelines rarely go straight from “merge” to “production.”  
Instead, code moves through several controlled environments — each one acting as a **quality gate**.

| Environment | Purpose | Trigger Type |
|--------------|----------|---------------|
| **Develop** | Used by developers to test newly merged code. Basic deployment and smoke testing happen here. | Automatic |
| **Quality Assurance (QA)** | Used by QA engineers or automation systems to run full integration and load tests on the deployed app. | Automatic |
| **Production** | The live environment. Deployed only when QA validation is successful and human approval is given. | Manual |

This pipeline will show you how **GitLab environments, stages, and job dependencies** work together to ensure safe and repeatable delivery.

---

### 🧱 Steps

#### 1️⃣ Update the Pipeline Stages

Open `.gitlab-ci.yml` and modify the `stages:` section to define the three new deployment stages:

```yaml
stages:
  - test
  - code_quality
  - sast
  - dependency_scanning
  - license_scanning
  - dast
  - deploy_develop
  - deploy_qa
  - qa_tests
  - deploy_prod
````

💡 **Explanation:**
These stages represent the full lifecycle: build & test → deploy to Develop → verify in QA → promote to Production.

---

#### 2️⃣ Add the Multi-Environment Deployment and Testing Jobs

Below is a complete example you can append to your `.gitlab-ci.yml` file:

```yaml
# ----------------------------
# DEVELOP DEPLOYMENT (automatic)
# ----------------------------
deploy_develop:
  stage: deploy_develop
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
  script:
    - echo "=== DEVELOP DEPLOYMENT START ==="
    - echo "Deploying Flask Todo App to DEVELOP environment..."
    - echo "Project: $CI_PROJECT_PATH"
    - echo "Commit: $CI_COMMIT_SHORT_SHA"
    - echo "Develop environment deployment completed (simulated)."
    - echo "=== DEVELOP DEPLOYMENT END ==="
  environment:
    name: develop
    url: https://develop.example.com/flask-todo

# ----------------------------
# QA DEPLOYMENT (automatic, depends on develop)
# ----------------------------
deploy_qa:
  stage: deploy_qa
  needs: ["deploy_develop"]
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
  script:
    - echo "=== QA DEPLOYMENT START ==="
    - echo "Deploying Flask Todo App to QA environment..."
    - echo "Using code from develop build for validation."
    - echo "QA environment deployment completed (simulated)."
    - echo "=== QA DEPLOYMENT END ==="
  environment:
    name: quality-assurance
    url: https://qa.example.com/flask-todo

# ----------------------------
# QA TESTS (integration + load testing)
# ----------------------------
qa_tests:
  stage: qa_tests
  needs: ["deploy_qa"]
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
  script:
    - echo "=== QA TESTING START ==="
    - echo "Running integration tests on QA environment..."
    - echo "Simulating end-to-end scenarios (login, DB access, etc.)..."
    - echo "Integration tests PASSED."
    - echo "Running load tests (500 concurrent users)..."
    - echo "Response times < 200ms, error rate < 1%."
    - echo "Load testing PASSED."
    - echo "=== QA TESTING END ==="
  artifacts:
    when: always
    paths:
      - qa-test-report.txt
  after_script:
    - echo "Simulated QA Test Report" > qa-test-report.txt

# ----------------------------
# PRODUCTION DEPLOYMENT (manual)
# ----------------------------
deploy_prod:
  stage: deploy_prod
  needs: ["qa_tests"]
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
  script:
    - echo "=== PRODUCTION DEPLOYMENT START ==="
    - echo "Promoting Flask Todo App from QA → PRODUCTION..."
    - echo "Project: $CI_PROJECT_PATH"
    - echo "Commit: $CI_COMMIT_SHORT_SHA"
    - echo "Production deployment successful (simulated)."
    - echo "=== PRODUCTION DEPLOYMENT END ==="
  when: manual
  environment:
    name: production
    url: https://prod.example.com/flask-todo
```

---

#### 3️⃣ How It Works

1. **Merge to `main` branch** triggers the pipeline.
2. The pipeline runs:

   * Code checks (unit tests, SAST, etc.)
   * Automatic **Develop** deployment.
   * Automatic **QA** deployment (dependent on Develop).
   * Automatic **Integration + Load tests** on QA environment.
3. After successful QA validation, a **manual gate** appears in the pipeline for **Production deployment**.
4. A release engineer or authorized user must click **▶ Play** to execute `deploy_prod`.

---

#### 4️⃣ Reflect and Discuss

💬 **Key Discussion Points for the team:**

* Why are multiple environments critical in enterprise DevOps pipelines?
* How does the QA stage help detect issues earlier than Production?
* How could you connect real test frameworks (e.g., Selenium, Locust, or Postman collections) to the `qa_tests` job?
* What GitLab settings could enforce role-based approvals for Production deploys?
* How do you integrate infrastructure?
* How did you ensure infrastructure as code quality?

💡 **Pro Tip:**
You can connect GitLab environments with Kubernetes namespaces, Docker containers, or cloud VMs later on — without changing the logical pipeline flow you’ve just created.

---

### ✅ Expected Results

After completing this task:

* The **Develop** environment deploys automatically after merges to `main`.
* The **QA** environment is deployed automatically and runs **integration** and **load tests**.
* Only if QA passes, a **manual approval** step allows promotion to **Production**.
* The pipeline visibly promotes your application through **Develop → QA → Production**, giving clear visibility and control.