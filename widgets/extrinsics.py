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
import pandas as pd
import threading
from collections import deque
import threading
import tools.log_config as log_config
import os
import logging

current_file_path = os.path.abspath(__file__)
base_dir = os.path.dirname(current_file_path)
logger = logging.getLogger(__name__)


class ExtrinsicsType(Enum):
    EXTRINSICS = "EXTRINSICS"
    DISTRIBUTION = "DISTRIBUTION"
    WEEKLY_TRANSACTION_RATE = "WEEKLY_TRANSACTION_RATE"
    TOTAL_EXTRINSICS = "TOTAL_EXTRINSICS"
    RECENT_EXTRINSICS = "RECENT_EXTRINSICS"


class Extrinsics:
    def __init__(self):
        self.subscan_actor = SubscanActor()
        self.subsquid_actor = SubSquidActor()
        self.cache_limit = 10
        self.cache = {}
        # queue now stores tuples of (public_key, lock)
        self.locks_dict = {}
        self.queue = deque(maxlen=10)  # This will only store public_keys now

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

    def _save_to_cache(self, public_key, stats_type: ExtrinsicsType, data):
        self.cache[public_key][stats_type] = data

    def _check_cache(self, public_key, stats_type: ExtrinsicsType):
        if public_key in self.cache and stats_type in self.cache[public_key]:
            return True
        return False

    def total_extrinsics(
        self,
        public_key,
    ):
        return self._extrinsics(
            public_key,
            ExtrinsicsType.TOTAL_EXTRINSICS,
        )

    def recent_extrinsics(
        self,
        public_key,
    ):
        all_extrinsics = self._extrinsics(
            public_key,
            ExtrinsicsType.EXTRINSICS,
        )

        if all_extrinsics:
            # Extracting the latest 10 transfers
            latest_10_extrinsics = []
            if len(all_extrinsics) > 10:
                latest_10_extrinsics = all_extrinsics[-10:][::-1]
            else:
                latest_10_extrinsics = all_extrinsics[::-1]
            return latest_10_extrinsics

    def weekly_transaction_rate(
        self,
        public_key,
    ):
        return self._extrinsics(
            public_key,
            ExtrinsicsType.WEEKLY_TRANSACTION_RATE,
        )

    def extrinsics(
        self,
        public_key,
    ):
        return self._extrinsics(
            public_key,
            ExtrinsicsType.EXTRINSICS,
        )

    def distribution(
        self,
        public_key,
    ):
        return self._extrinsics(
            public_key,
            ExtrinsicsType.DISTRIBUTION,
        )

    def _extrinsics(
        self,
        public_key,
        stats_type: ExtrinsicsType,
    ):
        # Get the lock associated with the public_key
        key_lock = self._get_lock_for_key(public_key)

        with key_lock:
            if not self._check_cache(
                public_key,
                stats_type,
            ):
                all_extrinsics = []
                extrinsics_limit = 50000
                max_fetch = 3

                # Fetch total count
                total_count_query = """
                        query ($public_key: String!) {
                        extrinsicsConnection(orderBy: id_ASC, where: {signerPublicKey_eq: $public_key}) {
                            totalCount
                        }
                    }
                    """
                total_count_result = self.subsquid_actor.subscan_explorer_graphql(
                    total_count_query,
                    {"public_key": public_key},
                )
                total_count = (
                    total_count_result.get(
                        "data",
                        {},
                    )
                    .get(
                        "extrinsicsConnection",
                        {},
                    )
                    .get(
                        "totalCount",
                        0,
                    )
                )
                
                # Saving the top 5 senders and receivers to the cache
                self._save_to_cache(
                    public_key,
                    ExtrinsicsType.TOTAL_EXTRINSICS,
                    {
                        "total_count": total_count,
                    },
                )

                if total_count == 0:
                    return self.cache[public_key].get(stats_type, None)

                # Calculate starting offset
                extrinsics_offset = max(
                    0,
                    total_count - (max_fetch * extrinsics_limit),
                )

                pages_fetched = 0
                while pages_fetched < max_fetch:
                    variables = {
                        "public_key": public_key,
                        "extrinsics_limit": extrinsics_limit,
                        "extrinsics_offset": extrinsics_offset,
                    }

                    query = """
                            query MyQuery($public_key: String!, $extrinsics_limit: Int!, $extrinsics_offset: Int!) {
                                extrinsics(orderBy:timestamp_ASC, offset: $extrinsics_offset, limit: $extrinsics_limit, where: {signerPublicKey_eq: $public_key}) {
                                    id
                                    success
                                    timestamp
                                    mainCall {
                                    callName
                                    palletName
                                    }
                                }
                                }
                        """

                    result = self.subsquid_actor.subscan_explorer_graphql(
                        query,
                        variables,
                    )
                    extrinsics = result.get("data", {}).get(
                        "extrinsics",
                        [],
                    )
                    if not extrinsics:
                        break

                    all_extrinsics.extend(extrinsics)

                    pages_fetched += 1
                    extrinsics_offset += extrinsics_limit


                self._save_to_cache(
                    public_key,
                    ExtrinsicsType.EXTRINSICS,
                    all_extrinsics,
                )

                # ----------------------------

                # Convert data to a dataframe
                df = pd.DataFrame(all_extrinsics)

                # Convert timestamp to datetime type
                df["timestamp"] = pd.to_datetime(df["timestamp"])

                # Keep only the year, month, and day
                df["timestamp"] = pd.to_datetime(df["timestamp"].dt.strftime("%Y-%m-%d"))

                # Get the current timestamp
                now = datetime.now()

                # Filter for the transactions within the last week
                one_week_ago = now - timedelta(days=120)
                last_week_transactions = df[df["timestamp"] > one_week_ago]

                # Get the transaction count for the last week
                last_week_transaction_count = len(last_week_transactions)

                self._save_to_cache(
                    public_key,
                    ExtrinsicsType.WEEKLY_TRANSACTION_RATE,
                    {
                        "last_week_transaction_count": last_week_transaction_count,
                    },
                )

                pallet_call_data = {}
                for entry in all_extrinsics:
                    pallet = entry["mainCall"]["palletName"]
                    call = entry["mainCall"]["callName"]

                    if pallet not in pallet_call_data:
                        pallet_call_data[pallet] = {
                            "total": 0,
                            "callNames": {},
                        }

                    pallet_call_data[pallet]["total"] += 1

                    if call not in pallet_call_data[pallet]["callNames"]:
                        pallet_call_data[pallet]["callNames"][call] = 0

                    pallet_call_data[pallet]["callNames"][call] += 1

                # Getting the top interacted pallets with counts
                top_pallets = sorted(
                    pallet_call_data.items(),
                    key=lambda x: x[1]["total"],
                    reverse=True,
                )
                top_pallets_counts = {pallet[0]: pallet[1]["total"] for pallet in top_pallets}

                # Getting the top calls for each pallet
                top_calls_counts = {}
                for (
                    pallet,
                    details,
                ) in top_pallets:
                    calls = details["callNames"]
                    sorted_calls = sorted(
                        calls.items(),
                        key=lambda x: x[1],
                        reverse=True,
                    )
                    top_calls_counts[pallet] = dict(sorted_calls)

                top_interacted = {
                    "pallets": top_pallets_counts,
                    "calls": top_calls_counts,
                }

                self._save_to_cache(
                    public_key,
                    ExtrinsicsType.DISTRIBUTION,
                    top_interacted,
                )

            return self.cache[public_key].get(stats_type, None)

