# === Python Backend ===
PYTHON=python3
VENV_DIR=backend/venv
BACKEND_DIR=backend
REQUIREMENTS=$(BACKEND_DIR)/requirements.txt
FRONTEND_IMAGE=896924684176.dkr.ecr.us-east-2.amazonaws.com/stock-analyzer-frontend
BACKEND_IMAGE=896924684176.dkr.ecr.us-east-2.amazonaws.com/stock-analyzer-backend

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

# Frontend ECR build
build-frontend-prod:
	docker build -f frontend/Dockerfile.prod -t $(FRONTEND_IMAGE) frontend

# Backend ECR build
build-backend-prod:
	docker build -f backend/Dockerfile.prod -t $(BACKEND_IMAGE) backend

push-frontend: build-frontend-prod
	docker push $(FRONTEND_IMAGE)

push-backend: build-backend-prod
	docker push $(BACKEND_IMAGE)

# === Clean ===
.PHONY: clean
clean:
	rm -rf $(VENV_DIR) __pycache__ .pytest_cache .mypy_cache *.pyc *.pyo