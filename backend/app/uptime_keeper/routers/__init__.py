from .monitors import router as monitor_router
from .ping import router as ping_router
from fastapi import APIRouter


router =APIRouter()

router.include_router(ping_router)
router.include_router(monitor_router)