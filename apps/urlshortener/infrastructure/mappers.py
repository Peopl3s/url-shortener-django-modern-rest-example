from dataclasses import dataclass

from apps.urlshortener.domain.models import ShortLinkEntity
from apps.urlshortener.infrastructure.models import ShortLinkModel


@dataclass(frozen=True, slots=True)
class ShortLinkMapper:
    def __call__(self, *, obj_model: ShortLinkModel) -> ShortLinkEntity:
        return self.to_domain(obj_model)

    def to_domain(self, obj_model: ShortLinkModel) -> ShortLinkEntity:
        return ShortLinkEntity(
            uid=obj_model.uid,
            original_url=obj_model.original_url,
            short_code=obj_model.short_code,
            created_at=obj_model.created_at,
            clicks=obj_model.clicks,
        )

    def to_model(self, entity: ShortLinkEntity) -> ShortLinkModel:
        return ShortLinkModel(
            uid=entity.uid,
            original_url=entity.original_url,
            short_code=entity.short_code,
            clicks=entity.clicks,
        )
