import uuid
from datetime import UTC, datetime

import pytest

from apps.urlshortener.domain.constants import MAX_ORIGINAL_URL_LENGTH, SHORT_CODE_MAX_RETRIES
from apps.urlshortener.domain.exceptions import ShortCodeCollisionError
from apps.urlshortener.domain.models import ShortLinkEntity
from apps.urlshortener.domain.services import Base64EncoderService, CreateShortLinkUseCase


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


def test_short_code_collision_error_stores_code() -> None:
    """ShortCodeCollisionError should store the colliding code and format the message."""
    err = ShortCodeCollisionError('xyz99')
    assert err.short_code == 'xyz99'
    assert str(err) == 'Short code collision: xyz99'


def test_create_short_link_use_case_falls_through_to_last_retry() -> None:
    """CreateShortLinkUseCase should execute the final attempt after all loop retries fail."""
    entity = _make_entity()
    call_count = 0

    class _StubRepository:
        def create(self, *, original_url: str, short_code: str) -> ShortLinkEntity:
            nonlocal call_count
            call_count += 1
            if call_count < SHORT_CODE_MAX_RETRIES:
                raise ShortCodeCollisionError(short_code)
            return entity

    use_case = CreateShortLinkUseCase(
        repository=_StubRepository(),  # type: ignore[arg-type]
        generator=lambda *, length: 'abc12345',  # type: ignore[arg-type]
    )
    result = use_case(original_url='https://example.com')

    assert result == entity
    assert call_count == SHORT_CODE_MAX_RETRIES
