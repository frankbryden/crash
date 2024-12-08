start:
	docker compose up -d

dev-front: start
	docker compose down frontend
	cd frontend && npm run dev

dev-back: start
	docker compose down backend
	cd backend && python -m fastapi run main.py

build:
	docker compose build

precommit:
	pip install pre-commit
	pre-commit install