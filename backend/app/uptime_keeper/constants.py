"""
Redis key naming conventions and scheduler configuration.

These constants centralize Redis key names and scheduling limits
to avoid hard-coded values across the codebase. Updating a key
or limit only requires changing it here.
"""

import os

# ------------------------------------------------------------------
# Redis Keys
# ------------------------------------------------------------------

# Prefix used for storing monitor schedules.
SCHEDULE_PREFIX = os.getenv(
    "SCHEDULE_PREFIX",
    "schedule:monitor:",
)

# Sorted set tracking the next execution time of every monitor.
SCHEDULE_ZSET_KEY = os.getenv(
    "SCHEDULE_ZSET_KEY",
    "schedule:monitor:zset",
)

# ------------------------------------------------------------------
# Application Limits
# ------------------------------------------------------------------

# Maximum number of monitors allowed for a single user.
MAX_MONITORS_PER_USER = int(
    os.getenv("PER_USER_MONITOR", "10")
)