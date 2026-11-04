.PHONY: up down check test migrate seed clean help

help:
	@echo "AdAtlas India - Operational Commands"
	@echo "  make up       - Start local container stack"
	@echo "  make down     - Stop local container stack"
	@echo "  make check    - Run formatting, type checking, security audits, and tests"
	@echo "  make test     - Run test suite"
	@echo "  make migrate  - Run database migrations"
	@echo "  make seed     - Seed reference data (cities, aliases, PIN codes, categories)"

up:
	docker compose -f infra/docker-compose.yml up -d

down:
	docker compose -f infra/docker-compose.yml down

check:
	python scripts/check.py

test:
	pytest backend/tests

migrate:
	alembic -c backend/alembic.ini upgrade head

seed:
	python -m app.db.seed --all

clean:
	rm -rf .pytest_cache backend/.pytest_cache .coverage

