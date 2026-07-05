# app/uptime_keeper/constants.py
import os

SCHEDULE_PREFIX = os.getenv("SCHEDULE_PREFIX", "schedule:monitor:")
SCHEDULE_ZSET_KEY = os.getenv("SCHEDULE_ZSET_KEY", "schedule:monitor:zset")
PER_USER_MONITOR = os.getenv("PER_USER_MONITOR")