# 🎭 playwright-demo-py

Python Playwright test framework with automated GitHub Actions CI and a live dashboard on GitHub Pages.
Python port of [playwright-demo-js](https://github.com/jay-yeluru/playwright-demo-js).

**Test site:** [the-internet.herokuapp.com](https://the-internet.herokuapp.com)

---

## Architecture: How this maps to your XCUITest world

```
XCUITest                           Playwright/pytest equivalent
──────────────────────────────     ──────────────────────────────
XCTestCase subclass                BasePage (pages/base_page.py)
Screen-specific helper class       LoginPage, HomePage (pages/*.py)
setUp() / tearDown()               fixtures in conftest.py
XCUIApplication()                  page (injected by pytest-playwright)
XCTAssertTrue / XCTAssertEqual     expect(locator).to_be_visible() etc.
@testCase("smoke")                 @pytest.mark.smoke
Test scheme / test plan            pytest -m smoke / -m regression
Parallel test execution            pytest -n auto (pytest-xdist)
```

---

## Project Structure

```
playwright-demo-py/
├── pages/                        # Page Object Model — one file per screen
│   ├── base_page.py              # Wrapper methods: click, fill, assert, etc.
│   ├── login_page.py             # LoginPage(BasePage)
│   └── home_page.py              # HomePage(BasePage)
│
├── tests/                        # Test files — mirror your pages/ structure
│   └── test_login.py             # class TestLogin — groups related tests
│
├── utils/                        # Shared helpers (data generators, API clients, etc.)
│   └── __init__.py
│
├── conftest.py                   # Fixtures: page objects, auth state, browser config
├── pyproject.toml                # pytest config, markers, Playwright options
├── requirements.txt
│
└── .github/
    ├── workflows/
    │   ├── run-tests.yml         # Trigger tests → upload artifacts
    │   └── publish-report.yml   # Download artifacts → generate dashboard → push gh-pages
    └── scripts/
        └── generate_dashboard.py # Reads JSON results, builds HTML dashboard
```

---

## OOP Architecture: The Page Object Model

### Why OOP here?

In XCUITest you probably have helper functions per screen. POM formalizes this:
each screen is a **class**, elements are **instance variables**, interactions are **methods**.

```
BasePage          ← common wrappers (click, fill, wait, assert)
  └── LoginPage   ← /login elements + actions + assertions
  └── HomePage    ← /secure elements + actions + assertions
  └── ...         ← add a new class for every new screen
```

### Adding a new page

1. Create `pages/my_new_page.py`
2. Class inherits `BasePage`
3. Define locators in `__init__`
4. Add action methods + assertion methods
5. Add fixture to `conftest.py`
6. Use in `tests/test_my_feature.py`

---

## Quick Start

```bash
# Install
pip install -r requirements.txt
playwright install chromium

# Run all tests
pytest

# Run smoke tests only
pytest -m smoke

# Run headed (watch the browser)
pytest --headed

# Run in a specific browser
pytest --browser=firefox

# Run in parallel (4 workers)
pytest -n 4

# View the HTML report
open reports/index.html
```

---

## Key Playwright Concepts

### Locators (how you find elements)

```python
page.get_by_label("Username")          # find by <label> text — preferred
page.get_by_role("button", name="Login") # find by ARIA role
page.get_by_test_id("submit")          # find by data-testid attr
page.locator("#flash")                 # CSS selector fallback
page.locator("text=Welcome")           # find by text content
```

### Assertions (async-safe, auto-retrying)

```python
from playwright.sync_api import expect

expect(locator).to_be_visible()        # element is on screen
expect(locator).to_have_text("Hello")  # exact text match
expect(locator).to_contain_text("He")  # partial match
expect(page).to_have_url(re.compile("/secure"))
```

Playwright's `expect()` **auto-retries** for up to 5 seconds by default —
no need for explicit `wait_for_element` calls in most cases.

### Fixtures (pytest's version of setUp)

```python
# conftest.py defines this once:
@pytest.fixture
def login_page(page: Page) -> LoginPage:
    return LoginPage(page)

# Any test can request it by name — no import needed:
def test_something(login_page):   # ← pytest injects it
    login_page.navigate()
```

---

## CI/CD Pipeline

```
Manual trigger (workflow_dispatch)
    ↓
run-tests.yml
  → install Python + Playwright
  → run pytest (selected browser)
  → upload reports/ as artifact
    ↓
publish-report.yml  (triggers automatically after run-tests.yml)
  → checkout gh-pages branch
  → download artifact
  → run generate_dashboard.py → updates index.html + history.json
  → commit + push to gh-pages
    ↓
Live dashboard at https://<you>.github.io/<repo>/
```

### GitHub Pages setup (one-time)

```bash
git switch --orphan gh-pages
git commit --allow-empty -m "init: gh-pages"
git push origin gh-pages
git checkout main
```

Then: Settings → Pages → Source: `gh-pages` branch, `/ (root)`
And: Settings → Actions → General → Workflow permissions → Read and write

---

## Adding More Tests

As you add screens to test, keep this pattern:

```
pages/
  checkout_page.py     → CheckoutPage(BasePage)
  cart_page.py         → CartPage(BasePage)

tests/
  test_checkout.py     → class TestCheckout
  test_cart.py         → class TestCart
```

Use `utils/` for shared non-UI helpers:
- `utils/api_client.py`   — API calls to set up test data
- `utils/data_factory.py` — random data generators
- `utils/db_helpers.py`   — direct DB queries if needed
