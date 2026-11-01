.PHONY: help install test eval run-backend run-frontend docker-up docker-down

help:
	@echo "ResearchX — Multi-Agent Research & Analysis Platform"
	@echo "Available commands:"
	@echo "  make install       - Install backend and frontend dependencies"
	@echo "  make test          - Run backend unit, integration, and E2E test suites"
	@echo "  make eval          - Execute 20-sample evaluation benchmark CLI"
	@echo "  make run-backend   - Run FastAPI backend development server"
	@echo "  make run-frontend  - Run Vite React frontend development server"
	@echo "  make docker-up     - Launch entire full stack with Docker Compose"
	@echo "  make docker-down   - Stop Docker Compose services"

install:
	pip install -r backend/requirements.txt
	cd frontend && npm install

test:
	python -m pytest backend/tests -v

eval:
	python -m evaluation.run_evaluation --limit 5

run-backend:
	cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

run-frontend:
	cd frontend && npm run dev

docker-up:
	docker compose up --build

docker-down:
	docker compose down
