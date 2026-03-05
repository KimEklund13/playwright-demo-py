"""
pages/home_page.py — Home / Secure Page Object
================================================
Represents the /secure page (post-login landing).
"""

from pages.base_page import BasePage
from playwright.sync_api import Page


class HomePage(BasePage):

    URL = "/secure"

    def __init__(self, page: Page):
        super().__init__(page)

        self.welcome_header = page.locator("h2")
        self.logout_button = page.get_by_role("link", name="Logout")

    def navigate(self):
        super().navigate(self.URL)

    def logout(self):
        self.click(self.logout_button)

    def get_welcome_text(self) -> str:
        return self.get_text(self.welcome_header)

    def assert_on_page(self):
        self.assert_url_contains("/secure")
        self.assert_visible(self.welcome_header)
