import asyncio
import hmac
import logging
import time
import uuid
from contextlib import asynccontextmanager
from typing import Annotated

import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse

from sids_ai.core.config import get_settings
from sids_ai.core.errors import ImageRejected, ModelUnavailable
from sids_ai.image.decoder import decode_and_sanitize
from sids_ai.image.quality import assess_quality
from sids_ai.insect.model import PestDetector, GeneralInsectClassifier
from sids_ai.registry.manifest import ModelManifest, load_manifest
from sids_ai.schemas import (
    IdentificationMode,
    IdentificationStatus,
    IdentifyResponse,
    ModelMetadata,
    UnknownReason,
    ValidateFrameResponse,
    ValidationReason,
)

logger = logging.getLogger("sids_ai")
settings = get_settings()
inference_slots = asyncio.Semaphore(settings.max_inference_concurrency)


def _unavailable_metadata() -> ModelMetadata:
    return ModelMetadata(id="unavailable", version="unavailable", datasetVersion="unavailable")


async def _warm_detector(detector: PestDetector, manifest: ModelManifest) -> None:
    if settings.environment == "test" or not manifest.crop_classes:
        return
    crop_slug = next(iter(manifest.crop_classes))
    sample = np.zeros((manifest.input_size, manifest.input_size, 3), dtype=np.uint8)
    await asyncio.to_thread(detector.identify, sample, crop_slug)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        manifest = load_manifest(settings.model_manifest)
        app.state.manifest = manifest
        app.state.detector = PestDetector(manifest)
        await _warm_detector(app.state.detector, manifest)
        logger.info("approved_model_loaded model_id=%s version=%s", manifest.model_id, manifest.version)
    except ModelUnavailable as exc:
        app.state.manifest = None
        app.state.detector = None
        logger.warning("approved_model_unavailable reason=%s", str(exc))
    try:
        small_subject_manifest = load_manifest(settings.small_subject_model_manifest)
        app.state.small_subject_manifest = small_subject_manifest
        app.state.small_subject_detector = PestDetector(small_subject_manifest)
        await _warm_detector(app.state.small_subject_detector, small_subject_manifest)
        logger.info(
            "small_subject_model_loaded model_id=%s version=%s",
            small_subject_manifest.model_id,
            small_subject_manifest.version,
        )
    except ModelUnavailable as exc:
        app.state.small_subject_manifest = None
        app.state.small_subject_detector = None
        logger.warning("small_subject_model_unavailable reason=%s", str(exc))
        
    try:
        if settings.general_insect_model_manifest:
            gi_manifest = load_manifest(settings.general_insect_model_manifest)
            app.state.general_insect_manifest = gi_manifest
            app.state.general_insect_detector = GeneralInsectClassifier(gi_manifest)
            logger.info("general_insect_model_loaded model_id=%s version=%s", gi_manifest.model_id, gi_manifest.version)
        else:
            app.state.general_insect_manifest = None
            app.state.general_insect_detector = None
    except ModelUnavailable as exc:
        app.state.general_insect_manifest = None
        app.state.general_insect_detector = None
        logger.warning("general_insect_model_unavailable reason=%s", str(exc))
        
    yield


app = FastAPI(title="SIDS Private AI Service", version="1.0.0", lifespan=lifespan)


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    started = time.perf_counter()
    if request.url.path.startswith("/internal/v1/") and not hmac.compare_digest(
        request.headers.get("x-sids-service-token", ""), settings.service_token
    ):
        response = JSONResponse(status_code=401, content={"detail": "Core service authentication required"})
    else:
        response = await call_next(request)
    response.headers["x-request-id"] = request_id
    logger.info(
        "request_complete request_id=%s path=%s status=%s latency_ms=%d",
        request_id,
        request.url.path,
        response.status_code,
        int((time.perf_counter() - started) * 1000),
    )
    return response


@app.exception_handler(ImageRejected)
async def image_rejected_handler(request: Request, exc: ImageRejected) -> JSONResponse:
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    return JSONResponse(
        status_code=400,
        content={"code": exc.reason, "message": str(exc), "retryable": True, "requestId": request_id, "details": {}},
    )


async def _read_bounded(upload: UploadFile) -> bytes:
    data = await upload.read(settings.max_upload_bytes + 1)
    if len(data) > settings.max_upload_bytes:
        raise ImageRejected("INVALID_IMAGE", "Image exceeds the byte limit.")
    return data


def _validate_context(mode: IdentificationMode, crop_id: str | None) -> None:
    if mode is IdentificationMode.CROP_PEST and crop_id is None:
        raise HTTPException(status_code=422, detail="crop_id is required for CROP_PEST mode")
    if mode is IdentificationMode.GENERAL_INSECT and crop_id is not None:
        raise HTTPException(status_code=422, detail="crop_id is forbidden for GENERAL_INSECT mode")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "UP"}


@app.get("/ready")
async def ready(request: Request) -> JSONResponse:
    ready_now = (
        request.app.state.detector is not None
        and request.app.state.small_subject_detector is not None
    )
    return JSONResponse(status_code=200 if ready_now else 503, content={"status": "READY" if ready_now else "MODEL_UNAVAILABLE"})


@app.post("/internal/v1/validate-frame", response_model=ValidateFrameResponse)
async def validate_frame(
    image: Annotated[UploadFile, File()],
    crop_id: Annotated[str | None, Form(min_length=1, max_length=64)] = None,
    mode: Annotated[IdentificationMode, Form()] = IdentificationMode.CROP_PEST,
) -> ValidateFrameResponse:
    _validate_context(mode, crop_id)
    decoded = decode_and_sanitize(await _read_bounded(image), image.content_type, settings)
    quality = assess_quality(decoded.rgb, settings)
    return ValidateFrameResponse(
        valid=quality.valid,
        reason=quality.reason,
        insectCandidate=quality.insect_candidate,
        quality=quality.summary,
    )


@app.post("/internal/v1/identify", response_model=IdentifyResponse)
async def identify(
    request: Request,
    image: Annotated[UploadFile, File()],
    crop_id: Annotated[str | None, Form(min_length=1, max_length=64)] = None,
    mode: Annotated[IdentificationMode, Form()] = IdentificationMode.CROP_PEST,
) -> IdentifyResponse:
    _validate_context(mode, crop_id)
    decoded = decode_and_sanitize(await _read_bounded(image), image.content_type, settings)
    quality = assess_quality(decoded.rgb, settings)
    if mode is IdentificationMode.GENERAL_INSECT:
        if not quality.valid:
            return IdentifyResponse(
                status=IdentificationStatus.REJECTED_IMAGE,
                reason=quality.reason,
                prediction=None,
                model=_unavailable_metadata(),
            )
            
        gen_manifest: ModelManifest | None = getattr(request.app.state, "general_insect_manifest", None)
        gen_detector: GeneralInsectClassifier | None = getattr(request.app.state, "general_insect_detector", None)
        
        metadata = (
            ModelMetadata(id=gen_manifest.model_id, version=gen_manifest.version, datasetVersion=gen_manifest.dataset_version)
            if gen_manifest is not None
            else _unavailable_metadata()
        )
        
        if gen_detector is None:
            return IdentifyResponse(
                status=IdentificationStatus.UNKNOWN,
                reason=UnknownReason.MODEL_UNAVAILABLE,
                prediction=None,
                model=metadata,
            )
            
        async with inference_slots:
            detection = await asyncio.to_thread(gen_detector.identify, decoded.rgb)
            
        if detection is None:
            return IdentifyResponse(
                status=IdentificationStatus.UNKNOWN,
                reason=UnknownReason.NO_DETECTION,
                prediction=None,
                model=metadata,
            )
            
        return IdentifyResponse(
            status=IdentificationStatus.IDENTIFIED,
            reason=None,
            prediction=detection.prediction,
            model=metadata,
        )
    assert crop_id is not None
    manifest: ModelManifest | None = request.app.state.manifest
    detector: PestDetector | None = request.app.state.detector
    metadata = (
        ModelMetadata(id=manifest.model_id, version=manifest.version, datasetVersion=manifest.dataset_version)
        if manifest is not None
        else _unavailable_metadata()
    )
    subject_size_warning = quality.reason is ValidationReason.SUBJECT_TOO_SMALL
    if not quality.valid and not subject_size_warning:
        return IdentifyResponse(
            status=IdentificationStatus.REJECTED_IMAGE,
            reason=quality.reason,
            prediction=None,
            model=metadata,
        )
    if subject_size_warning:
        small_subject_manifest: ModelManifest | None = request.app.state.small_subject_manifest
        small_subject_detector: PestDetector | None = request.app.state.small_subject_detector
        if small_subject_manifest is None or small_subject_detector is None:
            return IdentifyResponse(
                status=IdentificationStatus.REJECTED_IMAGE,
                reason=ValidationReason.SUBJECT_TOO_SMALL,
                prediction=None,
                model=metadata,
            )
        manifest = small_subject_manifest
        detector = small_subject_detector
        metadata = ModelMetadata(
            id=manifest.model_id,
            version=manifest.version,
            datasetVersion=manifest.dataset_version,
        )
    if detector is None:
        return IdentifyResponse(
            status=IdentificationStatus.UNKNOWN,
            reason=UnknownReason.MODEL_UNAVAILABLE,
            prediction=None,
            model=metadata,
        )
    async with inference_slots:
        detection = await asyncio.to_thread(detector.identify, decoded.rgb, crop_id)
    if detection is None:
        if subject_size_warning:
            return IdentifyResponse(
                status=IdentificationStatus.REJECTED_IMAGE,
                reason=ValidationReason.SUBJECT_TOO_SMALL,
                prediction=None,
                model=metadata,
            )
        return IdentifyResponse(
            status=IdentificationStatus.UNKNOWN,
            reason=UnknownReason.NO_DETECTION,
            prediction=None,
            model=metadata,
        )
    return IdentifyResponse(
        status=IdentificationStatus.IDENTIFIED,
        reason=None,
        prediction=detection.prediction,
        model=metadata,
    )
