from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.db import Base, engine
from app.exceptions import SubLedgerError
from app.routes import customers, invoices, payments, plans, subscriptions


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Only runs when the app actually starts serving (uvicorn, or a test
    # using `with TestClient(app)`) — never at bare import time, so tests
    # can swap in a different engine via dependency_overrides first.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="SubLedger",
    description="A simplified SaaS subscription & billing backend.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.exception_handler(SubLedgerError)
def handle_domain_error(request: Request, exc: SubLedgerError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


app.include_router(plans.router)
app.include_router(customers.router)
app.include_router(subscriptions.router)
app.include_router(invoices.router)
app.include_router(payments.router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
