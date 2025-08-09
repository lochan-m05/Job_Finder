# Job Discovery Platform Makefile

# Variables
COMPOSE_FILE := docker-compose.yml
COMPOSE_DEV_FILE := docker-compose.dev.yml
PROJECT_NAME := job_discovery

# Colors for output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

.PHONY: help
help: ## Show this help message
	@echo "$(BLUE)Job Discovery Platform$(RESET)"
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*##"; printf "\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(GREEN)%-15s$(RESET) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

.PHONY: build
build: ## Build all Docker images
	@echo "$(BLUE)Building Docker images...$(RESET)"
	docker-compose -f $(COMPOSE_FILE) build

.PHONY: build-dev
build-dev: ## Build development Docker images
	@echo "$(BLUE)Building development Docker images...$(RESET)"
	docker-compose -f $(COMPOSE_DEV_FILE) build

.PHONY: up
up: ## Start all services in production mode
	@echo "$(BLUE)Starting production services...$(RESET)"
	docker-compose -f $(COMPOSE_FILE) up -d

.PHONY: up-dev
up-dev: ## Start all services in development mode
	@echo "$(BLUE)Starting development services...$(RESET)"
	docker-compose -f $(COMPOSE_DEV_FILE) up -d

.PHONY: down
down: ## Stop all services
	@echo "$(BLUE)Stopping all services...$(RESET)"
	docker-compose -f $(COMPOSE_FILE) down

.PHONY: down-dev
down-dev: ## Stop development services
	@echo "$(BLUE)Stopping development services...$(RESET)"
	docker-compose -f $(COMPOSE_DEV_FILE) down

.PHONY: restart
restart: down up ## Restart all services

.PHONY: restart-dev
restart-dev: down-dev up-dev ## Restart development services

.PHONY: logs
logs: ## Show logs for all services
	docker-compose -f $(COMPOSE_FILE) logs -f

.PHONY: logs-backend
logs-backend: ## Show backend logs
	docker-compose -f $(COMPOSE_FILE) logs -f backend

.PHONY: logs-frontend
logs-frontend: ## Show frontend logs
	docker-compose -f $(COMPOSE_FILE) logs -f frontend

.PHONY: logs-celery
logs-celery: ## Show Celery worker logs
	docker-compose -f $(COMPOSE_FILE) logs -f celery_worker

.PHONY: shell-backend
shell-backend: ## Open shell in backend container
	docker-compose -f $(COMPOSE_FILE) exec backend bash

.PHONY: shell-frontend
shell-frontend: ## Open shell in frontend container
	docker-compose -f $(COMPOSE_FILE) exec frontend sh

.PHONY: shell-db
shell-db: ## Open MongoDB shell
	docker-compose -f $(COMPOSE_FILE) exec mongodb mongosh -u admin -p password123 --authenticationDatabase admin

.PHONY: test
test: ## Run all tests
	@echo "$(BLUE)Running tests...$(RESET)"
	docker-compose -f $(COMPOSE_FILE) exec backend python -m pytest
	docker-compose -f $(COMPOSE_FILE) exec frontend npm test -- --coverage --watchAll=false

.PHONY: test-backend
test-backend: ## Run backend tests
	@echo "$(BLUE)Running backend tests...$(RESET)"
	docker-compose -f $(COMPOSE_FILE) exec backend python -m pytest

.PHONY: test-frontend
test-frontend: ## Run frontend tests
	@echo "$(BLUE)Running frontend tests...$(RESET)"
	docker-compose -f $(COMPOSE_FILE) exec frontend npm test -- --coverage --watchAll=false

.PHONY: lint
lint: ## Run linting
	@echo "$(BLUE)Running linting...$(RESET)"
	docker-compose -f $(COMPOSE_FILE) exec backend flake8 app/
	docker-compose -f $(COMPOSE_FILE) exec backend black --check app/
	docker-compose -f $(COMPOSE_FILE) exec frontend npm run lint

.PHONY: format
format: ## Format code
	@echo "$(BLUE)Formatting code...$(RESET)"
	docker-compose -f $(COMPOSE_FILE) exec backend black app/
	docker-compose -f $(COMPOSE_FILE) exec frontend npm run format

.PHONY: migrate
migrate: ## Run database migrations
	@echo "$(BLUE)Running database migrations...$(RESET)"
	docker-compose -f $(COMPOSE_FILE) exec backend python -m app.database

.PHONY: seed
seed: ## Seed database with sample data
	@echo "$(BLUE)Seeding database...$(RESET)"
	docker-compose -f $(COMPOSE_FILE) exec backend python -m app.scripts.seed_data

.PHONY: backup-db
backup-db: ## Backup MongoDB database
	@echo "$(BLUE)Backing up database...$(RESET)"
	mkdir -p ./backups
	docker-compose -f $(COMPOSE_FILE) exec mongodb mongodump --authenticationDatabase admin -u admin -p password123 --out /tmp/backup
	docker cp job_discovery_mongodb:/tmp/backup ./backups/mongodb_$(shell date +%Y%m%d_%H%M%S)

.PHONY: restore-db
restore-db: ## Restore MongoDB database (requires BACKUP_PATH)
	@if [ -z "$(BACKUP_PATH)" ]; then echo "$(RED)Please specify BACKUP_PATH$(RESET)"; exit 1; fi
	@echo "$(BLUE)Restoring database from $(BACKUP_PATH)...$(RESET)"
	docker cp $(BACKUP_PATH) job_discovery_mongodb:/tmp/restore
	docker-compose -f $(COMPOSE_FILE) exec mongodb mongorestore --authenticationDatabase admin -u admin -p password123 /tmp/restore

.PHONY: clean
clean: ## Clean up Docker resources
	@echo "$(BLUE)Cleaning up Docker resources...$(RESET)"
	docker-compose -f $(COMPOSE_FILE) down -v --remove-orphans
	docker system prune -f
	docker volume prune -f

.PHONY: setup
setup: ## Initial setup (build and start services)
	@echo "$(BLUE)Setting up Job Discovery Platform...$(RESET)"
	make build
	make up
	@echo "$(GREEN)Setup complete! Services are starting...$(RESET)"
	@echo "$(YELLOW)Frontend: http://localhost:3000$(RESET)"
	@echo "$(YELLOW)Backend API: http://localhost:8000$(RESET)"
	@echo "$(YELLOW)Flower (Celery): http://localhost:5555$(RESET)"
	@echo "$(YELLOW)Grafana: http://localhost:3001$(RESET)"

.PHONY: setup-dev
setup-dev: ## Setup development environment
	@echo "$(BLUE)Setting up development environment...$(RESET)"
	make build-dev
	make up-dev
	@echo "$(GREEN)Development setup complete!$(RESET)"

.PHONY: status
status: ## Show status of all services
	@echo "$(BLUE)Service Status:$(RESET)"
	docker-compose -f $(COMPOSE_FILE) ps

.PHONY: stats
stats: ## Show resource usage statistics
	@echo "$(BLUE)Resource Usage:$(RESET)"
	docker stats --no-stream

.PHONY: update
update: ## Update all services
	@echo "$(BLUE)Updating services...$(RESET)"
	docker-compose -f $(COMPOSE_FILE) pull
	make build
	make restart

.PHONY: scale-workers
scale-workers: ## Scale Celery workers (use WORKERS=n)
	@if [ -z "$(WORKERS)" ]; then echo "$(RED)Please specify WORKERS=n$(RESET)"; exit 1; fi
	@echo "$(BLUE)Scaling Celery workers to $(WORKERS)...$(RESET)"
	docker-compose -f $(COMPOSE_FILE) up -d --scale celery_worker=$(WORKERS)

.PHONY: monitor
monitor: ## Open monitoring dashboard
	@echo "$(BLUE)Opening monitoring dashboards...$(RESET)"
	@echo "$(YELLOW)Flower: http://localhost:5555$(RESET)"
	@echo "$(YELLOW)Grafana: http://localhost:3001 (admin/admin123)$(RESET)"
	@echo "$(YELLOW)Prometheus: http://localhost:9090$(RESET)"

.PHONY: security-scan
security-scan: ## Run security scan on Docker images
	@echo "$(BLUE)Running security scan...$(RESET)"
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
		-v $(PWD):/app aquasec/trivy image job_discovery_backend:latest
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
		-v $(PWD):/app aquasec/trivy image job_discovery_frontend:latest

.PHONY: docs
docs: ## Generate and serve documentation
	@echo "$(BLUE)Generating documentation...$(RESET)"
	docker-compose -f $(COMPOSE_FILE) exec backend python -m mkdocs serve -a 0.0.0.0:8080

.PHONY: install-deps
install-deps: ## Install local development dependencies
	@echo "$(BLUE)Installing backend dependencies...$(RESET)"
	cd backend && pip install -r requirements.txt
	@echo "$(BLUE)Installing frontend dependencies...$(RESET)"
	cd frontend && npm install

.PHONY: env-check
env-check: ## Check environment configuration
	@echo "$(BLUE)Checking environment configuration...$(RESET)"
	@if [ ! -f .env ]; then echo "$(YELLOW)Warning: .env file not found$(RESET)"; fi
	@if [ ! -f config.env.example ]; then echo "$(RED)Error: config.env.example not found$(RESET)"; fi
	@echo "$(GREEN)Environment check complete$(RESET)"
