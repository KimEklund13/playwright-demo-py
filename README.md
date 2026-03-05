# 🎭 playwright-demo-py

A production-grade end-to-end test automation framework built with Python, Playwright, and pytest - featuring a fully automated CI/CD pipeline and a live test results dashboard hosted on GitHub Pages.

🔗 **[Live Dashboard](https://kimeklund13.github.io/playwright-demo-py/)**

---

## Overview

This framework demonstrates a complete test automation setup from local execution to CI/CD integration and test management reporting. It is built on the **Page Object Model (POM)** pattern for maintainability, integrated with **Qase TMS** for test case management and result tracking, and ships with a zero-cost reporting pipeline using only GitHub-native tooling.

**Test target:** [the-internet.herokuapp.com](https://the-internet.herokuapp.com) - a purpose-built web automation practice site.

---

## Tech Stack

| Tool | Purpose |
|---|---|
| [Playwright](https://playwright.dev/python/) | Browser automation and E2E testing |
| [pytest](https://pytest.org) | Test runner and fixture management |
| [Qase TMS](https://qase.io) | Test case management and result reporting |
| [GitHub Actions](https://github.com/features/actions) | CI/CD pipeline |
| [GitHub Pages](https://pages.github.com) | Live test dashboard hosting |
| [Commitizen](https://commitizen-tools.github.io/commitizen/) | Conventional commit enforcement |
| [pre-commit](https://pre-commit.com) | Git hook management |

---

## Features

- **Cross-browser testing** - Chromium, Firefox, and WebKit via a single workflow input
- **Multi-environment support** - `--env=dev/stg/prod` CLI flag dynamically sets base URL
- **Page Object Model** - clean separation of locators, actions, and assertions per page
- **Pytest markers** - `smoke`, `regression`, `auth` for flexible test scoping
- **Qase TMS integration** - automated tests linked to Qase test cases by ID; results posted automatically on every CI run
- **Live dashboard** - pass rate trends, run history, and per-run HTML reports published to GitHub Pages after every run, with no third-party services
- **Artifact retention** - screenshots, videos, and traces captured on failure; stored as GitHub Actions artifacts for 30 days
- **Conventional commits** - enforced locally via commitizen and pre-commit hooks

---

## Project Structure

```
playwright-demo-py/
├── pages/                        # Page Object Model - one class per page
│   ├── base_page.py              # Shared locator wrappers and assertions
│   ├── login_page.py             # LoginPage(BasePage)
│   └── home_page.py              # HomePage(BasePage)
│
├── tests/                        # Test suites organized by feature
│   └── test_login.py             # Authentication test cases
│
├── utils/                        # Shared helpers: data factories, API clients
│
├── conftest.py                   # Fixtures, env selector, browser context config
├── pyproject.toml                # pytest, commitizen, and project config
├── requirements.txt              # Python dependencies
│
└── .github/
    ├── workflows/
    │   ├── run-tests.yml         # Runs tests on demand; uploads report artifacts
    │   └── publish-report.yml   # Publishes dashboard to GitHub Pages post-run
    └── scripts/
        └── generate_dashboard.py # Builds HTML dashboard from JSON test history
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- A virtual environment (recommended)

### Installation

```bash
git clone https://github.com/kimeklund13/playwright-demo-py.git
cd playwright-demo-py

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
playwright install chromium

# Install git hooks (enforces conventional commit messages)
pre-commit install --hook-type commit-msg
```

### Environment variables (local)

Create a `.env` file in the project root - this file is gitignored:

```bash
QASE_API_TOKEN=your_personal_token_here
QASE_PROJECT=KIM
```

---

## Running Tests

Default browser is Chromium, default environment is `prod`. Both can be overridden per run.

```bash
# Run all tests
pytest

# Run by marker
pytest -m smoke
pytest -m regression
pytest -m "smoke or regression"

# Run a specific test file
pytest tests/test_login.py

# Run a specific test by name
pytest tests/test_login.py::TestLogin::test_valid_login

# Run headed (visible browser - useful for debugging)
pytest -m smoke --headed

# Run in a specific browser
pytest -m smoke --browser=firefox
pytest -m smoke --browser=webkit

# Run against a specific environment
pytest -m smoke --env=stg
pytest -m regression --env=prod

# Combine browser + environment + marker
pytest -m smoke --browser=firefox --env=stg

# Run with verbose output (shows each test name + result)
pytest -m smoke -v

# Parallelization - run tests across multiple workers
pytest -n 4        # 4 parallel workers
pytest -n auto     # uses all available CPU cores (fastest)

# Parallel + marker + browser
pytest -m regression -n auto --browser=chromium
```

### Qase TMS reporting

Two options for running with Qase result posting:

**Option 1 - Explicit flags** (works out of the box, reads token from `.env`):
```bash
pytest -m smoke \
  --qase-mode=testops \
  --qase-testops-api-token=$QASE_API_TOKEN \
  --qase-testops-project=KIM
```

**Option 2 - Shell alias** (cleaner, recommended for frequent use):

Set up once in `~/.zshrc` (see [Local Shell Alias](#local-shell-alias-recommended) below), then:
```bash
pytest-qase -m smoke
pytest-qase -m regression --env=stg
pytest-qase -m regression -n auto
```

---

## Qase TMS Integration

Test cases are created and managed in Qase, then linked to automated tests via decorator:

```python
from qase.pytest import qase

@qase.id(1)
@pytest.mark.smoke
def test_valid_login(self, login_page):
    login_page.navigate()
    login_page.login("tomsmith", "SuperSecretPassword!")
    login_page.assert_login_successful()
```

On each CI run, results are automatically posted to the linked Qase test case - no manual result entry required. Test runs can be scoped to a Qase test plan using `--qase-testops-plan-id`.

---

## CI/CD Pipeline

Triggered manually via `workflow_dispatch` with selectable browser and environment inputs.

```
run-tests.yml
  → Install Python + Playwright
  → Run pytest (selected browser + environment)
  → Upload reports/ and test-artifacts/ as artifacts
      ↓
publish-report.yml  (auto-triggers on completion)
  → Checkout gh-pages branch
  → Download report artifacts
  → Regenerate dashboard with updated run history
  → Commit and push to gh-pages
      ↓
https://kimeklund13.github.io/playwright-demo-py/
```

### Required GitHub secrets

| Secret | Description |
|---|---|
| `QASE_API_TOKEN` | Qase API token (Settings → Access Tokens) |
| `QASE_PROJECT` | Qase project code (`KIM`) |

---

## Extending the Framework

To add coverage for a new page or feature:

1. Create `pages/feature_page.py` extending `BasePage`
2. Define locators, action methods, and assertions
3. Add a fixture to `conftest.py`
4. Create `tests/test_feature.py` with appropriate markers
5. Create corresponding test cases in Qase and link via `@qase.id()`

```
pages/
  checkout_page.py   → CheckoutPage(BasePage)

tests/
  test_checkout.py   → class TestCheckout
```

---

## Commit Convention

This repo enforces [Conventional Commits](https://www.conventionalcommits.org/). The pre-commit hook will block non-conforming messages and display the reference:

```
feat:      new feature
fix:       bug fix
chore:     maintenance, deps, config
docs:      documentation only
refactor:  restructure, no behavior change
test:      adding or updating tests
ci:        GitHub Actions / CI config
style:     formatting, no logic change
perf:      performance improvement

Example: feat(login): add invalid password test
```

Use `cz commit` for an interactive prompt that builds the message for you.

---

## Local Shell Alias (Recommended)

For frequent Qase reporting, set up a shell alias so you don't have to pass flags every time.

**1. Export your Qase API token in `~/.zshrc`:**
```bash
export QASE_API_TOKEN=your_token_here
```

**2. Add the alias in `~/.zshrc`:**
```bash
alias pytest-qase='pytest --qase-mode=testops --qase-testops-api-token=$QASE_API_TOKEN --qase-testops-project=KIM'
```

**3. Apply to your current session:**
```bash
source ~/.zshrc
```

**4. Verify the token is set:**
```bash
echo $QASE_API_TOKEN
```

After setup, use whichever command fits your workflow:

```bash
pytest -m smoke                       # fast local run, no Qase reporting
pytest-qase -m smoke                  # smoke tests + post results to Qase
pytest-qase -m regression --env=stg   # regression against staging + Qase
pytest-qase -m regression -n auto     # parallel regression + Qase
```

The token lives in `~/.zshrc` rather than `.env` so it is available to the shell alias. CI uses GitHub Actions secrets and does not rely on this setup.