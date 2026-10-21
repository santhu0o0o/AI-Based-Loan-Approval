# LoanWise AI developer commands. Run `make help` for a list.
PYTHON ?= python3
IMAGE  ?= loanwise-ai

.DEFAULT_GOAL := help
.PHONY: help install install-dev train test lint typecheck format run serve build-frontend docker-build clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install: ## Install runtime dependencies and the package (editable)
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install -e . --no-deps

install-dev: ## Install runtime + development tooling
	$(PYTHON) -m pip install -r requirements-dev.txt
	$(PYTHON) -m pip install -e . --no-deps

train: ## Train the model and write artifacts/
	$(PYTHON) scripts/train_model.py

test: ## Run the test suite (stdlib unittest; pytest also works)
	$(PYTHON) -m unittest discover -s tests -t .

lint: ## Lint with ruff
	ruff check src tests scripts wsgi.py

typecheck: ## Type-check with mypy (strict)
	mypy --python-executable $(PYTHON)

format: ## Auto-fix lint issues and format
	ruff check --fix src tests scripts wsgi.py
	ruff format src tests scripts wsgi.py

run: ## Start the development server (LOANWISE_HOST / LOANWISE_PORT)
	$(PYTHON) scripts/run_server.py

serve: ## Start the production server locally with gunicorn
	gunicorn --bind 0.0.0.0:$${LOANWISE_PORT:-5000} --workers 2 wsgi:app

build-frontend: ## Build the React app into frontend/dist
	cd frontend && npm install && npm run build

docker-build: ## Build the production Docker image
	docker build -t $(IMAGE) .

clean: ## Remove caches (keeps artifacts and the history database)
	find . -path ./frontend -prune -o -type d -name __pycache__ -exec rm -rf {} +
	rm -rf .mypy_cache .ruff_cache .pytest_cache build src/*.egg-info
