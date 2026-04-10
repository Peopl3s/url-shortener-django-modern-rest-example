import uuid

from django.db import models

from apps.urlshortener.domain.constants import MAX_ORIGINAL_URL_LENGTH


class ShortLinkModel(models.Model):
    """Django ORM model for a short link."""

    uid = models.UUIDField(verbose_name='UUID', default=uuid.uuid4, unique=True)
    original_url = models.URLField(
        verbose_name='original URL', max_length=MAX_ORIGINAL_URL_LENGTH,
    )
    short_code = models.CharField(verbose_name='short url code', unique=True)
    created_at = models.DateTimeField(
        verbose_name='created date', auto_now_add=True,
    )
    clicks = models.PositiveIntegerField(verbose_name='clicks count', default=0)

    class Meta:
        verbose_name = 'short link'
        verbose_name_plural = 'short links'
        ordering = ('-created_at',)
        indexes = (
            models.Index(fields=['short_code']),
            models.Index(fields=['-created_at']),
        )

    def __str__(self) -> str:
        """Return short code as string representation."""
        return self.short_code
