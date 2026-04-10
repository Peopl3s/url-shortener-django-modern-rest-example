import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import final

from apps.urlshortener.domain.constants import MAX_ORIGINAL_URL_LENGTH


@final
@dataclass(frozen=True, kw_only=True, slots=True)
class ShortLinkEntity:
    """Domain entity representing a short link."""

    uid: uuid.UUID
    original_url: str
    short_code: str
    created_at: datetime
    clicks: int = 0

    def __post_init__(self) -> None:
        """Validate entity fields after initialization."""
        if len(self.original_url) == 0:
            raise ValueError('original_url cannot be empty')

        if len(self.original_url) > MAX_ORIGINAL_URL_LENGTH:
            raise ValueError(
                f'original_url is too long. Maximum allowed length is '
                f'{MAX_ORIGINAL_URL_LENGTH} characters '
                f'(got {len(self.original_url)})',
            )

        if not self.original_url.startswith(('http://', 'https://')):
            raise ValueError(
                'original_url must start with http:// or https://',
            )
