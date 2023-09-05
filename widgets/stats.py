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
import threading
import tools.log_config as log_config
import os
import logging

current_file_path = os.path.abspath(__file__)
base_dir = os.path.dirname(current_file_path)
logger = logging.getLogger(__name__)


class StatsType(Enum):
    # TOP_TRANSFERS_BY_COUNT = "TOP_TRANSFERS_BY_COUNT"
    RECENT_TRANSFERS = "RECENT_TRANSFERS"
    TRANSFER_RELATIONSHIP = "TRANSFER_RELATIONSHIP"
    TRANSFER_HISTORY = "TRANSFER_HISTORY"
    TOTAL_TRANSFERS = "TOTAL_TRANSFERS"
    # TRANSFER_SUCCESS_RATE = "TRANSFER_SUCCESS_RATE"


class Stats:
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

    def _save_to_cache(self, public_key, stats_type: StatsType, data):
        self.cache[public_key][stats_type] = data

    def _check_cache(self, public_key, stats_type: StatsType):
        if public_key in self.cache and stats_type in self.cache[public_key]:
            return True
        return False

    def transfer_relationship(
        self,
        public_key,
    ):
        return self._transfers(
            public_key,
            StatsType.TRANSFER_RELATIONSHIP,
        )

    def recent_transfers(
        self,
        public_key,
    ):
        return self._transfers(
            public_key,
            StatsType.RECENT_TRANSFERS,
        )

    def transfer_history(
        self,
        public_key,
    ):
        return self._transfers(
            public_key,
            StatsType.TRANSFER_HISTORY,
        )

    def total_transfers(
        self,
        public_key,
    ):
        return self._transfers(
            public_key,
            StatsType.TOTAL_TRANSFERS,
        )

    def _transfers(
        self,
        public_key,
        stats_type: StatsType,
    ):
        # Get the lock associated with the public_key
        key_lock = self._get_lock_for_key(public_key)

        with key_lock:
            if not self._check_cache(
                public_key,
                stats_type,
            ):
                all_transfers = []
                transfer_limit = 50000
                max_fetch = 3

                # Fetch total count
                total_to_count_query = """
                    query ($public_key: String!) {
                        transfersConnection(orderBy: id_ASC, where: {account: {id_eq: $public_key}, direction_eq: To}) {
                            totalCount
                        }
                    }            
                """
                total_to_count_result = self.subsquid_actor.subscan_main_graphql(
                    total_to_count_query,
                    {"public_key": public_key},
                )
                total_to_count = (
                    total_to_count_result.get(
                        "data",
                        {},
                    )
                    .get(
                        "transfersConnection",
                        {},
                    )
                    .get(
                        "totalCount",
                        0,
                    )
                )
                total_from_count_query = """
                    query ($public_key: String!) {
                        transfersConnection(orderBy: id_ASC, where: {account: {id_eq: $public_key}, direction_eq: From}) {
                            totalCount
                        }
                    }            
                """
                total_from_count_result = self.subsquid_actor.subscan_main_graphql(
                    total_from_count_query,
                    {"public_key": public_key},
                )
                total_from_count = (
                    total_from_count_result.get(
                        "data",
                        {},
                    )
                    .get(
                        "transfersConnection",
                        {},
                    )
                    .get(
                        "totalCount",
                        0,
                    )
                )

                total_count = total_to_count + total_from_count

                # Saving the top 5 senders and receivers to the cache
                self._save_to_cache(
                    public_key,
                    StatsType.TOTAL_TRANSFERS,
                    {
                        "total_count": total_count,
                        "received": total_to_count,
                        "sent": total_from_count,
                    },
                )
                if total_count == 0:
                    return self.cache[public_key][stats_type]


                # Calculate starting offset
                transfer_offset = max(
                    0,
                    total_count - (max_fetch * transfer_limit),
                )
                pages_fetched = 0
                while pages_fetched < max_fetch:
                    variables = {
                        "public_key": public_key,
                        "transfer_limit": transfer_limit,
                        "transfer_offset": transfer_offset,
                    }

                    query = """
                        query ($public_key: String!, $transfer_limit:Int!, $transfer_offset:Int!) {
                            transfers(limit: $transfer_limit, offset: $transfer_offset, where: {account: {publicKey_eq: $public_key}}) {
                            id
                            transfer {
                                blockNumber
                                timestamp
                                extrinsicHash
                                from {
                                    publicKey
                                }
                                amount
                                success
                                to {
                                    publicKey
                                }
                            }
                            direction
                            }
                        }
                    """

                    result = self.subsquid_actor.subscan_main_graphql(
                        query,
                        variables,
                    )
                    transfers = result.get("data", {}).get(
                        "transfers",
                        [],
                    )
                    if not transfers:
                        break

                    all_transfers.extend(transfers)

                    pages_fetched += 1
                    transfer_offset += transfer_limit
                
                # Extracting the latest 10 transfers
                latest_10_transfers = []
                if len(all_transfers) > 10:
                    latest_10_transfers = all_transfers[-10:][::-1]
                else:
                    latest_10_transfers = all_transfers[::-1]

                # Saving the latest 10 transfers to the cache
                self._save_to_cache(
                    public_key,
                    StatsType.RECENT_TRANSFERS,
                    latest_10_transfers,
                )

                # -----------------------------------------------------------

                # Extract sender and receiver data
                # me receives
                all_senders = [
                    transfer["transfer"]["from"]["publicKey"]
                    for transfer in all_transfers
                    if transfer["direction"] == "To"
                ]

                # me sent
                all_receivers = [
                    transfer["transfer"]["to"]["publicKey"]
                    for transfer in all_transfers
                    if transfer["direction"] == "From"
                ]

                # Count occurrences
                sender_counts = Counter(all_senders)
                receiver_counts = Counter(all_receivers)

                # Extract top 5 senders and receivers
                top_5_senders_by_count = [
                    {
                        "public_id": public_id,
                        "count": count,
                    }
                    for public_id, count in sender_counts.most_common(10)
                ]
                top_5_receivers_by_count = [
                    {
                        "public_id": public_id,
                        "count": count,
                    }
                    for public_id, count in receiver_counts.most_common(10)
                ]

                # -----------------------------------------------------------
                # Dictionaries to hold total amount for each sender and receiver
                sender_amounts = defaultdict(int)
                receiver_amounts = defaultdict(int)

                for transfer in all_transfers:
                    if transfer["direction"] == "To":
                        receiver = transfer["transfer"]["from"]["publicKey"]
                        receiver_amounts[receiver] += int(transfer["transfer"]["amount"])

                    elif transfer["direction"] == "From":
                        sender = transfer["transfer"]["to"]["publicKey"]
                        sender_amounts[sender] += int(transfer["transfer"]["amount"])

                # Sort and extract top 5 senders and receivers by amount
                top_5_senders_by_amount = sorted(
                    sender_amounts.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )[:5]
                top_5_receivers_by_amount = sorted(
                    receiver_amounts.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )[:5]

                # Convert to desired format
                top_5_senders_by_amount = [
                    {
                        "public_id": public_id,
                        "amount": amount,
                    }
                    for public_id, amount in top_5_senders_by_amount
                ]
                top_5_receivers_by_amount = [
                    {
                        "public_id": public_id,
                        "amount": amount,
                    }
                    for public_id, amount in top_5_receivers_by_amount
                ]

                self._save_to_cache(
                    public_key,
                    StatsType.TRANSFER_RELATIONSHIP,
                    data={
                        "count": {
                            "senders": top_5_senders_by_count,
                            "receivers": top_5_receivers_by_count,
                        },
                        "amount": {
                            "senders": top_5_senders_by_amount,
                            "receivers": top_5_receivers_by_amount,
                        },
                    },
                )

                # Convert the timestamps into 'YYYY-MM-DD' format and then count occurrences for incoming and outgoing transfers
                all_transfers_df = pd.DataFrame(all_transfers)

                # Extract timestamp from the nested 'transfer' dictionary and then convert to date format
                all_transfers_df["transfer_date"] = all_transfers_df["transfer"].apply(lambda x: x["timestamp"])
                all_transfers_df["transfer_date"] = pd.to_datetime(all_transfers_df["transfer_date"]).dt.date

                incoming_df = all_transfers_df[all_transfers_df["direction"] == "To"].groupby("transfer_date").size()
                outgoing_df = all_transfers_df[all_transfers_df["direction"] == "From"].groupby("transfer_date").size()

                # Create a date range spanning the entire period from the earliest transfer to today
                full_date_range = pd.date_range(start=min(all_transfers_df["transfer_date"]), end=date.today()).date

                # Reindex the dataframes to this range, filling in missing dates with zero
                incoming_df = incoming_df.reindex(full_date_range, fill_value=0)
                outgoing_df = outgoing_df.reindex(full_date_range, fill_value=0)

                self._save_to_cache(
                    public_key,
                    StatsType.TRANSFER_HISTORY,
                    data={
                        "timestamps": incoming_df.index,  # DatetimeIndex directly
                        "incoming_counts": incoming_df,  # Series directly
                        "outgoing_counts": outgoing_df,  # Series directly
                    },
                )

            return self.cache[public_key].get(stats_type,None)
