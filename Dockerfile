# 1. THE BASE
FROM python:3.10-slim

# 2. THE SUPPLIER (The "uv" Magic)
# Instead of 'pip install uv', we copy the binary from the official uv image.
# Logic: It's cleaner, smaller, and doesn't pollute your python environment.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 3. ENVIRONMENT VARIABLES
# UV_COMPILE_BYTECODE=1: Ensures uv compiles Python to .pyc files (faster startup)
# UV_LINK_MODE=copy: Ensures files are copied, not hardlinked (safer for Docker)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# 4. WORKSPACE
WORKDIR /app

# 5. SYSTEM DEPENDENCIES (Unchanged)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 6. DEPENDENCY CACHING LAYER (The "Logic" Change)
# We copy ONLY the dependency files first.
COPY pyproject.toml uv.lock* ./

# 7. INSTALL DEPENDENCIES
# --system: Tells uv "Don't create a venv, just install into the Docker container's global Python".
# --no-dev: We don't need testing tools in production.
RUN uv pip install --system --no-cache -r pyproject.toml || uv pip install --system --no-cache .

# 8. COPY SOURCE CODE
COPY . .

# 9. INSTALL PROJECT (Editable mode)
# Now we install the app itself.
RUN uv pip install --system --no-cache -e .

# 10. PORTS & START
EXPOSE 8501
EXPOSE 9999

# Run the app 
CMD ["python", "app/main.py"]