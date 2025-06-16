# === Python Backend ===
PYTHON=python3
VENV_DIR=backend/venv
BACKEND_DIR=backend
REQUIREMENTS=$(BACKEND_DIR)/requirements.txt
FRONTEND_IMAGE=896924684176.dkr.ecr.us-east-1.amazonaws.com/stock-analyzer-frontend
BACKEND_IMAGE=896924684176.dkr.ecr.us-east-1.amazonaws.com/stock-analyzer-backend
VERSION=v0.0.2
BUCKET_NAME=shrubb-stock-analyzer-frontend
DIST_DIR=frontend/dist

.PHONY: venv
venv:
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install --upgrade pip
	$(VENV_DIR)/bin/pip install -r $(REQUIREMENTS)

.PHONY: dev
dev: venv
	PYTHONPATH=. $(VENV_DIR)/bin/uvicorn backend.main:app --reload

.PHONY: deps
deps:
	$(VENV_DIR)/bin/python -m pip install --upgrade pip
	$(VENV_DIR)/bin/python -m pip install -r $(REQUIREMENTS)

.PHONY: freeze
freeze:
	$(VENV_DIR)/bin/pip freeze > $(REQUIREMENTS)

# === Models ===
.PHONY: train-models
train-models:
	PYTHONPATH=. $(VENV_DIR)/bin/python backend/train_model.py


# === React Frontend ===
.PHONY: frontend
frontend:
	cd frontend && npm run dev

.PHONY: frontend-deps
frontend-deps:
	cd frontend && npm install

.PHONY: frontend-build
frontend-build:
	cd frontend && npm run build

# Upload dist/ folder to S3
.PHONY: frontend-upload
frontend-upload:
	@echo "🚀 Uploading to S3 bucket $(BUCKET_NAME)..."
	aws s3 sync $(DIST_DIR)/ s3://$(BUCKET_NAME) --delete

# Combined build + upload
.PHONY: frontend-deploy
frontend-deploy: frontend-build frontend-upload
	@echo "✅ Deployment complete!"

# Clean the build output
.PHONY: frontend-clean
frontend-clean:
	@echo "🧹 Cleaning $(DIST_DIR)..."
	rm -rf $(DIST_DIR)

# === Docker ===
.PHONY: docker-up
docker-up:
	docker-compose up --build

.PHONY: docker-down
docker-down:
	docker-compose down -v

.PHONY: docker-rebuild
docker-rebuild:
	docker-compose down -v
	docker-compose build
	docker-compose up

# Backend ECR build
build-backend-prod:
	docker build -f backend/Dockerfile.prod -t $(BACKEND_IMAGE):$(VERSION) backend

push-backend: build-backend-prod
	docker push $(BACKEND_IMAGE):$(VERSION)

# === Clean ===
.PHONY: clean
clean:
	rm -rf $(VENV_DIR) __pycache__ .pytest_cache .mypy_cache *.pyc *.pyo