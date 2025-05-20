import pytest


@pytest.mark.django_db
class TestUserFactory:

    def test_generates_password_if_not_provided(self, user_factory):
        user = user_factory()
        assert user.has_usable_password()

    def test_uses_provided_password(self, user_factory):
        password = "qwerty1337"
        user = user_factory(password=password)
        assert user.check_password(password)