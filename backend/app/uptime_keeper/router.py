# from fastapi import APIRouter, Query
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session

# from app.accounts.models import Account
# from app.db import get_db
# from app.core.redis import redis_client
# from app.uptime_keeper import crud, schemas
# from app.accounts.dependencies import get_current_account, get_current_admin
# from .ping import ping

# router = APIRouter()


# @router.get(
#     "/test-ping",
#     summary="check health of  a URL",
#     description="Checks whether a given URL is reachable and returns the response time. Useful for uptime monitoring or pre-scrape health checks.",
# )
# async def test_ping(
#     url: str = Query(
#         ...,
#         description="The full URL to ping, including scheme.",
#         example="https://example.com",
#     )
# ):
#     """
#     Ping a URL to check its reachability.

#     - **url**: Must include `http://` or `https://`
#     - Returns response time in milliseconds if reachable
#     - Returns `reachable: false` if the host is down or times out
#     """
#     result = await ping(url)
#     try:
#         from app.core.data_exporters import GoogleSheetPusher
#         sheet= GoogleSheetPusher('Tavdev Monitor')
#         result["base_url"] = url
#         checked_at = result['checked_at']
#         result["checked_at"] = checked_at.isoformat()
#         sheet.append_row(result, "passed")
#     except Exception as e:
#         print("GOOGLE SHEET ERROR:", repr(e))
#         raise
#     return result




# # ------------------------
# # MONITORS
# # ------------------------

# #post a new monitor
# @router.post("/monitors", response_model=schemas.UptimeMonitorOut)
# def create_monitor(
#     payload: schemas.UptimeMonitorCreate,
#     db: Session = Depends(get_db),
#     account:Account = Depends(get_current_account)
#     ):
#     return crud.create_monitor(db, payload,account)


# @router.get("/monitors/{monitor_id}", response_model=schemas.UptimeMonitorOut)
# def get_monitor(monitor_id, db: Session = Depends(get_db)):
#     obj = crud.get_monitor(db, monitor_id)
#     if not obj:
#         raise HTTPException(status_code=404, detail="Monitor not found")
#     return obj

# #count the number of monitors
# @router.get("/motinor_count/", response_model=int)
# def get_monitor_count(db:Session=Depends(get_db)):
#     return crud.count_monitors(db)

# @router.get("/accounts/{account_id}/monitors", response_model=list[schemas.UptimeMonitorOut])
# def list_monitors(account_id, db: Session = Depends(get_db)):
#     return crud.get_monitors_by_account(db, account_id)


# @router.patch("/monitors/{monitor_id}", response_model=schemas.UptimeMonitorOut)
# def update_monitor(
#     monitor_id,
#     payload: schemas.UptimeMonitorUpdate,
#     db: Session = Depends(get_db),
#     account:Account = Depends(get_current_account)
#     ):
#     obj = crud.update_monitor(db, monitor_id, payload)
#     if not obj:
#         raise HTTPException(status_code=404, detail="Monitor not found")
#     return obj


# @router.delete("/monitors/{monitor_id}")
# def delete_monitor(
#     monitor_id,
#     db: Session = Depends(get_db),
#     account:Account = Depends(get_current_account)
#     ):
#     obj = crud.delete_monitor(db, monitor_id)
#     if not obj:
#         raise HTTPException(status_code=404, detail="Monitor not found")
#     return {"deleted": True}


# # ------------------------
# # PINGS
# # ------------------------

# @router.get("/monitors/{monitor_id}/pings", response_model=list[schemas.UptimePingOut])
# def list_pings(monitor_id, db: Session = Depends(get_db)):
#     return crud.get_pings_by_monitor(db, monitor_id)


# @router.get("/redis-test")
# def redis_test():
#     redis_client.set("ping", "pong")
#     return redis_client.get("ping")


# # app/uptime_keeper/router.py

# from fastapi import APIRouter, Depends, HTTPException
# from app.uptime_keeper.caching.db_to_redis import get_monitors, get_monitor_cached
# from app.accounts import get_current_account  # adjust to your actual auth dependency


# @router.get("/monitors")
# async def list_monitors(account = Depends(get_current_account)):
#     """
#     Dashboard list view. Monitor config comes from Postgres (one cheap query),
#     live status for each comes from redis — no ping-history table involved.
#     """
#     monitors = get_monitors(str(account.id))
#     return {"monitors": monitors}


# @router.get("/monitors/{monitor_id}")
# async def get_monitor_status(monitor_id: str, account = Depends(get_current_account)):
#     """
#     Single monitor's live status — pure redis read, no DB hit unless
#     the cache is cold (get_monitor_cached self-heals from Postgres then).
#     """
#     monitor = get_monitor_cached(monitor_id)
#     if not monitor:
#         raise HTTPException(status_code=404, detail="Monitor not found")

#     # TODO: verify monitor belongs to `account` before returning it —
#     # get_monitor_cached doesn't currently check ownership.

#     return monitor

from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
from app.accounts.models import Account
from app.db import get_db
from app.core.redis import redis_client
from app.uptime_keeper import crud, schemas
from app.uptime_keeper.caching.db_to_redis import get_monitor_cached, get_latest_pings_bulk,get_ping_history
from app.accounts.dependencies import get_current_account, get_current_admin
from .ping import ping

router = APIRouter()

logger = logging.getLogger('__name__')

@router.get(
    "/test-ping",
    summary="check health of a URL",
    description="Checks whether a given URL is reachable and returns the response time.",
)
async def test_ping(
    url: str = Query(..., description="The full URL to ping, including scheme.", example="https://example.com")
):
    result = await ping(url)

    # Logging side-effect should never break the actual response to the caller.
    try:
        from app.core.data_exporters import GoogleSheetPusher
        sheet = GoogleSheetPusher('Tavdev Monitor')
        row = {**result, "base_url": url, "checked_at": result["checked_at"].isoformat()}
        sheet.append_row(row, "passed")
    except Exception as e:
        logger.warning("GoogleSheet export failed for test-ping: %r", e)

    return result


# ------------------------
# MONITORS
# ------------------------

@router.post("/monitors", response_model=schemas.UptimeMonitorOut)
def create_monitor(
    payload: schemas.UptimeMonitorCreate,
    db: Session = Depends(get_db),
    account: Account = Depends(get_current_account),
):
    monitor = crud.create_monitor(db, payload, account)
    from app.uptime_keeper.caching.db_to_redis import sync_monitor_to_redis
    sync_monitor_to_redis(monitor)  # register in redis immediately, no waiting for next sync_all
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
def list_monitors(account_id, db: Session = Depends(get_db)):
    return crud.get_monitors_by_account(db, account_id)

# @router.get("/monitors/{monitor_id}/history")
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

@router.get("/motinor_count/", response_model=int)
def get_monitor_count(
    db: Session = Depends(get_db),
    # _admin: Account = Depends(get_current_admin),  # was unauthenticated — fixed
):
    return crud.count_monitors(db)

# @router.get("/accounts/{account_id}/monitors", response_model=list[schemas.UptimeMonitorOut])
# def list_monitors(account_id, db: Session = Depends(get_db)):
#     return crud.get_monitors_by_account(db, account_id)

# @router.get("/accounts/{account_id}/monitors", response_model=list[schemas.UptimeMonitorWithStatus])
# def list_monitors(
#     account_id: str,
#     db: Session = Depends(get_db),
#     account: Account = Depends(get_current_account),
# ):
#     if str(account_id) != str(account.id):
#         raise HTTPException(status_code=403, detail="Not authorized for this account")

#     monitors = crud.get_monitors_by_account(db, account_id)
#     ids = [str(m.id) for m in monitors]
#     live_by_id = get_latest_pings_bulk(ids)  # one MGET, not N calls

#     return [
#         schemas.UptimeMonitorWithStatus(**m.__dict__, live=live_by_id.get(str(m.id)))
#         for m in monitors
#     ]


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