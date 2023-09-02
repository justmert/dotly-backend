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

from substrateinterface import SubstrateInterface, Keypair
from substrateinterface.utils.ss58 import ss58_encode


class OverviewType(Enum):
    ACCOUNT = "ACCOUNT"
    MULTI_CHAIN_IDENTITY = "MULTI_CHAIN_IDENTITY"
    BALANCE_HISTORY = "BALANCE_HISTORY"
    BALANCE_STATS = "BALANCE_STATS"
    BALANCE_DISTRIBUTION = "BALANCE_DISTRIBUTION"
    TRANSACTION_RATE = "TRANSACTION_RATE"


class Overview:
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
        stats_type: OverviewType,
        data,
    ):
        self.cache[public_key][stats_type] = data

    def _check_cache(
        self,
        public_key,
        stats_type: OverviewType,
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

            # --------------------------------------------
        return self.cache[public_key][OverviewType.ACCOUNT]

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

        return self.cache[public_key][OverviewType.BALANCE_DISTRIBUTION]

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

        return self.cache[public_key][OverviewType.MULTI_CHAIN_IDENTITY]

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

        return self.cache[public_key][OverviewType.BALANCE_STATS]

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

        return self.cache[public_key][OverviewType.BALANCE_HISTORY]
