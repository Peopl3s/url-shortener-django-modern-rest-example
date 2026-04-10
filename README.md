# URL Shortener — django-modern-rest example

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![django-modern-rest](https://img.shields.io/badge/django--modern--rest-0.5.0-blueviolet)](https://django-modern-rest.readthedocs.io/en/latest/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![uv](https://img.shields.io/badge/uv-package%20manager-DE5FE9?logo=uv&logoColor=white)](https://docs.astral.sh/uv/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://docs.astral.sh/ruff/)
[![mypy](https://img.shields.io/badge/mypy-strict-2A6DB2?logo=python&logoColor=white)](https://mypy.readthedocs.io/)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](https://pytest-cov.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

REST API example built with Django and
[**django-modern-rest**](https://django-modern-rest.readthedocs.io/en/latest/),
following the architectural conventions of
[**wemake-django-template**](https://github.com/wemake-services/wemake-django-template).

The service accepts a long URL and returns a short code. Visiting the short code
redirects to the original URL and increments the click counter.

---

## Stack

| Layer | Tools |
|---|---|
| Language | Python 3.13 |
| Framework | Django 6 + [django-modern-rest](https://django-modern-rest.readthedocs.io/en/latest/) |
| Schemas / validation | Pydantic v2 |
| Database | SQLite (via Django ORM) |
| Server | Gunicorn (prod) / runserver (dev) |
| Package manager | [uv](https://docs.astral.sh/uv/) |
| Linter / formatter | [ruff](https://docs.astral.sh/ruff/) |
| Type checking | mypy (strict) + django-stubs |
| Tests | pytest + pytest-django + schemathesis |
| Containerisation | Docker + Docker Compose (dev / prod) |

---

## Project structure

```
dmr-urlshortener-example/
│
├── manage.py
├── pyproject.toml          # dependencies, mypy, ruff, pytest config
├── Makefile                # all commands in one place
├── Dockerfile
├── docker-compose.yml          # production
├── docker-compose.override.yml # dev (applied automatically)
│
├── config/                 # Django configuration
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── apps/
│   └── urlshortener/
│       │
│       ├── api/            # HTTP layer (dmr)
│       │   ├── controllers.py  # Controller classes (POST /links, GET /{code})
│       │   ├── schemas.py      # Pydantic request / response schemas
│       │   ├── mappers.py      # Entity → Response DTO
│       │   └── routers.py      # route registration
│       │
│       ├── domain/         # business logic (no Django dependencies)
│       │   ├── models.py       # ShortLinkEntity (dataclass)
│       │   ├── services.py     # use cases + short-code generation services
│       │   ├── interfaces.py   # Protocol interfaces
│       │   └── constants.py
│       │
│       ├── infrastructure/ # database layer
│       │   ├── models.py       # Django ORM models
│       │   ├── repositories.py # repository implementation
│       │   └── mappers.py      # ORM model ↔ Entity
│       │
│       ├── migrations/     # standard Django migrations
│       ├── factories.py    # dependency factories (DI)
│       ├── admin.py
│       └── apps.py
│
├── common/                 # shared utilities across apps
│
└── tests/
    ├── conftest.py
    ├── plugins/
    │   └── django_settings.py
    └── test_apps/
        └── test_urlshortener/
            ├── test_api.py     # HTTP integration tests
            ├── test_domain.py  # business logic unit tests
            ├── test_models.py
            └── test_schema.py
```

### Architecture layers

```
HTTP request
    │
    ▼
┌─────────────────────────────────┐
│  api/  (controllers, schemas)   │  ← HTTP only: parsing, serialisation
└─────────────────┬───────────────┘
                  │ calls use case
                  ▼
┌─────────────────────────────────┐
│  domain/  (services, models)    │  ← business rules, no Django imports
└─────────────────┬───────────────┘
                  │ via Protocol interface
                  ▼
┌─────────────────────────────────┐
│  infrastructure/ (repositories) │  ← ORM, SQL, external services
└─────────────────────────────────┘
```

---

## Quick start

### Local (without Docker)

**Requirements:** Python 3.13, [uv](https://docs.astral.sh/uv/)

```bash
# 1. Clone and enter the directory
git clone <repo-url> && cd dmr-urlshortener-example

# 2. Install dependencies
make install-dev

# 3. Apply migrations
make migrate

# 4. Run the development server
make run
```

The service is available at [http://localhost:8000](http://localhost:8000).
OpenAPI schema — [http://localhost:8000/docs/openapi.json/](http://localhost:8000/docs/openapi.json/).

---

### Docker (recommended)

**Requirements:** Docker, Docker Compose

```bash
# Development mode (hot-reload, dev dependencies inside the container)
make run-docker

# Production mode (gunicorn, no dev dependencies)
DJANGO_SECRET_KEY=<secret> make run-prod
```

> Both modes run `migrate` automatically on startup.

---

### Example requests

```bash
# Create a short link
curl -X POST http://localhost:8000/links/ \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://example.com/very/long/path"}'

# Response:
# {"short_code": "aB3xZ9", "original_url": "https://example.com/very/long/path", "clicks": 0}

# Follow a short link (returns 302 → original_url)
curl -L http://localhost:8000/aB3xZ9/
```

---

## Development commands

```bash
make help           # list all available commands

make test           # run full test suite with coverage
make test-fast      # run tests without coverage (faster feedback)
make lint           # ruff check without auto-fix
make format         # auto-format with ruff
make typecheck      # strict mypy check
make check          # lint + typecheck + test in one command

make migrate        # apply migrations locally
make makemigrations # create new migrations
make shell          # open Django shell
```

---

## Links

- [django-modern-rest — documentation](https://django-modern-rest.readthedocs.io/en/latest/)
- [wemake-django-template — GitHub](https://github.com/wemake-services/wemake-django-template)
- [uv — documentation](https://docs.astral.sh/uv/)
- [ruff — documentation](https://docs.astral.sh/ruff/)
