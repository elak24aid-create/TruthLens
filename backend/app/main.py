from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.routers.health import router as health_router
from app.routers.checker import router as checker_router
from app.routers.history import router as history_router
from app.routers.research import router as research_router
from app.routers.news import router as news_router
from app.routers.report import router as report_router
from app.routers.auth import router as auth_router
from app.utils.rate_limiter import SimpleRateLimiter

app = FastAPI(
    title="TruthLens API",
    description="AI-Assisted Fake News Detection Platform API providing explainable multi-signal evidence verification.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiter dependency
rate_limiter = SimpleRateLimiter(requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)


@app.middleware("http")
async def rate_limit_and_logging_middleware(request: Request, call_next):
    # Apply rate limiting to /api/ endpoints (excluding /api/health)
    if request.url.path.startswith("/api/") and not request.url.path.endswith("/health"):
        try:
            rate_limiter(request)
        except Exception as exc:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Too many requests. Please slow down and try again."},
            )

    response = await call_next(request)
    return response


# Validation Exception Handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = " -> ".join(str(loc) for loc in err.get("loc", []))
        errors.append(f"{field}: {err.get('msg')}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Input validation error",
            "errors": errors,
        },
    )


# Generic Exception Handler (No raw stack traces to end users)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected server error occurred. Please try again later.",
        },
    )


# Root route
@app.get("/")
def root():
    return {
        "message": "Welcome to TruthLens API — AI Fake News Detection Platform",
        "documentation": "/docs",
        "health": "/api/health",
    }


# Include Routers with /api prefix
app.include_router(health_router, prefix="/api")
app.include_router(checker_router, prefix="/api")
app.include_router(history_router, prefix="/api")
app.include_router(research_router, prefix="/api")
app.include_router(news_router, prefix="/api")
app.include_router(report_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
