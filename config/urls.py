from django.contrib import admin
from django.urls import include, path
from dmr.openapi import build_schema
from dmr.openapi.views import OpenAPIJsonView, SwaggerView

from apps.urlshortener.api.routers import router as urlshortener_router

schema = build_schema(urlshortener_router)

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'api/shortener/',
        include((urlshortener_router.urls, 'shortener'), namespace='shortener'),
    ),
    path('docs/openapi.json/', OpenAPIJsonView.as_view(schema), name='openapi'),
    path('docs/swagger/', SwaggerView.as_view(schema)),
]
