from abc import abstractmethod
from typing import Protocol

from apps.urlshortener.domain.models import ShortLinkEntity


class EncoderProtocol(Protocol):
    @abstractmethod
    def __call__(self, *, alphabet: str, number: int) -> str: ...


class ShortLinkRepositoryProtocol(Protocol):
    @abstractmethod
    def create(
        self, *, original_url: str, short_code: str,
    ) -> ShortLinkEntity: ...

    @abstractmethod
    def get_by_code(self, *, short_code: str) -> ShortLinkEntity | None: ...

    @abstractmethod
    def increment_clicks(self, *, short_code: str) -> None: ...


class LinkGeneratorProtocol(Protocol):
    @abstractmethod
    def __call__(self, *, length: int) -> str: ...
