import os
import pytest
from dotenv import load_dotenv
from playwright.sync_api import Page
from pages.login_page import LoginPage
from pages.home_page import HomePage

load_dotenv()

ENVIRONMENTS = {
    "dev":  "https://the-internet.herokuapp.com",
    "stg":  "https://the-internet.herokuapp.com",
    "prod": "https://the-internet.herokuapp.com",
}


def pytest_addoption(parser):
    parser.addoption(
        "--env",
        default="prod",
        choices=list(ENVIRONMENTS.keys()),
        help="Target environment: dev | stg | prod  (default: prod)",
    )


def pytest_configure(config):
    env = config.getoption("--env", default="prod")
    config.option.base_url = ENVIRONMENTS[env]


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    return LoginPage(page)


@pytest.fixture
def home_page(page: Page) -> HomePage:
    return HomePage(page)


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "ignore_https_errors": True,
    }