from http import HTTPStatus

import pytest
from django.urls import reverse
from dmr.test import DMRClient

from apps.urlshortener.api.schemas import ShortLinkResponseSchema
from apps.urlshortener.domain.exceptions import ShortCodeCollisionError
from apps.urlshortener.infrastructure.models import ShortLinkModel
from apps.urlshortener.infrastructure.repositories import (
    ShortLinkDjangoRepository,
)


@pytest.fixture
def short_link() -> ShortLinkModel:
    """Create a ShortLinkModel instance for testing."""
    return ShortLinkModel.objects.create(
        original_url='https://example.com',
        short_code='abc123',
    )


@pytest.mark.django_db
def test_create_short_link(dmr_client: DMRClient) -> None:
    """Ensures that a short link can be created via the API."""
    original_url = 'https://example.com/some/long/path'

    response = dmr_client.post(
        reverse('shortener:create_link'),
        data={'original_url': original_url},
    )

    assert response.status_code == HTTPStatus.CREATED
    payload = ShortLinkResponseSchema.model_validate(response.json())
    assert payload.original_url == original_url
    assert payload.clicks == 0
    assert ShortLinkModel.objects.filter(
        short_code=payload.short_code,
    ).exists()


@pytest.mark.django_db
def test_redirect_short_link(
    dmr_client: DMRClient,
    short_link: ShortLinkModel,
) -> None:
    """Ensures that a short link redirects to the original URL."""
    response = dmr_client.get(
        reverse(
            'shortener:redirect_link',
            kwargs={'short_code': short_link.short_code},
        ),
    )

    assert response.status_code == HTTPStatus.FOUND
    assert response['Location'] == short_link.original_url


@pytest.mark.django_db
def test_redirect_short_link_increments_clicks(
    dmr_client: DMRClient,
    short_link: ShortLinkModel,
) -> None:
    """Ensures that following a short link increments the click counter."""
    dmr_client.get(
        reverse(
            'shortener:redirect_link',
            kwargs={'short_code': short_link.short_code},
        ),
    )

    short_link.refresh_from_db()
    assert short_link.clicks == 1


@pytest.mark.django_db
def test_create_short_link_with_empty_url(dmr_client: DMRClient) -> None:
    """Ensures that an empty original_url returns 400."""
    response = dmr_client.post(
        reverse('shortener:create_link'),
        data={'original_url': ''},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.django_db
def test_redirect_short_link_not_found(dmr_client: DMRClient) -> None:
    """Ensures that a missing short link returns 404."""
    response = dmr_client.get(
        reverse(
            'shortener:redirect_link',
            kwargs={'short_code': 'nonexistent'},
        ),
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        'detail': [{'msg': 'Link not found', 'type': 'not_found'}],
    }


@pytest.mark.django_db
def test_create_short_link_collision_returns_409(
    dmr_client: DMRClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ensures that a ShortCodeCollisionError from the use case returns 409."""

    def _failing_usecase(*, original_url: str) -> None:
        raise ShortCodeCollisionError('abc12345')

    monkeypatch.setattr(
        'apps.urlshortener.api.controllers.get_create_short_link_use_case',
        lambda: _failing_usecase,
    )
    response = dmr_client.post(
        reverse('shortener:create_link'),
        data={'original_url': 'https://example.com'},
    )
    assert response.status_code == HTTPStatus.CONFLICT


@pytest.mark.django_db
def test_repository_create_raises_on_duplicate_short_code() -> None:
    """Create should raise ShortCodeCollisionError on IntegrityError."""
    ShortLinkModel.objects.create(
        original_url='https://a.com',
        short_code='dup001x',
    )
    repo = ShortLinkDjangoRepository()
    with pytest.raises(ShortCodeCollisionError):
        repo.create(original_url='https://b.com', short_code='dup001x')
