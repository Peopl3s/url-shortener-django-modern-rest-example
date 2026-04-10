import uuid
from dataclasses import dataclass
from typing import LiteralString, final

from apps.urlshortener.domain.constants import SHORT_CODE_LENGTH
from apps.urlshortener.domain.intefaces import (
    EncoderProtocol,
    LinkGeneratorProtocol,
    ShortLinkRepositoryProtocol,
)
from apps.urlshortener.domain.models import ShortLinkEntity


@final
@dataclass(frozen=True, kw_only=True, slots=True)
class Base64EncoderService(EncoderProtocol):
    def __call__(self, *, alphabet: str, number: int) -> str:
        if number == 0:
            return alphabet[0]

        base = len(alphabet)
        result = []
        while number > 0:
            num, rem = divmod(number, base)
            result.append(alphabet[rem])

        return ''.join(reversed(result))


@final
@dataclass(frozen=True, kw_only=True, slots=True)
class ShortLinkGeneratorService(LinkGeneratorProtocol):
    alphabet: LiteralString
    encoder: EncoderProtocol

    def __call__(self, *, length: int) -> str:
        code = self.encoder(alphabet=self.alphabet, number=uuid.uuid4().int)
        return code[:length]


@final
@dataclass(frozen=True, kw_only=True, slots=True)
class CreateShortLinkUseCase:
    repository: ShortLinkRepositoryProtocol
    generator: LinkGeneratorProtocol

    def __call__(self, *, original_url: str) -> ShortLinkEntity:
        code = self.generator(length=SHORT_CODE_LENGTH)
        return self.repository.create(
            original_url=original_url, short_code=code,
        )


@final
@dataclass(frozen=True, kw_only=True, slots=True)
class FollowShortLinkUseCase:
    repository: ShortLinkRepositoryProtocol

    def __call__(self, *, short_code: str) -> str:
        short_link_entity = self.repository.get_by_code(short_code=short_code)
        self.repository.increment_clicks(short_code=short_code)
        return short_link_entity.original_url
