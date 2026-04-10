import contextlib
import uuid
from dataclasses import dataclass
from typing import LiteralString, final, override

from apps.urlshortener.domain.constants import (
    SHORT_CODE_LENGTH,
    SHORT_CODE_MAX_RETRIES,
)
from apps.urlshortener.domain.exceptions import (
    ShortCodeCollisionError,
    ShortLinkNotFoundError,
)
from apps.urlshortener.domain.interfaces import (
    EncoderProtocol,
    LinkGeneratorProtocol,
    ShortLinkRepositoryProtocol,
    TransactionProtocol,
)
from apps.urlshortener.domain.models import ShortLinkEntity


@final
@dataclass(frozen=True, kw_only=True, slots=True)
class Base64EncoderService(EncoderProtocol):
    """Encodes an integer into a base-N string using a given alphabet."""

    @override
    def __call__(self, *, alphabet: str, number: int) -> str:
        """Encode the given number using the provided alphabet."""
        if number == 0:
            return alphabet[0]

        base = len(alphabet)
        result = []
        while number > 0:
            number, rem = divmod(number, base)
            result.append(alphabet[rem])

        return ''.join(reversed(result))


@final
@dataclass(frozen=True, kw_only=True, slots=True)
class ShortLinkGeneratorService(LinkGeneratorProtocol):
    """Generates a short code of a given length from a UUID."""

    alphabet: LiteralString
    encoder: EncoderProtocol

    @override
    def __call__(self, *, length: int) -> str:
        """Generate a short code of the specified length."""
        code = self.encoder(alphabet=self.alphabet, number=uuid.uuid4().int)
        return code[:length]


@final
@dataclass(frozen=True, kw_only=True, slots=True)
class CreateShortLinkUseCase:
    """Use case for creating a new short link."""

    repository: ShortLinkRepositoryProtocol
    generator: LinkGeneratorProtocol

    def __call__(self, *, original_url: str) -> ShortLinkEntity:
        """Create and persist a short link for the given URL."""
        for _ in range(SHORT_CODE_MAX_RETRIES - 1):
            with contextlib.suppress(ShortCodeCollisionError):
                return self.repository.create(
                    original_url=original_url,
                    short_code=self.generator(length=SHORT_CODE_LENGTH),
                )
        return self.repository.create(
            original_url=original_url,
            short_code=self.generator(length=SHORT_CODE_LENGTH),
        )


@final
@dataclass(frozen=True, kw_only=True, slots=True)
class FollowShortLinkUseCase:
    """Use case for following a short link to its original URL."""

    repository: ShortLinkRepositoryProtocol
    transaction: TransactionProtocol

    def __call__(self, *, short_code: str) -> str:
        """Resolve a short code to its original URL and record the click."""
        with self.transaction():
            short_link_entity = self.repository.get_by_code(
                short_code=short_code,
            )
            if short_link_entity is None:
                raise ShortLinkNotFoundError(short_code)
            self.repository.increment_clicks(short_code=short_code)
            return short_link_entity.original_url
