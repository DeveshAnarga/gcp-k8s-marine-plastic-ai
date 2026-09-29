"""
CloudEco: Marine Plastic Detection System
Author: Devesh Gurusinghe
Purpose: Locust load testing script for benchmarking concurrent user performance
Date: 2026-04-30
"""

import base64
import logging
from pathlib import Path

from locust import HttpUser, between, events, task

logger = logging.getLogger(__name__)

# ============================================
# TEST PAYLOAD (PRE-LOADED)
# ============================================
# I load t2.jpg once at import time so Locust does not waste CPU re-encoding on every request.
IMAGE_PATH = Path(__file__).resolve().parent / "Test_images" / "t2.jpg"
IMAGE_B64 = base64.b64encode(IMAGE_PATH.read_bytes()).decode("utf-8")


# ============================================
# SIMULATED USER
# ============================================
class MarinePlasticUser(HttpUser):
    # I point Locust at my NodePort service on the GCP master public IP.

    host = "http://34.151.142.31:30080"
    # I add a small wait between tasks to simulate realistic user pacing (not hammering back-to-back).
    wait_time = between(0.1, 0.5)

    def on_start(self) -> None:
        # I give each simulated user a unique id so uuid values are easy to trace in logs.
        self._user_id = id(self)

    def _payload(self) -> dict[str, str]:
        # I build the same JSON body shape as the real API (ImageRequest).
        user_id = getattr(self, "_user_id", "unknown")
        return {
            "uuid": f"locust-test-user-{user_id}",
            "image": IMAGE_B64,
        }

    def _post_and_validate(self, endpoint: str, request_name: str) -> None:
        # I validate responses so Locust failure % reflects real API errors, not just HTTP status.
        try:
            with self.client.post(
                endpoint,
                json=self._payload(),
                headers={"Content-Type": "application/json"},
                name=request_name,
                catch_response=True,
            ) as response:
                if response.status_code != 200:
                    response.failure(f"Expected HTTP 200, got {response.status_code}")
                    return

                try:
                    body = response.json()
                except Exception as exc:
                    response.failure(f"Invalid JSON response: {exc}")
                    return

                if "count" not in body:
                    response.failure("Missing 'count' field in response.")
                    return
                if "boxes" not in body or not isinstance(body["boxes"], list):
                    response.failure("Missing or invalid 'boxes' array in response.")
                    return

                response.success()
        except Exception as exc:
            logger.exception("Request error on %s: %s", endpoint, exc)
            events.request.fire(
                request_type="POST",
                name=request_name,
                response_time=0,
                response_length=0,
                exception=exc,
                context={},
            )

    # ============================================
    # TASKS
    # ============================================
    @task(1)
    def predict_task(self) -> None:
        # I test /api/predict — lighter response (no big image in JSON).
        self._post_and_validate("/api/predict", "POST /api/predict")

    @task(1)
    def annotate_task(self) -> None:
        # I test /api/annotate — heavier because of base64 image in the response.
        self._post_and_validate("/api/annotate", "POST /api/annotate")
