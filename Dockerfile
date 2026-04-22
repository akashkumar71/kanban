FROM node:20-slim AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim

WORKDIR /app

COPY backend/pyproject.toml backend/pyproject.toml
RUN pip install --no-cache-dir fastapi uvicorn aiofiles httpx python-dotenv

COPY backend/ backend/
COPY --from=frontend-builder /app/frontend/out frontend/out

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
