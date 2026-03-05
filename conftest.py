"""
conftest.py — Playwright + pytest fixture hub
=============================================
This is the equivalent of a BaseTestCase or XCTestCase subclass in XCUITest.
Everything here is automatically available to every test file — no imports needed.

Key concepts:
  - Fixtures replace setUp/tearDown
  - Scope controls how often a fixture runs:
      "function" = before/after each test  (like setUp/tearDown)
      "session"  = once for the whole run   (like suiteSetUp)
  - yield = the fixture runs setup BEFORE yield, teardown AFTER yield
"""

import pytest
from dotenv import load_dotenv
from playwright.sync_api import Page
from pages.login_page import LoginPage
from pages.home_page import HomePage

# Load environment variables from .env file
load_dotenv()

# ---------------------------------------------------------------------------
# Environment selector
# ---------------------------------------------------------------------------
# In a real project each key would point to a different host, e.g.:
#   "dev":  "https://dev.myapp.com"
#   "stg":  "https://staging.myapp.com"
#   "prod": "https://myapp.com"
#
# Usage:
#   pytest --env=stg -m smoke
#   pytest --env=prod -m regression
#
# Since this is a demo site with only one environment, all keys resolve
# to the same URL — the pattern is here so you can copy it into real projects.
# ---------------------------------------------------------------------------

ENVIRONMENTS = {
    "dev":  "https://the-internet.herokuapp.com",
    "stg":  "https://the-internet.herokuapp.com",
    "prod": "https://the-internet.herokuapp.com",
}


def pytest_addoption(parser):
    """
    Registers custom CLI options.
    This is how pytest learns about --env before any test runs.
    Equivalent to adding launch arguments to an XCUITest scheme.
    """
    parser.addoption(
        "--env",
        default="prod",
        choices=list(ENVIRONMENTS.keys()),
        help="Target environment: dev | stg | prod  (default: prod)",
    )


def pytest_configure(config):
    """
    Runs once before any tests or fixtures.
    We use it to dynamically set base_url from --env so that
    every page.goto("/some-path") resolves against the right host.
    """
    env = config.getoption("--env", default="prod")
    config.option.base_url = ENVIRONMENTS[env]


# ---------------------------------------------------------------------------
# Page Object fixtures
# These are how you hand page objects to tests without any boilerplate.
# ---------------------------------------------------------------------------

@pytest.fixture
def login_page(page: Page) -> LoginPage:
    """
    Gives tests a ready-to-use LoginPage object.
    'page' is injected by pytest-playwright — no setup needed.
    """
    return LoginPage(page)


@pytest.fixture
def home_page(page: Page) -> HomePage:
    return HomePage(page)


# ---------------------------------------------------------------------------
# Auth fixture — reusable logged-in state
# Equivalent to a helper you'd call in setUp for tests that need auth
# but aren't testing the login flow itself.
# ---------------------------------------------------------------------------

@pytest.fixture
def authenticated_page(page: Page) -> Page:
    """
    Returns a page already logged in.

    Usage in a test:
        def test_something_protected(authenticated_page):
            authenticated_page.goto("/secure")
    """
    login = LoginPage(page)
    login.navigate()
    login.login("tomsmith", "SuperSecretPassword!")
    return page


# ---------------------------------------------------------------------------
# Browser context config — applies to every test
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """
    Customize the browser context for every test.
    Equivalent to XCUIApplication launch arguments/environment variables.
    """
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
        # "record_video_dir": "test-artifacts/videos",  # uncomment to always record
    }