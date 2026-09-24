from .health import router as health_router
from .checker import router as checker_router
from .history import router as history_router

__all__ = ["health_router", "checker_router", "history_router"]

from .report import router as report_router
