from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.init_db import init_db

app = FastAPI(title="PaperBridge API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}
