"""
pages/base_page.py — Base class for all Page Objects
=====================================================
This is your "wrapper layer" — the equivalent of a helper/utility class
in XCUITest that wraps XCUIElement interactions.

Every page object inherits from this, so common Playwright actions
(click, fill, wait, etc.) live here once and are reused everywhere.

Architecture decision: OOP Page Object Model (POM)
- Each screen/page of the app gets its own class  →  pages/
- Each class inherits BasePage
- Tests use page objects, never raw Playwright calls
- This mirrors how you'd organize XCUITest with screen-specific helper methods
"""

from playwright.sync_api import Page, Locator, expect
import re


class BasePage:
    """
    Base class all page objects inherit from.
    Think of this as your XCUIElement wrapper layer.
    """

    def __init__(self, page: Page):
        self.page = page

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def navigate(self, path: str = ""):
        """Navigate to a path relative to base_url."""
        self.page.goto(path)

    def get_title(self) -> str:
        return self.page.title()

    def get_url(self) -> str:
        return self.page.url

    # ------------------------------------------------------------------
    # Element interaction wrappers
    # These wrap raw Playwright calls so your page objects stay readable.
    # Equivalent to tapElement(), typeText(), etc. in XCUITest helpers.
    # ------------------------------------------------------------------

    def click(self, locator: Locator):
        locator.click()

    def fill(self, locator: Locator, text: str):
        """Clear and type into a field."""
        locator.fill(text)

    def get_text(self, locator: Locator) -> str:
        return locator.inner_text()

    def is_visible(self, locator: Locator) -> bool:
        return locator.is_visible()

    def wait_for_visible(self, locator: Locator, timeout: int = 5000):
        """Wait up to timeout ms for element to appear."""
        locator.wait_for(state="visible", timeout=timeout)

    def wait_for_hidden(self, locator: Locator, timeout: int = 5000):
        locator.wait_for(state="hidden", timeout=timeout)

    def wait_for_url(self, pattern: str, timeout: int = 5000):
        """Wait until the URL matches a string or regex."""
        self.page.wait_for_url(re.compile(pattern), timeout=timeout)

    # ------------------------------------------------------------------
    # Assertions (wrap Playwright's expect() for reuse)
    # ------------------------------------------------------------------

    def assert_visible(self, locator: Locator):
        expect(locator).to_be_visible()

    def assert_text(self, locator: Locator, text: str):
        expect(locator).to_have_text(text)

    def assert_url_contains(self, fragment: str):
        expect(self.page).to_have_url(re.compile(fragment))

    def assert_title(self, title: str):
        expect(self.page).to_have_title(title)
