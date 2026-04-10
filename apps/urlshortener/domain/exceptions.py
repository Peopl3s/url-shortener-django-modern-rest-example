from typing import final


@final
class ShortLinkNotFoundError(Exception):
    """Raised when a short link cannot be found by its short code."""

    def __init__(self, short_code: str) -> None:
        """Initialize with the missing short code."""
        super().__init__(f'Short link not found: {short_code}')
        self.short_code = short_code
