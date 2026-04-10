from dataclasses import dataclass
from typing import final

from apps.urlshortener.api.schemas import ShortLinkResponseSchema
from apps.urlshortener.domain.models import ShortLinkEntity


@final
@dataclass(frozen=True, slots=True)
class ShortLinkDtoMapper:
    """Maps ShortLinkEntity to ShortLinkResponseSchema."""

    def __call__(
        self, *, short_link: ShortLinkEntity,
    ) -> ShortLinkResponseSchema:
        """Convert a domain entity to an API response schema."""
        return ShortLinkResponseSchema(
            short_code=short_link.short_code,
            original_url=short_link.original_url,
            clicks=short_link.clicks,
        )
