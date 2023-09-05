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
import threading
import tools.log_config as log_config
import os
import logging

current_file_path = os.path.abspath(__file__)
base_dir = os.path.dirname(current_file_path)
logger = logging.getLogger(__name__)


class OverviewType(Enum):
    ACCOUNT = "ACCOUNT"
    MULTI_CHAIN_IDENTITY = "MULTI_CHAIN_IDENTITY"
    BALANCE_HISTORY = "BALANCE_HISTORY"
    BALANCE_STATS = "BALANCE_STATS"
    BALANCE_DISTRIBUTION = "BALANCE_DISTRIBUTION"
    TRANSACTION_RATE = "TRANSACTION_RATE"


class Overview:
    def __init__(self):
        self.subscan_actor = SubscanActor()
        self.subsquid_actor = SubSquidActor()
        self.cache_limit = 10
        self.cache = {}
        # queue now stores tuples of (public_key, lock)
        self.locks_dict = {}
        self.queue = deque(maxlen=100)  # This will only store public_keys now

    def _get_lock_for_key(self, key):
        if key not in self.locks_dict:
            self.locks_dict[key] = threading.Lock()

            # If the queue is full, pop the oldest key and delete its lock
            if len(self.queue) == self.queue.maxlen:
                oldest_key = self.queue.popleft()
                del self.locks_dict[oldest_key]

            self.queue.append(key)

            # If a new key is being added, ensure its presence in the cache
            if key not in self.cache:
                self.cache[key] = {}

        return self.locks_dict[key]

    def _save_to_cache(self, public_key, stats_type: OverviewType, data):
        key_lock = self._get_lock_for_key(public_key)
        with key_lock:
            self.cache[public_key][stats_type] = data

    def _check_cache(self, public_key, stats_type: OverviewType):
        key_lock = self._get_lock_for_key(public_key)
        with key_lock:
            return public_key in self.cache and stats_type in self.cache[public_key]

    def account(self, public_key, address):
        if not self._check_cache(
            public_key,
            OverviewType.ACCOUNT,
        ):
            request_data = {"key": address}
            account = self.subscan_actor.subscan_rest_make_request("v2/scan/search", data=request_data)

            if account is None or not account.get("data", None):
                return None

            self._save_to_cache(
                public_key,
                OverviewType.ACCOUNT,
                account["data"]["account"],
            )
        return self.cache[public_key].get(OverviewType.ACCOUNT, None)

    def balance_distribution(
        self,
        public_key,
        address,
    ):
        if not self._check_cache(
            public_key,
            OverviewType.BALANCE_DISTRIBUTION,
        ):
            request_data = {"address": address}
            balance_list = self.subscan_actor.subscan_rest_make_request("scan/multiChain/account", data=request_data)

            if balance_list is None or not balance_list.get("data", None):
                return None

            self._save_to_cache(
                public_key,
                OverviewType.BALANCE_DISTRIBUTION,
                balance_list["data"],
            )

        return self.cache[public_key].get(OverviewType.BALANCE_DISTRIBUTION, None)

    def identity(
        self,
        public_key,
        address,
    ):
        if not self._check_cache(
            public_key,
            OverviewType.MULTI_CHAIN_IDENTITY,
        ):
            request_data = {"address": address}
            multi_chain_identity = self.subscan_actor.subscan_rest_make_request(
                "scan/multiChain/identities", data=request_data
            )

            if multi_chain_identity is None or not multi_chain_identity.get("data", None):
                return None

            self._save_to_cache(
                public_key,
                OverviewType.MULTI_CHAIN_IDENTITY,
                multi_chain_identity["data"],
            )

        return self.cache[public_key].get(OverviewType.MULTI_CHAIN_IDENTITY, None)

    def balance_stats(self, public_key, address):
        if not self._check_cache(
            public_key,
            OverviewType.BALANCE_STATS,
        ):
            request_data = {"address": address}
            balance_stats = self.subscan_actor.subscan_rest_make_request(
                "scan/multiChain/balance_value_stat", data=request_data
            )

            if balance_stats is None or not balance_stats.get("data", None):
                return None

            self._save_to_cache(
                public_key,
                OverviewType.BALANCE_STATS,
                balance_stats["data"],
            )

        return self.cache[public_key].get(OverviewType.BALANCE_STATS, None)

    def balance_history(self, public_key, address):
        if not self._check_cache(
            public_key,
            OverviewType.BALANCE_HISTORY,
        ):
            # today's date
            request_data = {
                "address": address,
                "end": datetime.now().strftime("%Y-%m-%d"),
                "start": (datetime.now() - relativedelta(months=12)).strftime("%Y-%m-%d"),
            }
            balance_stats = self.subscan_actor.subscan_rest_make_request(
                "scan/multiChain/balance_value_history", data=request_data
            )

            if balance_stats is None or not balance_stats.get("data", None):
                return None

            self._save_to_cache(
                public_key,
                OverviewType.BALANCE_HISTORY,
                balance_stats["data"],
            )

        return self.cache[public_key].get(OverviewType.BALANCE_HISTORY,None)
