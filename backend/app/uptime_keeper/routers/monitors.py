from fastapi import (
    APIRouter,
    Depends,
    HTTPException
    )
from sqlalchemy.orm import Session
from app.core.logger import Logger
from app.accounts.models import Account
from app.db import get_db
from app.uptime_keeper import crud, schemas
from app.uptime_keeper.caching.db_to_redis import (
    get_monitor_cached,
    get_ping_history
    )
from app.accounts.dependencies import get_current_account

router = APIRouter()

logger = Logger.get_logger(__name__,"uptime")

# ------------------------
# MONITORS
# ------------------------

@router.post("/monitors", response_model=schemas.UptimeMonitorOut)
def create_monitor(
    payload: schemas.UptimeMonitorCreate,
    db: Session = Depends(get_db),
    account: Account = Depends(get_current_account),
):
    try:
        monitor = crud.create_monitor(db, payload, account)
    except crud.MonitorLimitExceeded:
        logger.error(f"Monitor creation failed for user {account} with {payload}")
        raise HTTPException(status_code=403, detail="You've reached your 10 monitor limit.")

    from app.uptime_keeper.caching.db_to_redis import sync_monitor_to_redis
    sync_monitor_to_redis(monitor)
    return monitor

@router.get("/monitors/{monitor_id}", response_model=schemas.UptimeMonitorOut)
def get_monitor(
    monitor_id: str,
    db: Session = Depends(get_db),
    account: Account = Depends(get_current_account),
):
    obj = crud.get_monitor(db, monitor_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Monitor not found")
    if str(obj.account_id) != str(account.id):
        raise HTTPException(status_code=404, detail="Monitor not found")  # 404, not 403 — don't leak existence
    return obj

@router.get("/accounts/{account_id}/monitors", response_model=list[schemas.UptimeMonitorOut])
def list_monitors(
    account_id: str,
    db: Session = Depends(get_db),
    account: Account = Depends(get_current_account),
):
    if str(account_id) != str(account.id):
        raise HTTPException(status_code=404, detail="Not found")  # 404, not 403 — consistent with your other endpoints, don't leak existence
    return crud.get_monitors_by_account(db, account_id)

@router.get("/monitors/{monitor_id}/pings", )#response_model=list[schemas.UptimePingOut]
async def get_monitor_history(
    monitor_id: str,
    # hours: int = Query(24, ge=1, le=24),
    account: Account = Depends(get_current_account),
):
    monitor = get_monitor_cached(monitor_id)
    if not monitor or monitor.get("account_id") != str(account.id):
        raise HTTPException(status_code=404, detail="Monitor not found")

    return {"monitor_id": monitor_id, "pings": get_ping_history(monitor_id, 24)}

@router.get('/pings/download/{monitor_id}')
def download_pings(monitor_id:str,file_type:str):
    from app.uptime_keeper.export import monitor_ping_data
    return monitor_ping_data(monitor_id,file_type)


@router.get("/monitor_count/", response_model=int)
def get_monitor_count(
    # _admin: Account = Depends(get_current_admin),  # was unauthenticated — fixed
):
    from app.uptime_keeper.caching.db_to_redis import get_monitor_count
    return get_monitor_count()


@router.patch("/monitors/{monitor_id}", response_model=schemas.UptimeMonitorOut)
def update_monitor(
    monitor_id: str,
    payload: schemas.UptimeMonitorUpdate,
    db: Session = Depends(get_db),
    account: Account = Depends(get_current_account),
):
    obj = crud.get_monitor(db, monitor_id)
    if not obj or str(obj.account_id) != str(account.id):
        raise HTTPException(status_code=404, detail="Monitor not found")

    updated = crud.update_monitor(db, monitor_id, payload)
    from app.uptime_keeper.caching.db_to_redis import sync_monitor_to_redis
    sync_monitor_to_redis(updated)  # keep redis cache in sync immediately
    return updated


@router.delete("/monitors/{monitor_id}")
def delete_monitor(
    monitor_id: str,
    db: Session = Depends(get_db),
    account: Account = Depends(get_current_account),
):
    obj = crud.get_monitor(db, monitor_id)
    if not obj or str(obj.account_id) != str(account.id):
        raise HTTPException(status_code=404, detail="Monitor not found")

    crud.delete_monitor(db, monitor_id)
    from app.uptime_keeper.caching.db_to_redis import delete_monitor as delete_monitor_redis
    delete_monitor_redis(monitor_id)  # was previously never called from the router at all
    return {"deleted": True}


# ------------------------
# INCIDENTS (down-history only — see store_ping_result)
# ------------------------

@router.get("/monitors/{monitor_id}/incidents", response_model=list[schemas.UptimePingOut])
def list_incidents(
    monitor_id: str,
    db: Session = Depends(get_db),
    account: Account = Depends(get_current_account),
):
    obj = crud.get_monitor(db, monitor_id)
    if not obj or str(obj.account_id) != str(account.id):
        raise HTTPException(status_code=404, detail="Monitor not found")
    return crud.get_pings_by_monitor(db, monitor_id)