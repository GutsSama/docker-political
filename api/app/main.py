from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.api import api_router

app = FastAPI(
    version="1.0.0"
)

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


@app.get("/")
async def root():
    return {"message": "Hello World"}