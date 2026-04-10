# Запуск приложения

## Требования

| Инструмент | Версия |
|---|---|
| Python | 3.13.5 |
| uv | ≥ 0.6 |
| Docker | ≥ 26 |
| Docker Compose | ≥ 2.24 |

---

## Вариант 1 — локально (без Docker)

### 1. Установить зависимости

```bash
make install-dev
```

### 2. Применить миграции

```bash
make migrate
```

### 3. Запустить сервер

```bash
make run
```

Приложение доступно на http://localhost:8000

---

## Вариант 2 — Docker (режим разработки)

Исходный код монтируется в контейнер — изменения применяются без пересборки образа.

### 1. Запустить

```bash
make run-docker
```

Это выполняет `docker compose up --build`, который автоматически подхватывает
`docker-compose.override.yml` с настройками для разработки.

### 2. Остановить

```bash
make stop
```

---

## Вариант 3 — Docker (продакшн-режим)

Использует только `docker-compose.yml` без override.

### 1. Сгенерировать секретный ключ

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 2. Задать переменные окружения

Создать файл `.env` в корне проекта:

```env
DJANGO_SECRET_KEY=<сгенерированный-ключ>
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

Или экспортировать в текущем шелле:

```bash
export DJANGO_SECRET_KEY=<сгенерированный-ключ>
```

### 3. Запустить

```bash
make run-prod
```

---

## Доступные адреса

| URL | Описание |
|---|---|
| http://localhost:8000/api/ | POST — создать короткую ссылку |
| http://localhost:8000/api/`<code>`/ | GET — редирект по короткому коду |
| http://localhost:8000/docs/swagger/ | Swagger UI |
| http://localhost:8000/docs/openapi.json/ | OpenAPI схема |
| http://localhost:8000/admin/ | Панель администратора |

---

## Полезные команды

### Тесты и качество кода

```bash
make test          # запустить тесты с покрытием
make test-fast     # запустить тесты без покрытия (быстрее)
make lint          # проверить код ruff-ом (без исправлений)
make format        # авто-форматирование и исправление ruff-ом
make typecheck     # проверка типов mypy
make check         # всё сразу: lint + typecheck + test
```

### Миграции в Docker

```bash
make migrate-docker          # применить миграции
make makemigrations-docker   # создать новые файлы миграций
```

### Логи и отладка

```bash
make logs          # хвост логов всех контейнеров
make logs-web      # хвост логов только web-контейнера
make shell-docker  # sh-сессия внутри запущенного контейнера
make shell         # Django shell локально
```

### Очистка

```bash
make clean         # удалить __pycache__, .pytest_cache, htmlcov и т.д.
make clean-docker  # удалить контейнеры и volumes (удаляет данные БД!)
make clean-all     # всё вместе
```

Полный список команд: `make help`
