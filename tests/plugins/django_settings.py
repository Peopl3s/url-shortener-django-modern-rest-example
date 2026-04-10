import pytest
from django.conf import LazySettings


@pytest.fixture(autouse=True)
def _debug(settings: LazySettings) -> None:
    """Sets proper DEBUG and TEMPLATE debug mode for coverage."""
    settings.DEBUG = False
    for template in settings.TEMPLATES:
        template['OPTIONS']['debug'] = True
