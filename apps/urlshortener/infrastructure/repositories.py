from dataclasses import dataclass
from typing import final, override

from django.db import IntegrityError
from django.db.models import F

from apps.urlshortener.domain.exceptions import ShortCodeCollisionError
from apps.urlshortener.domain.interfaces import ShortLinkRepositoryProtocol
from apps.urlshortener.domain.models import ShortLinkEntity
from apps.urlshortener.infrastructure.mappers import ShortLinkMapper
from apps.urlshortener.infrastructure.models import ShortLinkModel


@final
@dataclass(frozen=True, slots=True)
class ShortLinkDjangoRepository(ShortLinkRepositoryProtocol):
    """Django ORM implementation of ShortLinkRepositoryProtocol."""

    @override
    def create(self, *, original_url: str, short_code: str) -> ShortLinkEntity:
        """Create and persist a new short link."""
        try:
            obj = ShortLinkModel.objects.create(
                original_url=original_url,
                short_code=short_code,
            )
        except IntegrityError as exc:
            raise ShortCodeCollisionError(short_code) from exc
        return ShortLinkMapper()(obj_model=obj)

    @override
    def get_by_code(self, *, short_code: str) -> ShortLinkEntity | None:
        """Retrieve a short link entity by its short code, or None if absent."""
        try:
            obj = ShortLinkModel.objects.get(short_code=short_code)
        except ShortLinkModel.DoesNotExist:
            return None
        return ShortLinkMapper()(obj_model=obj)

    @override
    def increment_clicks(self, *, short_code: str) -> None:
        """Increment the click counter for the given short code."""
        ShortLinkModel.objects.filter(short_code=short_code).update(
            clicks=F('clicks') + 1,
        )
