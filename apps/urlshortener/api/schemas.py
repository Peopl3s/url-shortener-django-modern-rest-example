from typing import final

import pydantic


@final
class ShortLinkCreateSchema(pydantic.BaseModel):
    original_url: str = pydantic.Field(
        json_schema_extra={
            'example': 'https://github.com/wemake-services/wemake-django-template',
        },
    )


@final
class ShortLinkResponseSchema(pydantic.BaseModel):
    short_code: str
    original_url: str
    clicks: int


@final
class ShortLinkPath(pydantic.BaseModel):
    short_code: str
