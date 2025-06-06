# Variables
PYTHON=python3
VENV_DIR=venv
REQUIREMENTS=requirements.txt

# Local virtual environment setup
.PHONY: venv
venv:
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install --upgrade pip
	$(VENV_DIR)/bin/pip install -r $(REQUIREMENTS)

# Run locally with live reload
.PHONY: dev
dev: venv
	$(VENV_DIR)/bin/uvicorn main:app --reload

# Install dependencies (after editing requirements.txt)
.PHONY: deps
deps:
	$(VENV_DIR)/bin/pip install -r $(REQUIREMENTS)

# Freeze current local env requirements
.PHONY: freeze
freeze:
	$(VENV_DIR)/bin/pip freeze > $(REQUIREMENTS)

# Run backend in Docker
.PHONY: docker-up
docker-up:
	docker-compose up --build

# Stop containers
.PHONY: docker-down
docker-down:
	docker-compose down -v

# Rebuild Docker
.PHONY: docker-rebuild
docker-rebuild:
	docker-compose down -v
	docker-compose build
	docker-compose up

# Clean everything
.PHONY: clean
clean:
	rm -rf $(VENV_DIR) __pycache__ .pytest_cache .mypy_cache *.pyc *.pyo
