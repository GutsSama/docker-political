from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routers.api import api_router
from app.middleware.metrics import PrometheusMiddleware, metrics_endpoint

app = FastAPI(
    title="Prédi'lection API",
    version="1.0.0",
    description="API de prédiction politique — FastAPI + PostgreSQL",
)

# ─── Middleware Prometheus ────────────────────────────────────────────────────
app.add_middleware(PrometheusMiddleware)

origins = [
    "http://localhost",
    "http://localhost:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# ─── Endpoint métriques Prometheus ───────────────────────────────────────────
app.add_route("/metrics", metrics_endpoint, include_in_schema=False)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health", tags=["Health"])
async def health_check():
    """Endpoint de health check pour Uptime Kuma et les load balancers."""
    return {"status": "ok", "service": "predilection-api"}