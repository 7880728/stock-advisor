"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.scheduler.eod import setup_eod_scheduler
from app.api import dashboard, stock, strategy, signals


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    setup_eod_scheduler()
    yield


app = FastAPI(
    title="Stock Advisor",
    description="A股智能股票顾问系统",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(dashboard.router)
app.include_router(stock.router)
app.include_router(strategy.router)
app.include_router(signals.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
