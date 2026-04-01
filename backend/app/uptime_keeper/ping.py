import httpx

async def ping(url: str):
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(url, timeout=10)
        print(f"Pinged {url} → {r.status_code}", flush=True)
        return {"url": url, "status": "up", "code": r.status_code}
    except Exception as e:
        print(f"Failed {url} → {e}", flush=True)
        return {"url": url, "status": "down", "reason": str(e)}

