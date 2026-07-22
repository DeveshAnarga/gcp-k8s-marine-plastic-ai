"""
CloudEco: Marine Plastic Detection System
Author: Devesh Gurusinghe ()
Purpose: Image encoding/decoding utilities (base64, JPEG optimization)
Date: 2026-04-30
"""

import base64
import io

from PIL import Image

# ============================================
# BASE64 NORMALIZATION
# ============================================


def _normalize_base64_input(raw_value: str) -> str:
    # I accept both raw base64 and data-URL style strings (data:image/jpeg;base64,...).
    if "," in raw_value and raw_value.strip().startswith("data:"):
        return raw_value.split(",", 1)[1]
    return raw_value


# ============================================
# DECODE
# ============================================


def decode_base64_image(image_base64: str) -> Image.Image:
    # I decode client images here before passing them into YOLO.
    normalized = _normalize_base64_input(image_base64.strip())
    try:
        image_bytes = base64.b64decode(normalized, validate=True)
    except Exception as exc:
        raise ValueError("Invalid base64 image payload.") from exc

    try:
        # I force RGB because YOLO expects 3-channel images.
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as exc:
        raise ValueError("Decoded payload is not a valid image.") from exc

    return image


# ============================================
# ENCODE
# ============================================


def encode_image_to_base64(image: Image.Image, fmt: str = "JPEG", quality: int = 95) -> str:
    # I default to JPEG because PNG annotate payloads were massive and killed QPS in Locust tests.
    buffer = io.BytesIO()
    kwargs = {"format": fmt}
    if fmt == "JPEG":
        kwargs["quality"] = quality  # I use 95 as a good balance of size vs visual quality.
    image.save(buffer, **kwargs)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")
