"""
pages/login_page.py — Login Page Object
========================================
Represents the /login screen on the-internet.herokuapp.com.

Key Playwright concept: Locators
  - page.locator("css selector")    →  like XCUITest's app.buttons["label"]
  - page.get_by_role("button")      →  semantic, preferred when possible
  - page.get_by_label("Username")   →  finds input by its <label> text
  - page.get_by_test_id("login")    →  uses data-testid attribute

Locators are lazy — they don't hit the DOM until you act on them (click, fill, etc.)
This means you can define them as properties at the top of the class.
"""

from pages.base_page import BasePage
from playwright.sync_api import Page


class LoginPage(BasePage):

    URL = "/login"

    def __init__(self, page: Page):
        super().__init__(page)

        # ------------------------------------------------------------------
        # Locators — defined once here, used throughout the class
        # Equivalent to lazy var elements in XCUITest page/screen objects
        # ------------------------------------------------------------------
        self.username_field = page.get_by_label("Username")
        self.password_field = page.get_by_label("Password")
        self.login_button = page.get_by_role("button", name="Login")
        self.flash_message = page.locator("#flash")

    # ------------------------------------------------------------------
    # Actions — the public API your tests will call
    # ------------------------------------------------------------------

    def navigate(self):
        """Go to the login page."""
        super().navigate(self.URL)

    def login(self, username: str, password: str):
        """Fill credentials and submit."""
        self.fill(self.username_field, username)
        self.fill(self.password_field, password)
        self.click(self.login_button)

    def get_flash_message(self) -> str:
        return self.get_text(self.flash_message)

    # ------------------------------------------------------------------
    # Assertions — page-specific checks that tests can call
    # ------------------------------------------------------------------

    def assert_login_successful(self):
        self.assert_url_contains("/secure")
        self.assert_visible(self.flash_message)

    def assert_login_failed(self):
        self.assert_url_contains("/login")
        self.assert_visible(self.flash_message)
