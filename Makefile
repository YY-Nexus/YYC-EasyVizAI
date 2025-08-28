.PHONY: bootstrap dev backend frontend test lint fmt migrate openapi seed clean type

bootstrap:
\tpip install --upgrade pip
\tcd backend && pip install -r requirements.txt
\tcd frontend && pnpm install

dev:
\ttmux new-session -d -s easyviz 'make backend' \\; split-window -h 'make frontend' \\; attach

backend:
\tcd backend && DJANGO_SETTINGS_MODULE=app.settings python manage.py runserver 0.0.0.0:8000

frontend:
\tcd frontend && pnpm dev

migrate:
\tcd backend && python manage.py migrate

test:
\tcd backend && pytest -q
\tcd frontend && pnpm test

lint:
\tcd backend && ruff check .
\tcd frontend && pnpm lint

fmt:
\tcd backend && ruff format .
\tcd frontend && pnpm format

type:
\tcd backend && mypy app
\tcd frontend && tsc --noEmit

openapi:
\tcd backend && python manage.py generate_openapi > ../docs/api/openapi_v1.yaml

seed:
\tcd backend && python manage.py loaddata demo_seed.json

clean:
\trm -rf **/__pycache__ **/*.pyc