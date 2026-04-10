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
from apps.urlshortener.domain.exceptions import (
    ShortCodeCollisionError,
    ShortLinkNotFoundError,
)
from apps.urlshortener.factories import (
    get_create_short_link_use_case,
    get_follow_short_link_use_case,
)


@final
class ShortLinkController(Controller[PydanticSerializer]):
    """Controller for creating short links."""

    description = 'Short Link Controller'

    @modify(
        extra_responses=[
            ResponseSpec(
                Controller.error_model,
                status_code=HTTPStatus.BAD_REQUEST,
            ),
            ResponseSpec(
                Controller.error_model,
                status_code=HTTPStatus.CONFLICT,
            ),
        ],
    )
    def post(
        self,
        parsed_body: Body[ShortLinkCreateSchema],
    ) -> ShortLinkResponseSchema:
        """Create a new short link from the given original URL."""
        usecase = get_create_short_link_use_case()
        short_link_entity = usecase(original_url=parsed_body.original_url)
        return ShortLinkDtoMapper()(short_link=short_link_entity)

    @override
    def handle_error(
        self,
        endpoint: Endpoint,
        controller: Controller[PydanticSerializer],
        exc: Exception,
    ) -> HttpResponse:
        if isinstance(exc, ValueError):
            return self.to_error(
                self.format_error(
                    str(exc),
                    error_type=ErrorType.value_error,
                ),
                status_code=HTTPStatus.BAD_REQUEST,
            )
        if isinstance(exc, ShortCodeCollisionError):
            return self.to_error(
                self.format_error(
                    'Failed to generate a unique short code, please retry',
                    error_type=ErrorType.value_error,
                ),
                status_code=HTTPStatus.CONFLICT,
            )
        return super().handle_error(  # pragma: no cover
            endpoint,
            controller,
            exc,
        )


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
    def get(self, parsed_path: Path[ShortLinkPath]) -> None:
        """Redirect to the original URL for the given short code."""
        usecase = get_follow_short_link_use_case()
        original_url = usecase(short_code=parsed_path.short_code)
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
        if isinstance(exc, ShortLinkNotFoundError):
            return self.to_error(
                self.format_error(
                    'Link not found',
                    error_type=ErrorType.not_found,
                ),
                status_code=HTTPStatus.NOT_FOUND,
            )
        return super().handle_error(  # pragma: no cover
            endpoint,
            controller,
            exc,
        )
