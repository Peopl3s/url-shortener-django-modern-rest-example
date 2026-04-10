import logging
from collections.abc import Iterator

import pytest
import schemathesis as st
from django.conf import LazySettings
from django.urls import reverse
from schemathesis.specs.openapi.schemas import OpenApiSchema

from config.wsgi import application


@pytest.fixture(autouse=True)
def _disable_logging(settings: LazySettings) -> Iterator[None]:
    settings.DQC_ENABLED = False
    logging.disable(logging.CRITICAL)
    yield
    logging.disable(logging.NOTSET)


@pytest.fixture
def api_schema(
    transactional_db: None,
) -> 'OpenApiSchema':
    """Load OpenAPI schema as a pytest fixture."""
    return st.openapi.from_wsgi(reverse('openapi'), application)


schema = st.pytest.from_fixture('api_schema')


@pytest.mark.timeout(60)
@schema.parametrize()
def test_schemathesis(settings: LazySettings, *, case: st.Case) -> None:
    """Ensure that API implementation matches the OpenAPI schema."""
    case.call_and_validate()
