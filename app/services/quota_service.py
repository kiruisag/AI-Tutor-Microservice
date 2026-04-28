import time
import logging
from collections import defaultdict
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class QuotaService:
    """
    Production-ready in-memory quota system (Redis-ready design)
    """

    def __init__(self):
        # tenant -> list of (timestamp, tokens, reserved)
        self.usage: Dict[str, List[Tuple[float, int, bool]]] = defaultdict(list)

        # per-tenant limits (can later come from DB)
        self.limits = defaultdict(lambda: 10000)

        # reservation tracking
        self.reserved: Dict[str, int] = defaultdict(int)

    # -----------------------
    # CLEANUP OLD RECORDS
    # -----------------------
    def _cleanup(self, tenant: str):
        now = time.time()
        window = 60  # 1-minute sliding window

        self.usage[tenant] = [
            (t, tokens, reserved)
            for (t, tokens, reserved) in self.usage[tenant]
            if now - t < window
        ]

    # -----------------------
    # AVAILABLE TOKENS
    # -----------------------
    def _used_tokens(self, tenant: str) -> int:
        return sum(tokens for _, tokens, _ in self.usage[tenant])

    # -----------------------
    # RESERVE (SAFE CHECK)
    # -----------------------
    def reserve(self, tenant: str, tokens: int) -> bool:
        self._cleanup(tenant)

        used = self._used_tokens(tenant)
        limit = self.limits[tenant]

        if used + self.reserved[tenant] + tokens > limit:
            return False

        # mark reserved (not yet committed)
        self.reserved[tenant] += tokens
        return True

    # -----------------------
    # COMMIT (FINALIZE USAGE)
    # -----------------------
    def commit(self, tenant: str, tokens: int):
        self.reserved[tenant] = max(0, self.reserved[tenant] - tokens)
        self.usage[tenant].append((time.time(), tokens, True))

    # -----------------------
    # ROLLBACK (ON FAILURE)
    # -----------------------
    def rollback(self, tenant: str, tokens: int):
        self.reserved[tenant] = max(0, self.reserved[tenant] - tokens)

    # -----------------------
    # ADMIN: SET LIMIT
    # -----------------------
    def set_limit(self, tenant: str, limit: int):
        self.limits[tenant] = limit