import string
from typing import LiteralString

from django.db import transaction

from apps.urlshortener.domain.services import (
    Base64EncoderService,
    CreateShortLinkUseCase,
    FollowShortLinkUseCase,
    ShortLinkGeneratorService,
)
from apps.urlshortener.infrastructure.repositories import (
    ShortLinkDjangoRepository,
)

# Check normal DI here:
# https://github.com/wemake-services/wemake-django-template/blob/master/%7B%7Bcookiecutter.project_name%7D%7D/server/common/di.py


def get_base64_ascii_shortlink_generator() -> ShortLinkGeneratorService:
    """Build a ShortLinkGeneratorService with ASCII alphabet."""
    alphabet: LiteralString = string.ascii_letters + string.digits
    return ShortLinkGeneratorService(
        alphabet=alphabet,
        encoder=Base64EncoderService(),
    )


def get_create_short_link_use_case() -> CreateShortLinkUseCase:
    """Build the CreateShortLinkUseCase with default dependencies."""
    return CreateShortLinkUseCase(
        repository=ShortLinkDjangoRepository(),
        generator=get_base64_ascii_shortlink_generator(),
    )


def get_follow_short_link_use_case() -> FollowShortLinkUseCase:
    """Build the FollowShortLinkUseCase with default dependencies."""
    return FollowShortLinkUseCase(
        repository=ShortLinkDjangoRepository(),
        transaction=transaction.atomic,
    )
