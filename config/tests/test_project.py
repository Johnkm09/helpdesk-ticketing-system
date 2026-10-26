from django.conf import settings


def test_django_settings_are_loaded():
    assert settings.ROOT_URLCONF == "config.urls"
