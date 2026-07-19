import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.init_db import init_db
from app.routers import cases, documents
from app.seed import run as seed_demo_case

app = FastAPI(title="PaperBridge API")

# In local/demo mode (no FRONTEND_ORIGIN set) allow any origin so the app
# works out of the box. In deployment, set FRONTEND_ORIGIN to the deployed
# Vercel URL to restrict CORS to the real frontend.
_frontend_origin = os.environ.get("FRONTEND_ORIGIN")
_allow_origins = [_frontend_origin] if _frontend_origin else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allow_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()
    seed_demo_case()


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(cases.router)
app.include_router(documents.router)
