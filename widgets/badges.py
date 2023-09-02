from actors.subsquid_actor import (
    SubSquidActor,
)
from actors.subscan_actor import (
    SubscanActor,
)
from enum import (
    Enum,
)
from collections import (
    deque,
)
from collections import (
    Counter,
)
from collections import (
    defaultdict,
)
from datetime import (
    datetime,
    timedelta,
)
from dateutil.relativedelta import (
    relativedelta,
)
from tools.helpers import dot_string_to_float
import pandas as pd
from datetime import date
from api.api import STATS_CONTEXT, StatsType
from api.api import OVERVIEW_CONTEXT, OverviewType
from api.api import REWARDS_CONTEXT, RewardsType
from api.api import EXTRINSICS_CONTEXT, ExtrinsicsType


class BadgesType(Enum):
    CHECK_BADGES = "CHECK_BADGES"


class Badges:
    def __init__(
        self,
    ):
        self.subscan_actor = SubscanActor()
        self.subsquid_actor = SubSquidActor()
        self.cache_limit = 10
        self.cache = {}
        self.queue = deque(maxlen=100)

    def _save_to_cache(
        self,
        public_key,
        stats_type: BadgesType,
        data,
    ):
        self.cache[public_key][stats_type] = data

    def _check_cache(
        self,
        public_key,
        stats_type: BadgesType,
    ):
        if public_key in self.cache:
            if stats_type in self.cache[public_key]:
                return True
            else:
                return False

        self.cache[public_key] = {}
        popped_value = None

        if len(self.queue) == self.queue.maxlen:
            popped_value = self.queue.popleft()  # Remove the oldest value and get it

        if popped_value is not None:
            del self.cache[popped_value]

        self.queue.append(public_key)
        return False

    def _check_join_party_badge(self, public_key):
        total_transfers = STATS_CONTEXT.total_transfers(public_key)
        if total_transfers["sent"] > 0:
            return True
        else:
            return False

    def _check_is_this_gift_for_me(self, public_key):
        total_transfers = STATS_CONTEXT.total_transfers(public_key)
        if total_transfers["received"] > 0:
            return True
        else:
            return False

    def check_badges(self, public_key):
        badges = [
            {
                "name": "Join the party!",
                "description": "Sent a token.",
                "success": False,
                "function": self._check_join_party_badge,
                "args": {
                    "public_key": public_key,
                },
            },
            {
                "name": "Is this gift for me?",
                "description": "Receive a token.",
                "success": False,
                "function": self._check_is_this_gift_for_me,
                "args": {
                    "public_key": public_key,
                },
            },
        ]

        for badge in badges:
            badge["success"] = badge["function"](**badge["args"])

        # return without args and function
        return [
            {
                "name": badge["name"],
                "description": badge["description"],
                "success": badge["success"],
            }
            for badge in badges
        ]
