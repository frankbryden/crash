start:
	docker compose up -d

start-db:
	docker compose up -d db

dev-front: start
	docker compose down frontend
	cd frontend && npm run dev

dev-back: start
	docker compose down backend
	cd backend && python -m fastapi dev src/crash/main.py

build:
	docker compose build

precommit:
	pip install pre-commit
	pre-commit install

build-backend:
	docker compose build backend

test: build-backend start-db
	docker run --rm  --network crash_backend-network --name test backend pytest

mongo:
	docker exec -it mongo mongosh crash
