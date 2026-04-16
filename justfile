# dash-vibe task runner

# Install dependencies
init:
    uv pip install -e .

# Run the app locally
run:
    streamlit run app.py

# Install + run in one go
dev: init run

# Format code
fmt:
    ruff format .

# Lint
lint:
    ruff check .
