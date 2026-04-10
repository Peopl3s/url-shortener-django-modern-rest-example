from dataclasses import dataclass
from typing import final

from django.db.models import F

from apps.urlshortener.domain.intefaces import ShortLinkRepositoryProtocol
from apps.urlshortener.domain.models import ShortLinkEntity
from apps.urlshortener.infrastructure.mappers import ShortLinkMapper
from apps.urlshortener.infrastructure.models import ShortLinkModel


@final
@dataclass(frozen=True, slots=True)
class ShortLinkDjangoRepository(ShortLinkRepositoryProtocol):
    def create(self, *, original_url: str, short_code: str) -> ShortLinkEntity:
        obj = ShortLinkModel.objects.create(
            original_url=original_url, short_code=short_code,
        )
        return ShortLinkMapper()(obj_model=obj)

    def get_by_code(self, *, short_code: str) -> ShortLinkEntity | None:
        obj = ShortLinkModel.objects.get(short_code=short_code)
        return ShortLinkMapper()(obj_model=obj)

    def increment_clicks(self, *, short_code: str) -> None:
        ShortLinkModel.objects.filter(short_code=short_code).update(
            clicks=F('clicks') + 1,
        )
