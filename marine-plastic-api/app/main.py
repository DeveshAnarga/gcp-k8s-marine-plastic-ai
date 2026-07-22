"""
CloudEco: Marine Plastic Detection System
Author: Devesh Gurusinghe ()
Purpose: FastAPI application with async predict/annotate endpoints for YOLO inference
Date: 2026-04-30
"""

from fastapi import FastAPI, HTTPException

from app.inference import get_inference_engine
from app.schemas import AnnotateResponse, ImageRequest, PredictResponse
from app.utils import decode_base64_image, encode_image_to_base64

# ============================================
# APPLICATION
# ============================================
# I use FastAPI here because the assignment needs a JSON REST API with clear schemas.
app = FastAPI(title="Marine Plastic Detection API", version="1.0.0")


# ============================================
# ROOT (BROWSER-FRIENDLY)
# ============================================
@app.get("/")
def root() -> dict:
    # I added this route so markers can open the base URL in a browser and immediately
    # see the service is live (without needing POST or Swagger).
    return {
        "service": "Marine Plastic Detection API",
        "status": "live",
        "health": "/health",
        "docs": "/docs",
        "predict": "POST /api/predict",
        "annotate": "POST /api/annotate",
    }


# ============================================
# HEALTH
# ============================================
@app.get("/health")
def health() -> dict:
    # I keep /health very cheap (no model call) because Kubernetes liveness/readiness
    # probes hit this endpoint every few seconds.
    return {"status": "ok"}


# ============================================
# STARTUP
# ============================================
@app.on_event("startup")
def startup_load_model() -> None:
    # I load YOLO once at startup so a broken model file fails the pod early,
    # instead of failing randomly on the first real user request.
    get_inference_engine()


# ============================================
# PREDICT
# ============================================
@app.post("/api/predict", response_model=PredictResponse)
async def predict(request: ImageRequest) -> PredictResponse:
    # I made this endpoint async even though YOLO itself is blocking, because I offload
    # the heavy work to a thread pool (see inference.py) and keep the event loop free.
    try:
        image = decode_base64_image(request.image)
    except ValueError as exc:
        # I return HTTP 400 for bad base64 so clients get a clear validation error.
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # I await predict_async here — that is the key concurrency design for the assignment.
    detections, boxes, speed_ms, _ = await get_inference_engine().predict_async(image=image)

    # I echo the client uuid and map Ultralytics timing fields into the response schema.
    return PredictResponse(
        uuid=request.uuid,
        count=len(boxes),
        detections=detections,
        boxes=boxes,
        speed_preprocess_ms=speed_ms["preprocess"],
        speed_inference_ms=speed_ms["inference"],
        speed_postprocess_ms=speed_ms["postprocess"],
    )


# ============================================
# ANNOTATE
# ============================================
@app.post("/api/annotate", response_model=AnnotateResponse)
async def annotate(request: ImageRequest) -> AnnotateResponse:
    # I use the same inference path as /predict, but I also return the drawn image.
    try:
        image = decode_base64_image(request.image)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    detections, boxes, speed_ms, annotated = await get_inference_engine().predict_async(image=image)

    # I encode as JPEG (not PNG) because annotate responses were huge and slow under load.
    return AnnotateResponse(
        uuid=request.uuid,
        count=len(boxes),
        detections=detections,
        boxes=boxes,
        speed_preprocess_ms=speed_ms["preprocess"],
        speed_inference_ms=speed_ms["inference"],
        speed_postprocess_ms=speed_ms["postprocess"],
        annotated_image=encode_image_to_base64(annotated, fmt="JPEG"),
    )
