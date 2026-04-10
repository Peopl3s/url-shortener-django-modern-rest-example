import contextlib
import uuid
from datetime import UTC, datetime

import pytest

from apps.urlshortener.domain.constants import (
    MAX_ORIGINAL_URL_LENGTH,
    SHORT_CODE_LENGTH,
    SHORT_CODE_MAX_RETRIES,
)
from apps.urlshortener.domain.exceptions import (
    ShortCodeCollisionError,
    ShortLinkNotFoundError,
)
from apps.urlshortener.domain.models import ShortLinkEntity
from apps.urlshortener.domain.services import (
    Base64EncoderService,
    CreateShortLinkUseCase,
    FollowShortLinkUseCase,
    ShortLinkGeneratorService,
)


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
    """Store the colliding code and format the message."""
    err = ShortCodeCollisionError('xyz99')
    assert err.short_code == 'xyz99'
    assert str(err) == 'Short code collision: xyz99'


def test_create_short_link_use_case_falls_through_to_last_retry() -> None:
    """Execute the final attempt after all loop retries fail."""
    entity = _make_entity()
    call_count = 0

    class _StubRepository:
        def create(
            self,
            *,
            original_url: str,
            short_code: str,
        ) -> ShortLinkEntity:
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


def test_create_short_link_use_case_success() -> None:
    """Return entity immediately on first successful create."""
    entity = _make_entity()
    generator_lengths: list[int] = []

    class _StubRepository:
        def create(
            self,
            *,
            original_url: str,
            short_code: str,
        ) -> ShortLinkEntity:
            return entity

    use_case = CreateShortLinkUseCase(
        repository=_StubRepository(),  # type: ignore[arg-type]
        generator=lambda *, length: (
            generator_lengths.append(length),
            'abc12345',
        )[1],  # type: ignore[arg-type]
    )
    result = use_case(original_url='https://example.com')

    assert result == entity
    assert generator_lengths == [SHORT_CODE_LENGTH]


def test_follow_short_link_use_case_returns_original_url() -> None:
    """Return original_url and increment clicks."""
    entity = _make_entity(original_url='https://example.com')
    incremented: list[str] = []

    class _StubRepository:
        def get_by_code(self, *, short_code: str) -> ShortLinkEntity | None:
            return entity

        def increment_clicks(self, *, short_code: str) -> None:
            incremented.append(short_code)

    use_case = FollowShortLinkUseCase(
        repository=_StubRepository(),  # type: ignore[arg-type]
        transaction=contextlib.nullcontext,  # type: ignore[arg-type]
    )
    result = use_case(short_code='abc12345')

    assert result == 'https://example.com'
    assert incremented == ['abc12345']


def test_follow_short_link_use_case_raises_when_not_found() -> None:
    """Raise ShortLinkNotFoundError when code is unknown."""

    class _StubRepository:
        def get_by_code(self, *, short_code: str) -> ShortLinkEntity | None:
            return None

    use_case = FollowShortLinkUseCase(
        repository=_StubRepository(),  # type: ignore[arg-type]
        transaction=contextlib.nullcontext,  # type: ignore[arg-type]
    )
    with pytest.raises(ShortLinkNotFoundError) as exc_info:
        use_case(short_code='missing')

    assert exc_info.value.short_code == 'missing'
    assert str(exc_info.value) == 'Short link not found: missing'


def test_short_link_generator_returns_correct_length() -> None:
    """Return a code of exactly the requested length."""
    generator = ShortLinkGeneratorService(
        alphabet='abcdefghijklmnopqrstuvwxyz0123456789',
        encoder=Base64EncoderService(),
    )
    code = generator(length=SHORT_CODE_LENGTH)

    assert len(code) == SHORT_CODE_LENGTH


def test_short_link_generator_uses_encoder_and_alphabet() -> None:
    """Pass its alphabet and a UUID int to the encoder."""
    received: list[dict[str, object]] = []

    def _stub_encoder(*, alphabet: str, number: int) -> str:
        received.append({'alphabet': alphabet, 'number': number})
        return 'x' * 20

    alphabet = 'abc123'
    generator = ShortLinkGeneratorService(
        alphabet=alphabet,
        encoder=_stub_encoder,  # type: ignore[arg-type]
    )
    result = generator(length=5)

    assert len(received) == 1
    assert received[0]['alphabet'] == alphabet
    assert isinstance(received[0]['number'], int)
    assert result == 'xxxxx'
