# === Python Backend ===
PYTHON=python3
BACKEND_DIR=backend
ML_DIR=ml
VENV_DIR=$(BACKEND_DIR)/venv
ML_VENV_DIR=$(ML_DIR)/venv
REQUIREMENTS=$(BACKEND_DIR)/requirements.txt
ML_REQUIREMENTS=$(ML_DIR)/requirements.txt
ACCOUNT_ID:=896924684176
AWS_REGION=us-east-1
ECR_URI:=$(ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
FRONTEND_IMAGE=$(ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/stock-analyzer-frontend
BACKEND_IMAGE=$(ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/stock-analyzer-backend
FRONTEND_VERSION=v0.0.2
BACKEND_VERSION=v0.0.9
MODEL_VERSION=v0.0.4
CLOUDFRONT_DISTRIBUTION_ID=E3R6TRBTP0FQ33
BUCKET_NAME=shrubb-stock-analyzer-frontend
DIST_DIR=frontend/dist

.PHONY: venv
venv:
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install --upgrade pip
	$(VENV_DIR)/bin/pip install -r $(REQUIREMENTS)

.PHONY: backend-dev
backend-dev: venv
	PYTHONPATH=./backend USE_LOCAL_MODELS=true $(VENV_DIR)/bin/uvicorn backend.main:app --reload

.PHONY: deps
deps:
	$(VENV_DIR)/bin/python -m pip install --upgrade pip
	$(VENV_DIR)/bin/python -m pip install -r $(REQUIREMENTS)

.PHONY: freeze
freeze:
	$(VENV_DIR)/bin/pip freeze > $(REQUIREMENTS)

.PHONY: test-backend
test-backend:
	PYTHONPATH=./backend $(VENV_DIR)/bin/pytest backend/tests

# === Models ===
.PHONY: train-models
train-models:
	$(PYTHON) -m venv $(ML_VENV_DIR)
	$(ML_VENV_DIR)/bin/pip install --upgrade pip
	$(ML_VENV_DIR)/bin/pip install -r $(ML_REQUIREMENTS)
	PYTHONPATH=./ml USE_LOCAL_MODELS=true $(ML_VENV_DIR)/bin/python ml/train_model.py

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
	cd frontend && echo "{\"version\": \"${FRONTEND_VERSION}\", \"timestamp\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"}" > version.json
	@echo "🚀 Uploading to S3 bucket $(BUCKET_NAME)..."
	aws s3 sync $(DIST_DIR)/ s3://$(BUCKET_NAME) --delete
	aws s3 cp frontend/version.json s3://$(BUCKET_NAME)/version.json --content-type application/json
	aws cloudfront create-invalidation \
            --distribution-id $(CLOUDFRONT_DISTRIBUTION_ID) \
            --paths "/version.json"

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
	docker build -f backend/Dockerfile.prod -t $(BACKEND_IMAGE):$(BACKEND_VERSION) backend

push-backend: build-backend-prod
	docker push $(BACKEND_IMAGE):$(BACKEND_VERSION)

# Terraform Apply
tf-apply:
	cd terraform && ./terraform init
	cd terraform && ./terraform apply -var backend_version="$(BACKEND_VERSION)"

# Custom Sagemaker AI Image
# Target: Build the ML training image
ml-image-build:
	docker build -f ml/Dockerfile -t stock-analyzer-shrubb-ai-custom-trainer:$(MODEL_VERSION) ml

# Target: Tag and push the image to ECR
ml-image-push: ml-image-build
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $(ECR_URI)
	docker tag stock-analyzer-shrubb-ai-custom-trainer:$(MODEL_VERSION) $(ECR_URI)/stock-analyzer-shrubb-ai-custom-trainer:$(MODEL_VERSION)
	docker push $(ECR_URI)/stock-analyzer-shrubb-ai-custom-trainer:$(MODEL_VERSION)

# === Clean ===
.PHONY: clean
clean:
	rm -rf $(VENV_DIR) __pycache__ .pytest_cache .mypy_cache *.pyc *.pyo