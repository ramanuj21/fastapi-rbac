# # Dockerfile

FROM python:3.12-slim

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy and install dependencies
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false && poetry install --no-root

WORKDIR /app

COPY . .

# Expose FastAPI port
EXPOSE 8000

# Default command: run FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
