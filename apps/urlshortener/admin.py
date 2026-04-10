from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from apps.urlshortener.infrastructure.models import ShortLinkModel


@admin.register(ShortLinkModel)
class ShortLinkAdmin(admin.ModelAdmin):
    list_display = [
        'short_code_link',
        'original_url_truncated',
        'clicks',
        'created_at',
    ]
    list_display_links = ['short_code_link']

    list_filter = ['created_at']
    search_fields = ['short_code', 'original_url']

    readonly_fields = ['uid', 'clicks', 'created_at', 'full_short_url']

    fieldsets = [
        (
            'General information',
            {
                'fields': [
                    'short_code',
                    'original_url',
                    'full_short_url',
                ],
            },
        ),
        (
            'Stats and tech data',
            {
                'fields': [
                    'clicks',
                    'created_at',
                    'uid',
                ],
                'classes': ['collapse'],
            },
        ),
    ]

    @admin.display(description='Original URL')
    def original_url_truncated(self, obj: ShortLinkModel):
        if len(obj.original_url) > 50:
            return obj.original_url[:47] + '...'
        return obj.original_url

    @admin.display(description='Full short URL')
    def full_short_url(self, obj: ShortLinkModel):
        from django.conf import settings

        domain = getattr(settings, 'SHORTENER_DOMAIN', 'http://127.0.0.1:8000')
        url = f'{domain.rstrip("/")}/{obj.short_code}'
        return f'<a href="{url}" target="_blank">{url}</a>'

    @admin.action(description='Reset URL clicks', permissions=['change'])
    def reset_clicks_count(
        self, request: HttpRequest, queryset: QuerySet[ShortLinkModel],
    ):
        updated = queryset.update(clicks=0)
        self.message_user(
            request, f'Clicks counter has been reset - {updated}.',
        )
