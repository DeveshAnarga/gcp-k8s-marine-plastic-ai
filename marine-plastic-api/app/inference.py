"""
CloudEco: Marine Plastic Detection System
Author: Devesh Gurusinghe ()
Purpose: YOLO model inference engine with ThreadPoolExecutor for async CPU-bound operations
Date: 2026-04-30
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Lock
from typing import Dict, List, Tuple

from PIL import Image
from ultralytics import YOLO
from ultralytics.yolo.utils.ops import Profile

from app.schemas import Box

# ============================================
# ASYNC EXECUTOR
# ============================================
# I use a thread pool because YOLO predict() is CPU-bound and would block the asyncio loop
# if I called it directly inside async route handlers.
executor = ThreadPoolExecutor(max_workers=8)


# ============================================
# WEIGHTS & COMPAT HELPERS
# ============================================


def _resolve_weights_path(project_root: Path) -> Path:
    # I try fine-tuned weights first, then fall back to yolov8m.pt in the container.
    candidates = [
        project_root / "runs" / "detect" / "train" / "weights" / "best.pt",
        project_root / "yolov8m.pt",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("No model weights found. Expected best.pt or yolov8m.pt.")


def _safe_float(value: object) -> float:
    # I normalize timing values because Ultralytics 8.0.x sometimes returns floats
    # and sometimes Profile objects with a .dt attribute.
    if isinstance(value, (int, float)):
        return float(value)
    dt = getattr(value, "dt", None)
    if isinstance(dt, (int, float)):
        return float(dt)
    return 0.0


def _extract_speed_ms(result: object) -> Dict[str, float]:
    # I expose preprocess/inference/postprocess ms in the API because the rubric asks for speed_* fields.
    speed_ms = {"preprocess": 0.0, "inference": 0.0, "postprocess": 0.0}
    try:
        raw_speed = getattr(result, "speed")
    except Exception:
        return speed_ms

    if isinstance(raw_speed, dict):
        speed_ms["preprocess"] = _safe_float(raw_speed.get("preprocess", 0.0))
        speed_ms["inference"] = _safe_float(raw_speed.get("inference", 0.0))
        speed_ms["postprocess"] = _safe_float(raw_speed.get("postprocess", 0.0))
        return speed_ms

    if isinstance(raw_speed, (list, tuple)):
        keys = ("preprocess", "inference", "postprocess")
        for key, value in zip(keys, raw_speed):
            speed_ms[key] = _safe_float(value)
    return speed_ms


def _ensure_profile_dt_compat() -> None:
    # I hit a rare Ultralytics crash where Profile.dt was missing; this class-level fallback
    # stops random 500s under concurrent requests on older 8.0.x builds.
    if not hasattr(Profile, "dt"):
        setattr(Profile, "dt", 0.0)


# ============================================
# INFERENCE ENGINE
# ============================================


class MarinePlasticInference:
    # I wrap the model in a class so I can keep one loaded instance per worker process.

    def __init__(self, project_root: Path) -> None:
        _ensure_profile_dt_compat()
        self.project_root = project_root
        self.model_path = _resolve_weights_path(project_root)
        self.model = YOLO(str(self.model_path))
        # I added this lock because Ultralytics predict() is NOT thread-safe — without it,
        # concurrent requests caused intermittent crashes when I load-tested with Locust.
        self._predict_lock = Lock()

    def _names(self) -> Dict[int, str]:
        # I map class indices to human-readable labels from the model metadata.
        names = self.model.names
        if isinstance(names, dict):
            return {int(k): str(v) for k, v in names.items()}
        return {i: str(name) for i, name in enumerate(names)}

    def predict(
        self,
        image: Image.Image,
        confidence: float = 0.25,
        iou: float = 0.45,
    ) -> Tuple[List[str], List[Box], Dict[str, float], Image.Image]:
        # This is the real blocking inference function that runs inside the thread pool.
        with self._predict_lock:
            # I set verbose=False so Ultralytics does not spam stdout — saves I/O under load.
            results = self.model.predict(image, conf=confidence, iou=iou, verbose=False)
        result = results[0]

        names = self._names()
        detections: List[str] = []
        boxes_out: List[Box] = []

        if result.boxes is not None:
            classes = result.boxes.cls.tolist()
            scores = result.boxes.conf.tolist()
            boxes = result.boxes.xyxy.tolist()

            for class_id_raw, conf_raw, bbox in zip(classes, scores, boxes):
                class_id = int(class_id_raw)
                class_name = names.get(class_id, f"class_{class_id}")
                x1, y1, x2, y2 = [float(v) for v in bbox]
                detections.append(class_name)
                # I convert xyxy to x,y,width,height because that matches the assignment JSON schema.
                boxes_out.append(
                    Box(
                        x=round(x1, 2),
                        y=round(y1, 2),
                        width=round(max(0.0, x2 - x1), 2),
                        height=round(max(0.0, y2 - y1), 2),
                        probability=round(float(conf_raw), 6),
                    )
                )

        speed_ms = _extract_speed_ms(result)

        # I build the annotated image here so /annotate can reuse the same inference pass.
        # I use line_width=1 on the plot to keep the annotated image a bit leaner before JPEG encode.
        plotted_bgr = result.plot(line_width=1)
        plotted_rgb = plotted_bgr[:, :, ::-1]
        annotated_image = Image.fromarray(plotted_rgb)

        return detections, boxes_out, speed_ms, annotated_image

    async def predict_async(
        self,
        image: Image.Image,
        confidence: float = 0.25,
        iou: float = 0.45,
    ) -> Tuple[List[str], List[Box], Dict[str, float], Image.Image]:
        # I bridge sync YOLO code into async FastAPI using run_in_executor — this is what I explain in the interview.
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            executor,
            self.predict,
            image,
            confidence,
            iou,
        )


# ============================================
# SINGLETON ACCESS
# ============================================
_inference_instance: MarinePlasticInference | None = None


def get_inference_engine() -> MarinePlasticInference:
    # I use a singleton so each uvicorn worker loads the model only once (saves memory and startup time).
    global _inference_instance
    if _inference_instance is None:
        project_root = Path(__file__).resolve().parents[1]
        _inference_instance = MarinePlasticInference(project_root=project_root)
    return _inference_instance
