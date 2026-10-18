FROM python:3.11-slim AS build
WORKDIR /app
ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    POETRY_VIRTUALENVS_CREATE=false
RUN python -m pip install --no-cache-dir poetry==2.1.3 && python -m venv /opt/venv
COPY pyproject.toml poetry.lock README.md ./
RUN poetry install --only main --no-root --no-interaction --no-ansi
COPY src ./src
RUN poetry install --only main --no-interaction --no-ansi

FROM python:3.11-slim
WORKDIR /app
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"
COPY --from=build /opt/venv /opt/venv
COPY --from=build /app/src /app/src
USER 65532:65532
EXPOSE 8000
CMD ["uvicorn", "sids_ai.app:app", "--host", "0.0.0.0", "--port", "8000"]
