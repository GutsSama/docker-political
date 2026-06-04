from fastapi import FastAPI
from app.routers.api import api_router

app = FastAPI(
    version="1.0.0",
    root_path="/api",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)
app.include_router(api_router)

origins = [
    "http://localhost",
    "http://localhost:8080"
]


@app.get("/")
async def root():
    return {"message": "Hello World"}
