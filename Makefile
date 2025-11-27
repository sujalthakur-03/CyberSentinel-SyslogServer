.PHONY: help build up down restart logs clean test lint format health

# Variables
COMPOSE_FILE := docker-compose.yml
ENV_FILE := .env
SERVICES := receiver processor api alerting

help: ## Show this help message
	@echo 'CyberSentinel SyslogServer - Makefile Commands'
	@echo ''
	@echo 'Usage:'
	@echo '  make <target>'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build all Docker images
	@echo "Building Docker images..."
	docker-compose -f $(COMPOSE_FILE) build --parallel

up: ## Start all services
	@echo "Starting CyberSentinel SyslogServer..."
	@if [ ! -f $(ENV_FILE) ]; then \
		echo "Creating .env file from .env.example..."; \
		cp .env.example $(ENV_FILE); \
	fi
	docker-compose -f $(COMPOSE_FILE) up -d
	@echo ""
	@echo "Services started successfully!"
	@echo "API: http://localhost:8000/docs"
	@echo "Grafana: http://localhost:3001 (admin/admin)"
	@echo "Prometheus: http://localhost:9090"
	@echo ""
	@make health

down: ## Stop all services
	@echo "Stopping CyberSentinel SyslogServer..."
	docker-compose -f $(COMPOSE_FILE) down

restart: ## Restart all services
	@echo "Restarting services..."
	docker-compose -f $(COMPOSE_FILE) restart

stop: ## Stop all services without removing containers
	@echo "Stopping services..."
	docker-compose -f $(COMPOSE_FILE) stop

start: ## Start existing containers
	@echo "Starting services..."
	docker-compose -f $(COMPOSE_FILE) start

logs: ## Show logs from all services (use ARGS="service-name" for specific service)
	docker-compose -f $(COMPOSE_FILE) logs -f $(ARGS)

logs-receiver: ## Show receiver service logs
	docker-compose -f $(COMPOSE_FILE) logs -f receiver

logs-processor: ## Show processor service logs
	docker-compose -f $(COMPOSE_FILE) logs -f processor

logs-api: ## Show API service logs
	docker-compose -f $(COMPOSE_FILE) logs -f api

logs-alerting: ## Show alerting service logs
	docker-compose -f $(COMPOSE_FILE) logs -f alerting

ps: ## List running services
	docker-compose -f $(COMPOSE_FILE) ps

health: ## Check health status of all services
	@echo "Checking service health..."
	@./scripts/health-check.sh

clean: ## Remove all containers, volumes, and images
	@echo "WARNING: This will remove all containers, volumes, and data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose -f $(COMPOSE_FILE) down -v --rmi all; \
		echo "Cleanup complete!"; \
	fi

clean-data: ## Remove only volumes (data)
	@echo "WARNING: This will remove all data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose -f $(COMPOSE_FILE) down -v; \
		echo "Data cleanup complete!"; \
	fi

rebuild: ## Rebuild and restart services
	@echo "Rebuilding services..."
	docker-compose -f $(COMPOSE_FILE) up -d --build

scale-processor: ## Scale processor service (use REPLICAS=n)
	@echo "Scaling processor to $(REPLICAS) replicas..."
	docker-compose -f $(COMPOSE_FILE) up -d --scale processor=$(REPLICAS)

test-receiver: ## Test syslog receiver with sample messages
	@echo "Sending test syslog messages..."
	@./scripts/test-syslog.sh

test-api: ## Test API endpoints
	@echo "Testing API endpoints..."
	@./scripts/test-api.sh

setup-certs: ## Generate self-signed TLS certificates
	@echo "Generating TLS certificates..."
	@./scripts/generate-certs.sh

backup: ## Backup all data volumes
	@echo "Creating backup..."
	@./scripts/backup.sh

restore: ## Restore data from backup
	@echo "Restoring from backup..."
	@./scripts/restore.sh

init: ## Initialize the system (first-time setup)
	@echo "Initializing CyberSentinel SyslogServer..."
	@if [ ! -f $(ENV_FILE) ]; then \
		cp .env.example $(ENV_FILE); \
		echo "Created .env file - please review and update configuration"; \
	fi
	@./scripts/generate-certs.sh
	@echo "Initialization complete!"
	@echo "Next steps:"
	@echo "  1. Review and update .env file"
	@echo "  2. Run 'make build' to build images"
	@echo "  3. Run 'make up' to start services"

metrics: ## Open Prometheus metrics UI
	@echo "Opening Prometheus..."
	@xdg-open http://localhost:9090 2>/dev/null || open http://localhost:9090 2>/dev/null || echo "Navigate to http://localhost:9090"

dashboard: ## Open Grafana dashboard
	@echo "Opening Grafana..."
	@xdg-open http://localhost:3001 2>/dev/null || open http://localhost:3001 2>/dev/null || echo "Navigate to http://localhost:3001"

api-docs: ## Open API documentation
	@echo "Opening API docs..."
	@xdg-open http://localhost:8000/docs 2>/dev/null || open http://localhost:8000/docs 2>/dev/null || echo "Navigate to http://localhost:8000/docs"

dev: ## Start services in development mode with live reload
	docker-compose -f $(COMPOSE_FILE) -f docker-compose.dev.yml up

lint: ## Run linting on Python code
	@echo "Running linters..."
	@for service in $(SERVICES); do \
		echo "Linting $$service..."; \
		docker run --rm -v $(PWD)/services/$$service:/app -w /app python:3.11 \
			bash -c "pip install -q flake8 black && flake8 src/ && black --check src/"; \
	done

format: ## Format Python code with black
	@echo "Formatting code..."
	@for service in $(SERVICES); do \
		echo "Formatting $$service..."; \
		docker run --rm -v $(PWD)/services/$$service:/app -w /app python:3.11 \
			bash -c "pip install -q black && black src/"; \
	done

stats: ## Show resource usage statistics
	@docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

version: ## Show version information
	@echo "CyberSentinel SyslogServer v1.0.0"
	@echo "Docker Compose version:"
	@docker-compose version
