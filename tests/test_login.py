import pytest
from qase.pytest import qase


class TestLogin:

    @pytest.fixture(autouse=True)
    def setup(self, login_page, home_page):
        self.login = login_page
        self.home = home_page
        self.valid_user = "tomsmith"
        self.valid_password = "SuperSecretPassword!"

    @qase.id(1)
    @pytest.mark.smoke
    def test_valid_login(self):
        """Happy path: correct credentials → redirect to /secure."""
        self.login.navigate()
        self.login.login(self.valid_user, self.valid_password)
        self.login.assert_login_successful()

    @qase.id(2)
    @pytest.mark.smoke
    def test_invalid_password(self):
        """Wrong password → stay on /login, show error flash."""
        self.login.navigate()
        self.login.login(self.valid_user, "wrongpassword")
        self.login.assert_login_failed()

    @qase.id(3)
    def test_invalid_username(self):
        """Unknown user → error flash."""
        self.login.navigate()
        self.login.login("nobody", self.valid_password)
        self.login.assert_login_failed()

    @qase.id(4)
    def test_empty_credentials(self):
        """Submit with nothing filled in."""
        self.login.navigate()
        self.login.login("", "")
        self.login.assert_login_failed()

    @qase.id(5)
    @pytest.mark.regression
    def test_logout_after_login(self):
        """Full auth round-trip: login → /secure → logout → /login."""
        self.login.navigate()
        self.login.login(self.valid_user, self.valid_password)
        self.home.assert_on_page()
        self.home.logout()
        self.login.assert_url_contains("/login")