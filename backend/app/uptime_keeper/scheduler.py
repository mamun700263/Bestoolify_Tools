import asyncio
from .ping import ping

URLS =[
    "https://bestoolify-tools-background-tasks.onrender.com/",
    "https://narayanpur-high-school.onrender.com/",
    "https://online-school-1wkk.onrender.com/", 
    "https://dashboard.render.com/web/srv-d24v6ufdiees739njq8g",
    "https://google.com",
]
async def scheduler():
    while True:
        print("--- pinging all urls ---", flush=True)
        results = await asyncio.gather(*[ping(u) for u in URLS])
        for r in results:
            print(r, flush=True)
        await asyncio.sleep(30)  # 30 seconds for testing
