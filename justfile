# dash-vibe task runner

# Install all dependencies including dev
init:
    uv venv --python 3.11
    uv pip install -e ".[dev]"
    uv run playwright install chromium

# Run the app locally
run:
    uv run streamlit run app.py

# Install + run in one go
dev: init run

# Format code
fmt:
    uv run ruff format .

# Lint
lint:
    uv run ruff check .

# Lint and auto-fix what's safe
fix:
    uv run ruff check --fix .

# Run unit tests only
test:
    uv run pytest tests/ -v --ignore=tests/e2e

# Run e2e tests (requires app running on localhost:8501)
test-e2e:
    uv run pytest tests/e2e/ -v

# Full check: lint + unit tests
check: lint test
