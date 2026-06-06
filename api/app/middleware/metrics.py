"""
Middleware Prometheus pour FastAPI.

Métriques exposées :
    - http_requests_total         : nombre de requêtes par méthode, endpoint, status code
    - http_request_duration_seconds : latence par méthode et endpoint (histogram)
    - http_requests_in_progress   : requêtes en cours (gauge)
    - api_errors_total            : nombre d'erreurs 4xx/5xx par endpoint
"""

import time
from typing import Callable

from fastapi import Request, Response
from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    CollectorRegistry,
    CONTENT_TYPE_LATEST,
    generate_latest,
)
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import Match

# ─── Registry global ──────────────────────────────────────────────────────────
REGISTRY = CollectorRegistry(auto_describe=True)

# ─── Métriques ────────────────────────────────────────────────────────────────
HTTP_REQUESTS_TOTAL = Counter(
    name="http_requests_total",
    documentation="Nombre total de requêtes HTTP reçues",
    labelnames=["method", "endpoint", "status_code"],
    registry=REGISTRY,
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    name="http_request_duration_seconds",
    documentation="Durée des requêtes HTTP en secondes",
    labelnames=["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
    registry=REGISTRY,
)

HTTP_REQUESTS_IN_PROGRESS = Gauge(
    name="http_requests_in_progress",
    documentation="Nombre de requêtes HTTP en cours de traitement",
    labelnames=["method", "endpoint"],
    registry=REGISTRY,
)

API_ERRORS_TOTAL = Counter(
    name="api_errors_total",
    documentation="Nombre total d'erreurs HTTP (4xx et 5xx)",
    labelnames=["method", "endpoint", "status_code"],
    registry=REGISTRY,
)


def _get_route_path(request: Request) -> str:
    """Résout le path de route FastAPI (ex: /predict/{id} et non /predict/42)."""
    for route in request.app.routes:
        match, _ = route.matches(request.scope)
        if match == Match.FULL:
            return route.path  # type: ignore[union-attr]
    return request.url.path  # fallback sur le path brut


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware qui collecte les métriques Prometheus sur chaque requête."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        endpoint = _get_route_path(request)
        method = request.method

        # Exclure l'endpoint /metrics lui-même pour éviter la récursion
        if endpoint == "/metrics":
            return await call_next(request)

        HTTP_REQUESTS_IN_PROGRESS.labels(method=method, endpoint=endpoint).inc()
        start_time = time.perf_counter()

        try:
            response: Response = await call_next(request)
            status_code = str(response.status_code)
        except Exception:
            status_code = "500"
            HTTP_ERRORS_TOTAL = API_ERRORS_TOTAL.labels(
                method=method, endpoint=endpoint, status_code=status_code
            )
            HTTP_ERRORS_TOTAL.inc()
            raise
        finally:
            duration = time.perf_counter() - start_time
            HTTP_REQUESTS_IN_PROGRESS.labels(method=method, endpoint=endpoint).dec()
            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=method, endpoint=endpoint
            ).observe(duration)

        HTTP_REQUESTS_TOTAL.labels(
            method=method, endpoint=endpoint, status_code=status_code
        ).inc()

        # Enregistrer les erreurs 4xx/5xx
        if response.status_code >= 400:
            API_ERRORS_TOTAL.labels(
                method=method, endpoint=endpoint, status_code=status_code
            ).inc()

        return response


async def metrics_endpoint(request: Request) -> Response:
    """Endpoint /metrics exposant les métriques au format Prometheus."""
    data = generate_latest(REGISTRY)
    return Response(
        content=data,
        media_type=CONTENT_TYPE_LATEST,
    )
