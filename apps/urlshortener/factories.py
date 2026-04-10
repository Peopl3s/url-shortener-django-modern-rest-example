import string
from typing import LiteralString

from apps.urlshortener.domain.services import (
    Base64EncoderService,
    CreateShortLinkUseCase,
    FollowShortLinkUseCase,
    ShortLinkGeneratorService,
)
from apps.urlshortener.infrastructure.repositories import (
    ShortLinkDjangoRepository,
)


def get_base64_ascii_shortlink_generator() -> ShortLinkGeneratorService:
    alphabet: LiteralString = string.ascii_letters + string.digits
    return ShortLinkGeneratorService(
        alphabet=alphabet, encoder=Base64EncoderService(),
    )


def get_create_short_link_use_case() -> CreateShortLinkUseCase:
    return CreateShortLinkUseCase(
        repository=ShortLinkDjangoRepository(),
        generator=get_base64_ascii_shortlink_generator(),
    )


def get_follow_short_link_use_case() -> FollowShortLinkUseCase:
    return FollowShortLinkUseCase(repository=ShortLinkDjangoRepository())
