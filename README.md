https://habr.com/ru/articles/883578/

https://django-modern-rest.readthedocs.io/en/latest/

`mkdir dmr-example && cd dmr-example`

`pyenv --version`

`pyenv install -l`

`pyenv install 3.13.5`

`pip install uv`

`uv init`

`pyenv local 3.13.5`

`uv venv`

`source .venv/bin/activate`

![img.png](img.png)

`uv add django`

`uv add django-modern-rest`

`uv add django-stubs-ext`

`uv add --dev 'django-stubs[compatible-mypy]'`

`uv add --dev ruff pytest pytest-django schemathesis pydantic`

`uv add --group docs sphinx`

`uv add structlog gunicorn`

`django-admin startproject config .`

Добавляем в pyproject.toml:
```
[tool.mypy]
plugins = ["config.main"]

[tool.django-stubs]
django_settings_module = "config.settings"
```

```
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dmr',
]
```


```
dmr-example/
│
├── manage.py
├── pyproject.toml
│
├── config/                  # Django конфиг
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── asgi.py / wsgi.py
│
├── apps/                    # Все приложения
│   └── users/
│       ├── __init__.py
│       │
│       ├── api/             # HTTP слой (dmr)
│       │   ├── controllers.py
│       │   ├── schemas.py
│       │   └── router.py
│       │
│       ├── domain/          # Бизнес-логика
│       │   ├── models.py
│       │   └── services.py
│       │
│       ├── infrastructure/  # Работа с БД, внешними сервисами
│       │   ├── repositories.py
│       │   └── mappers.py
│       │
│       └── apps.py
├── tests/
│   ├── conftest.py       # общий для всех приложений
│   ├── utils.py          # общие тестовые утилиты
│   └── users/
│       └── test_api.py
└── common/                  # Общие утилиты
    └── di.py
```

Проблема в том, что PyCharm не видит виртуальное окружение .venv, созданное через uv. Нужно указать его вручную.                                                                                               
                                                                                                                                                                                                                 
  Как исправить                                                                                                                                                                                                  
                                                                                                                                                                                                                 
  Settings → Project → Python Interpreter → Add Interpreter → Add Local Interpreter                                                                                                                              
                                                                                                                                                                                                                 
  Выбери Existing и укажи путь к интерпретатору:                                                                                                                                                                 
  /Users/maximmelnikov/Desktop/drm-example/.venv/bin/python                                                                                                                                                      
                                                                                                                                                                                                                 
  Пошагово:                                                                                                                                                                                                      
                                                                                                                                                                                                                 
  1. PyCharm → Settings (⌘,) → Project: drm-example → Python Interpreter                                                                                                                                         
  2. Нажми шестерёнку → Add Interpreter → Add Local Interpreter
  3. Выбери Existing → путь: .venv/bin/python3.13 в корне проекта                                                                                                                                                    
  4. OK  