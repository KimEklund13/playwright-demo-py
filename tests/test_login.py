"""
tests/test_login.py — Login test suite
=======================================
Playwright test anatomy vs XCUITest:

  XCUITest                        Playwright/pytest
  --------                        -----------------
  func testLogin()                def test_login(login_page):
  XCTAssertTrue(...)              expect(locator).to_be_visible()
  setUp() / tearDown()            fixtures in conftest.py
  @testCase("smoke")              @pytest.mark.smoke
  XCUIApplication()               page (injected by pytest-playwright)

The `login_page` argument is a fixture defined in conftest.py.
pytest finds it by name — no import needed.
"""

import pytest


class TestLogin:
    """
    Group related tests in a class for organization.
    pytest collects any class starting with 'Test'.
    No need to inherit from anything (unlike XCTestCase).
    """

    @pytest.mark.smoke
    def test_valid_login(self, login_page):
        """Happy path: correct credentials → redirect to /secure."""
        login_page.navigate()
        login_page.login("tomsmith", "SuperSecretPassword!")
        login_page.assert_login_successful()

    @pytest.mark.smoke
    def test_invalid_password(self, login_page):
        """Wrong password → stay on /login, show error flash."""
        login_page.navigate()
        login_page.login("tomsmith", "wrongpassword")
        login_page.assert_login_failed()

    def test_invalid_username(self, login_page):
        """Unknown user → error flash."""
        login_page.navigate()
        login_page.login("nobody", "SuperSecretPassword!")
        login_page.assert_login_failed()

    def test_empty_credentials(self, login_page):
        """Submit with nothing filled in."""
        login_page.navigate()
        login_page.login("", "")
        login_page.assert_login_failed()

    @pytest.mark.regression
    def test_logout_after_login(self, login_page, home_page):
        """Full auth round-trip: login → land on /secure → logout → back to /login."""
        login_page.navigate()
        login_page.login("tomsmith", "SuperSecretPassword!")
        home_page.assert_on_page()
        home_page.logout()
        login_page.assert_url_contains("/login")
