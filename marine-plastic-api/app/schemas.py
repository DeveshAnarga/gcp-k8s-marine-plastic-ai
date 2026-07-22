"""
CloudEco: Marine Plastic Detection System
Author: Devesh Gurusinghe ()
Purpose: Pydantic data models for API request/response validation
Date: 2026-04-30
"""

from typing import List

from pydantic import BaseModel, Field

# ============================================
# REQUEST
# ============================================
# I use Pydantic so FastAPI validates incoming JSON automatically against the assignment spec.


class ImageRequest(BaseModel):
    # Every request must include uuid + base64 image — I enforce that here.
    uuid: str = Field(..., description="Client-provided request UUID.")
    image: str = Field(..., description="Base64 encoded image content.")


# ============================================
# DETECTION BOX
# ============================================


class Box(BaseModel):
    # I match the rubric box format: top-left x,y plus width/height and confidence.
    x: float
    y: float
    width: float
    height: float
    probability: float


# ============================================
# RESPONSES
# ============================================


class PredictResponse(BaseModel):
    # I return everything /predict needs, including the three speed_* timing fields.
    uuid: str
    count: int
    detections: List[str]
    boxes: List[Box]
    speed_preprocess_ms: float
    speed_inference_ms: float
    speed_postprocess_ms: float


class AnnotateResponse(PredictResponse):
    # I extend PredictResponse so /annotate returns the same fields plus annotated_image.
    annotated_image: str
