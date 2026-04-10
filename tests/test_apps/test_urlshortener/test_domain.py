import uuid
from datetime import UTC, datetime

import pytest

from apps.urlshortener.domain.constants import MAX_ORIGINAL_URL_LENGTH
from apps.urlshortener.domain.models import ShortLinkEntity
from apps.urlshortener.domain.services import Base64EncoderService


def _make_entity(**kwargs: object) -> ShortLinkEntity:
    defaults: dict[str, object] = {
        'uid': uuid.uuid4(),
        'original_url': 'https://example.com',
        'short_code': 'abc123',
        'created_at': datetime.now(tz=UTC),
    }
    defaults.update(kwargs)
    return ShortLinkEntity(**defaults)  # type: ignore[arg-type]


def test_entity_rejects_empty_url() -> None:
    """ShortLinkEntity should raise ValueError for an empty original_url."""
    with pytest.raises(ValueError, match='original_url cannot be empty'):
        _make_entity(original_url='')


def test_entity_rejects_url_exceeding_max_length() -> None:
    """ShortLinkEntity should raise ValueError when original_url is too long."""
    with pytest.raises(ValueError, match='original_url is too long'):
        _make_entity(original_url='x' * (MAX_ORIGINAL_URL_LENGTH + 1))


def test_base64_encoder_returns_first_char_for_zero() -> None:
    """Base64EncoderService should return the first alphabet character for 0."""
    encoder = Base64EncoderService()
    assert encoder(alphabet='abc', number=0) == 'a'
