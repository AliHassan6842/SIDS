from fastapi import FastAPI
from sids_ai.api.health import router as health_router
from sids_ai.api.router import router as analysis_router
from sids_ai.core.exceptions import setup_exception_handlers

app = FastAPI(title="SIDS AI Service")

setup_exception_handlers(app)

app.include_router(health_router)
app.include_router(analysis_router)
