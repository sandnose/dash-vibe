# dash-vibe task runner

# Install all dependencies including dev
init:
    uv venv --python 3.11
    uv pip install -e ".[dev]"

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

# Run tests
test:
    uv run pytest -v

# Full check: lint + test
check: lint test
