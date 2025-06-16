# Dockerfile
FROM python:3.12-slim

# Install dependencies
RUN apt-get update && apt-get install -y build-essential

# Set workdir
WORKDIR /app

# Copy project files
COPY . /app

# Install project + dev deps (if pyproject.toml has them)
RUN pip install --upgrade pip \
  && pip install pytest

# Install your package in editable mode
RUN pip install -e .

# Run tests by default
CMD ["pytest", "tests"]
