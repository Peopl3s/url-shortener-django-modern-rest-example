from http import HTTPStatus
from typing import final, override

from django.http import HttpResponse
from dmr import APIRedirectError, Body, Controller, HeaderSpec, Path, modify
from dmr.endpoint import Endpoint
from dmr.errors import ErrorType
from dmr.metadata import ResponseSpec
from dmr.plugins.pydantic import PydanticSerializer

from apps.urlshortener.api.mappers import ShortLinkDtoMapper
from apps.urlshortener.api.schemas import (
    ShortLinkCreateSchema,
    ShortLinkPath,
    ShortLinkResponseSchema,
)
from apps.urlshortener.factories import (
    get_create_short_link_use_case,
    get_follow_short_link_use_case,
)
from apps.urlshortener.infrastructure.models import ShortLinkModel


@final
class ShortLinkController(Controller[PydanticSerializer]):
    """Controller for creating short links."""

    description = 'Short Link Controller'

    def post(
        self, body: Body[ShortLinkCreateSchema],
    ) -> ShortLinkResponseSchema:
        """Create a new short link from the given original URL."""
        usecase = get_create_short_link_use_case()
        short_link_entity = usecase(original_url=body.original_url)
        return ShortLinkDtoMapper()(short_link=short_link_entity)


@final
class RedirectController(Controller[PydanticSerializer]):
    """Controller for redirecting short links to original URLs."""

    description = 'Redirect Controller'

    @modify(
        extra_responses=[
            ResponseSpec(
                Controller.error_model,
                status_code=HTTPStatus.NOT_FOUND,
            ),
            ResponseSpec(
                None,
                status_code=HTTPStatus.FOUND,
                headers={'Location': HeaderSpec()},
            ),
        ],
        description='Redirect from short to original URL',
        tags=['Redirects'],
    )
    def get(self, path: Path[ShortLinkPath]) -> HttpResponse:
        """Redirect to the original URL for the given short code."""
        usecase = get_follow_short_link_use_case()
        original_url = usecase(short_code=path.short_code)
        raise APIRedirectError(
            redirect_to=original_url,
            status_code=HTTPStatus.FOUND,
        )

    @override
    def handle_error(
        self,
        endpoint: Endpoint,
        controller: Controller[PydanticSerializer],
        exc: Exception,
    ) -> HttpResponse:
        if isinstance(exc, ShortLinkModel.DoesNotExist):
            return self.to_error(
                self.format_error(
                    'Link not found',
                    error_type=ErrorType.not_found,
                ),
                status_code=HTTPStatus.NOT_FOUND,
            )
        return super().handle_error(
            endpoint,
            controller,
            exc,
        )
