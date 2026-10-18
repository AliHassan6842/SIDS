# SIDS private AI service

Python 3.11/FastAPI service for bounded image decoding, sanitization, quality validation, and approved rice-pest model inference. It does not own users, authorization, agronomic policy, or durable business data.

Install and verify with the committed Poetry lockfile:

```powershell
python -m pip install poetry==2.1.3
poetry install --with dev
poetry run ruff check src tests
poetry run mypy src
poetry run pytest
poetry run uvicorn sids_ai.app:app --app-dir src --reload --port 8000
```

`AI_SERVICE_SERVICE_TOKEN` protects private endpoints. `AI_SERVICE_MODEL_MANIFEST` points to the promoted manifest described in the root README. `/health` is liveness; `/ready` reports whether a checksum-verified model is loaded.
