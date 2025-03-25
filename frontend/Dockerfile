# Use a smaller base image and specify a stable tag for reproducibility.
FROM python:3.10-slim-buster AS base

# Install essential build tools and dependencies in a single layer to reduce image size.
RUN apt-get update && apt-get install -y --no-install-recommends \
    unzip \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install UV for faster dependency management.
RUN pip install --no-cache-dir uv

# Set the working directory for the application.
WORKDIR /app

# Copy project files.
COPY frontend ./frontend
COPY frontend/pyproject.toml ./pyproject.toml

# Create and activate a virtual environment using UV.
RUN uv venv .venv

# Install project dependencies and Reflex in a single command, leveraging UV's speed.
RUN . /app/.venv/bin/activate && uv pip install -e . reflex

# Make sure the virtual environment binaries are in PATH
ENV PATH="/app/.venv/bin:$PATH"

# Expose the port Reflex uses.
EXPOSE 3005
EXPOSE 8000


# Set the working directory to the frontend directory.
WORKDIR /app/frontend

# Initialize and run the Reflex application.
CMD ["sh", "-c", "reflex init && reflex run --backend-host 0.0.0.0"]