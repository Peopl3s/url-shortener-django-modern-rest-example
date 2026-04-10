from typing import final

import pydantic

from apps.urlshortener.domain.constants import MAX_ORIGINAL_URL_LENGTH


@final
class ShortLinkCreateSchema(pydantic.BaseModel):
    """Schema for creating a new short link."""

    original_url: str = pydantic.Field(
        json_schema_extra={
            'minLength': 1,
            'maxLength': MAX_ORIGINAL_URL_LENGTH,
            'pattern': '^https?://',
            'example': 'https://github.com/wemake-services/wemake-django-template',
        },
    )


@final
class ShortLinkResponseSchema(pydantic.BaseModel):
    """Schema for a short link API response."""

    short_code: str
    original_url: str
    clicks: int


@final
class ShortLinkPath(pydantic.BaseModel):
    """Schema for short link path parameters."""

    short_code: str
