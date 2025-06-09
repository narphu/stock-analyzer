# === Python Backend ===
PYTHON=python3
VENV_DIR=backend/venv
BACKEND_DIR=backend
REQUIREMENTS=$(BACKEND_DIR)/requirements.txt

.PHONY: venv
venv:
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install --upgrade pip
	$(VENV_DIR)/bin/pip install -r $(REQUIREMENTS)

.PHONY: dev
dev: venv
	$(VENV_DIR)/bin/uvicorn backend/main:app --reload

.PHONY: deps
deps:
	$(VENV_DIR)/bin/pip install -r $(REQUIREMENTS)

.PHONY: freeze
freeze:
	$(VENV_DIR)/bin/pip freeze > $(REQUIREMENTS)

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

# === Clean ===
.PHONY: clean
clean:
	rm -rf $(VENV_DIR) __pycache__ .pytest_cache .mypy_cache *.pyc *.pyo