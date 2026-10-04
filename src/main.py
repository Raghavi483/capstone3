from contextlib import asynccontextmanager
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from src.repositories.database import init_db
from src.controllers.health_controller import router as health_router
from src.controllers.eligibility_controller import router as eligibility_router
from src.controllers.pre_auth_controller import router as pre_auth_router
from src.controllers.claim_controller import router as claim_router
from src.controllers.settlement_controller import router as settlement_router
from src.utils.logger import get_logger

logger = get_logger("medicard.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("MediCard database initialized successfully")
    yield


app = FastAPI(
    title="MediCard Health Cashless Platform",
    description="Automated cashless hospitalization, adjudication, and settlement API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response


import os
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app.include_router(health_router)
app.include_router(eligibility_router)
app.include_router(pre_auth_router)
app.include_router(claim_router)
app.include_router(settlement_router)

frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    @app.get("/")
    def serve_frontend_index():
        return FileResponse(str(frontend_dir / "index.html"))
