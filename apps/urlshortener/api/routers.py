from dmr.routing import Router, path

from apps.urlshortener.api import controllers

router = Router(
    'shortener/',
    [
        path(
            '/',
            controllers.ShortLinkController.as_view(),
            name='create_link',
        ),
        path(
            '<str:short_code>/',
            controllers.RedirectController.as_view(),
            name='redirect_link',
        ),
    ],
)
