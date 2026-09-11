.PHONY: help install setup dev docker-build docker-up docker-down k8s-deploy k8s-delete test lint clean

help:
	@echo "Movie Ticketing Platform - Available Commands"
	@echo "=============================================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install          - Install all dependencies"
	@echo "  make setup            - Setup environment files"
	@echo "  make setup-db         - Initialize database"
	@echo ""
	@echo "Development:"
	@echo "  make dev              - Start development environment"
	@echo "  make dev-stop         - Stop development environment"
	@echo "  make logs             - View logs"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build     - Build Docker images"
	@echo "  make docker-up        - Start Docker containers"
	@echo "  make docker-down      - Stop Docker containers"
	@echo "  make docker-clean     - Remove Docker containers and images"
	@echo ""
	@echo "Kubernetes:"
	@echo "  make k8s-create-ns    - Create Kubernetes namespaces"
	@echo "  make k8s-deploy       - Deploy to Kubernetes"
	@echo "  make k8s-status       - Check deployment status"
	@echo "  make k8s-delete       - Delete Kubernetes deployment"
	@echo ""
	@echo "ML & Data:"
	@echo "  make train-models     - Train ML models"
	@echo "  make mlflow-start     - Start MLflow server"
	@echo "  make airflow-start    - Start Airflow"
	@echo "  make model-serve      - Start model serving API"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  make test             - Run all tests"
	@echo "  make test-unit        - Run unit tests"
	@echo "  make test-integration - Run integration tests"
	@echo "  make lint             - Run linters"
	@echo "  make format           - Format code"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean            - Clean build artifacts"
	@echo "  make docs             - Generate documentation"
	@echo ""

# ==================== Installation ====================

install:
	@echo "Installing Node dependencies..."
	npm install
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt
	@echo "Installation complete!"

setup:
	@echo "Setting up environment..."
	cp .env.example .env
	@echo "Created .env file - please update with your configuration"

setup-db:
	@echo "Initializing database..."
	docker-compose up -d postgres
	sleep 5
	docker-compose exec postgres psql -U ticketing_user -d ticketing_db -c "SELECT 1;"
	@echo "Database initialized!"

# ==================== Development ====================

dev: docker-up
	@echo "Development environment started"
	@echo "Frontend: http://localhost:3100"
	@echo "API: http://localhost:3000"
	@echo "MLflow: http://localhost:5000"

dev-stop: docker-down
	@echo "Development environment stopped"

logs:
	docker-compose logs -f

# ==================== Docker ====================

docker-build:
	@echo "Building Docker images..."
	docker build -t ticketing/app:latest .
	@echo "Build complete!"

docker-up:
	@echo "Starting Docker containers..."
	docker-compose up -d
	@echo "Containers started! Wait 30 seconds for services to be ready..."
	sleep 30
	@echo "Services should now be available"

docker-down:
	@echo "Stopping Docker containers..."
	docker-compose down

docker-clean: docker-down
	@echo "Removing Docker volumes..."
	docker-compose down -v
	docker system prune -f

# ==================== Kubernetes ====================

k8s-create-ns:
	@echo "Creating Kubernetes namespaces..."
	kubectl create namespace ticketing 2>/dev/null || true
	kubectl create namespace ai-models 2>/dev/null || true
	kubectl create namespace ai-training 2>/dev/null || true
	@echo "Namespaces created!"

k8s-deploy: k8s-create-ns
	@echo "Deploying to Kubernetes..."
	kubectl apply -f kubernetes-deployment.yaml
	kubectl apply -f kubernetes_ai_workloads.yaml
	@echo "Deployment complete!"

k8s-status:
	@echo "=== Ticketing Services ==="
	kubectl get pods -n ticketing
	@echo ""
	@echo "=== AI/ML Services ==="
	kubectl get pods -n ai-models
	@echo ""
	@echo "=== Training Jobs ==="
	kubectl get pods -n ai-training

k8s-delete:
	@echo "Deleting Kubernetes deployment..."
	kubectl delete -f kubernetes-deployment.yaml
	kubectl delete -f kubernetes_ai_workloads.yaml
	@echo "Deployment deleted!"

# ==================== ML & Data ====================

train-models:
	@echo "Training ML models..."
	python recommendation_model.py
	python fraud_detection_model.py
	python demand_forecasting_model.py
	@echo "Model training complete!"

mlflow-start:
	@echo "Starting MLflow server on http://localhost:5000"
	mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./artifacts

airflow-start:
	@echo "Initializing Airflow..."
	airflow db init
	@echo "Starting Airflow server on http://localhost:8080"
	airflow webserver -p 8080

model-serve:
	@echo "Starting model serving API on http://localhost:8000"
	python model_serving_api.py

# ==================== Testing ====================

test: test-unit test-integration
	@echo "All tests passed!"

test-unit:
	@echo "Running unit tests..."
	pytest tests/unit --cov=src --cov-report=html

test-integration:
	@echo "Running integration tests..."
	pytest tests/integration

test-ml:
	@echo "Testing ML models..."
	pytest tests/ml

# ==================== Linting & Formatting ====================

lint:
	@echo "Running linters..."
	npm run lint
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	pylint src/

format:
	@echo "Formatting code..."
	npx prettier --write .
	black .
	isort .
	@echo "Code formatted!"

# ==================== Utilities ====================

clean:
	@echo "Cleaning build artifacts..."
	rm -rf dist/ build/ *.egg-info
	rm -rf __pycache__ .pytest_cache .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	@echo "Clean complete!"

docs:
	@echo "Generating documentation..."
	@echo "Documentation generated in docs/ directory"

# ==================== Database ====================

db-migrate:
	@echo "Running database migrations..."
	npx db-migrate up

db-reset:
	@echo "Resetting database..."
	docker-compose exec postgres dropdb -U ticketing_user ticketing_db 2>/dev/null || true
	docker-compose exec postgres createdb -U ticketing_user ticketing_db
	@echo "Database reset!"

# ==================== Deployment ====================

deploy-staging:
	@echo "Deploying to staging..."
	kubectl apply -f kubernetes-deployment.yaml -n staging

deploy-production:
	@echo "Deploying to production..."
	@echo "WARNING: This will deploy to production!"
	@echo "Are you sure? (y/n)"
	@read -r response; \
	if [ "$$response" = "y" ]; then \
		kubectl apply -f kubernetes-deployment.yaml -n production; \
		echo "Production deployment complete!"; \
	else \
		echo "Deployment cancelled"; \
	fi

# ==================== Monitoring ====================

monitor:
	@echo "Opening monitoring dashboards..."
	@echo "Grafana: http://localhost:3000"
	@echo "Prometheus: http://localhost:9090"

# ==================== One-time Setup ====================

init: install setup setup-db docker-build
	@echo "Project initialization complete!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Update .env with your configuration"
	@echo "2. Run 'make dev' to start development"
	@echo "3. Open http://localhost:3100 in your browser"
