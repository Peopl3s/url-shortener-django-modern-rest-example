from abc import abstractmethod
from typing import Protocol

from apps.urlshortener.domain.models import ShortLinkEntity


class EncoderProtocol(Protocol):
    """Protocol for encoding a number into a short string."""

    @abstractmethod
    def __call__(self, *, alphabet: str, number: int) -> str:
        """Encode the number into a string using the given alphabet."""
        ...


class ShortLinkRepositoryProtocol(Protocol):
    """Protocol for short link persistence operations."""

    @abstractmethod
    def create(
        self, *, original_url: str, short_code: str,
    ) -> ShortLinkEntity:
        """Create and persist a new short link."""
        ...

    @abstractmethod
    def get_by_code(self, *, short_code: str) -> ShortLinkEntity | None:
        """Retrieve a short link entity by its short code."""
        ...

    @abstractmethod
    def increment_clicks(self, *, short_code: str) -> None:
        """Increment the click counter for the given short code."""
        ...


class LinkGeneratorProtocol(Protocol):
    """Protocol for generating short link codes."""

    @abstractmethod
    def __call__(self, *, length: int) -> str:
        """Generate a short code of the specified length."""
        ...
