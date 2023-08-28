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


class StatsType(Enum):
    TOP_TRANSFERS = "TOP_TRANSFERS"
    RECENT_TRANSFERS = "RECENT_TRANSFERS"
    TRANSFER_RELATIONSHIP = "TRANSFER_RELATIONSHIP"
    TRANSFER_DIRECTION = "TRANSFER_DIRECTION"
    TOTAL_TRANSFERS = "TOTAL_TRANSFERS"
    TRANSFER_SUCCESS_RATE = "TRANSFER_SUCCESS_RATE"
    RECENT_REWARDS = "RECENT_REWARDS"
    REWARD_HISTORY = "REWARD_HISTORY"
    TOTAL_REWARDS = "TOTAL_REWARDS"
    BALANCE_HISTORY = "BALANCE_HISTORY"


class Stats:
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
        stats_type: StatsType,
        data,
    ):
        self.cache[public_key][stats_type] = data

    def _check_cache(
        self,
        public_key,
        stats_type: StatsType,
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

    def top_transfers(
        self,
        public_key,
    ):
        return self._transfers(
            public_key,
            StatsType.TOP_TRANSFERS,
        )

    def transfer_direction(
        self,
        public_key,
    ):
        return self._transfers(
            public_key,
            StatsType.TRANSFER_DIRECTION,
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
        if not self._check_cache(
            public_key,
            stats_type,
        ):
            all_transfers = []
            transfer_limit = 1000
            max_fetch = 3

            # Fetch total count
            total_count_query = """
                query ($public_key: String!) {
                transfersConnection(first: 0, orderBy: id_ASC, where: {account: {id_eq: $public_key}}) {
                    totalCount
                }
            }
            """
            total_count_result = self.subsquid_actor.subscan_main_graphql(
                total_count_query,
                {"public_key": public_key},
            )
            total_count = (
                total_count_result.get(
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

            # Saving the top 5 senders and receivers to the cache
            self._save_to_cache(
                public_key,
                StatsType.TOTAL_TRANSFERS,
                total_count,
            )

            # Calculate starting offset
            transfer_offset = max(
                0,
                total_count - (max_fetch * transfer_limit),
            )

            pages_fetched = 0
            while pages_fetched < max_fetch:
                variables = {
                    "public_key": public_key,
                    "account_limit": 1,
                    "account_offset": 0,
                    "transfer_limit": transfer_limit,
                    "transfer_offset": transfer_offset,
                }

                query = """
                    query ($public_key: String!, $account_limit:Int!, $account_offset:Int!, $transfer_limit:Int!, $transfer_offset:Int!) {
                    accounts(where: {id_eq: $public_key}, limit: $account_limit, offset: $account_offset) {
                        transfers(limit: $transfer_limit, offset: $transfer_offset) {
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
                    }
                """

                result = self.subsquid_actor.subscan_main_graphql(
                    query,
                    variables,
                )
                account_info = result.get(
                    "data",
                    {},
                ).get(
                    "accounts",
                    [None],
                )[0]
                if account_info is not None:
                    transfers = account_info.get(
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
                latest_10_transfers = all_transfers[:10]

            # Saving the latest 10 transfers to the cache
            self._save_to_cache(
                public_key,
                StatsType.RECENT_TRANSFERS,
                latest_10_transfers,
            )

            # -----------------------------------------------------------

            # Extract sender and receiver data
            senders = [
                transfer["transfer"]["from"]["publicKey"]
                for transfer in all_transfers
                if transfer["direction"] == "From"
            ]
            receivers = [
                transfer["transfer"]["to"]["publicKey"] for transfer in all_transfers if transfer["direction"] == "To"
            ]

            # Count occurrences
            sender_counts = Counter(senders)
            receiver_counts = Counter(receivers)

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

            # Saving the top 5 senders and receivers to the cache
            self._save_to_cache(
                public_key,
                StatsType.TOP_TRANSFERS,
                {
                    "senders": top_5_senders_by_count,
                    "receivers": top_5_receivers_by_count,
                },
            )

            # -----------------------------------------------------------
            # Dictionaries to hold total amount for each sender and receiver
            sender_amounts = defaultdict(int)
            receiver_amounts = defaultdict(int)

            for transfer in all_transfers:
                if transfer["direction"] == "To":
                    receiver = transfer["transfer"]["to"]["publicKey"]
                    receiver_amounts[receiver] += int(transfer["transfer"]["amount"])

                elif transfer["direction"] == "From":
                    sender = transfer["transfer"]["from"]["publicKey"]
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

            # -----------------------------------------------------------

            success_count = sum(1 for transfer in all_transfers if transfer["transfer"]["success"])
            failed_count = len(all_transfers) - success_count
            success_rate = success_count / len(all_transfers) * 100 if all_transfers else 0  # handle division by zero

            # Saving the transfer success rate to the cache
            transfer_success_rate = {
                "success_count": success_count,
                "failed_count": failed_count,
                "success_rate": success_rate,
            }
            self._save_to_cache(
                public_key,
                StatsType.TRANSFER_SUCCESS_RATE,
                transfer_success_rate,
            )

            # -----------------------------------------------------------

            # Create lists to hold the data for the chart
            timestamps = []
            incoming_counts = []
            outgoing_counts = []

            # Create a Counter for incoming and outgoing transfers
            incoming_counter = Counter(
                [transfer["transfer"]["timestamp"] for transfer in all_transfers if transfer["direction"] == "To"]
            )
            outgoing_counter = Counter(
                [transfer["transfer"]["timestamp"] for transfer in all_transfers if transfer["direction"] == "From"]
            )

            # Aggregate data over unique timestamps
            for timestamp in sorted(
                set(incoming_counter) | set(outgoing_counter)
            ):  # Since transfers are already sorted
                timestamps.append(timestamp)
                incoming_counts.append(
                    incoming_counter.get(
                        timestamp,
                        0,
                    )
                )
                outgoing_counts.append(
                    outgoing_counter.get(
                        timestamp,
                        0,
                    )
                )

            # Construct the chart format
            chart_format = {
                "xAxis": {
                    "type": "category",
                    "data": timestamps,
                },
                "yAxis": {"type": "value"},
                "series": [
                    {
                        "name": "Incoming Transfers",
                        "type": "line",
                        "data": incoming_counts,
                    },
                    {
                        "name": "Outgoing Transfers",
                        "type": "line",
                        "data": outgoing_counts,
                    },
                ],
            }

            self._save_to_cache(
                public_key,
                StatsType.TRANSFER_DIRECTION,
                data=chart_format,
            )

        return self.cache[public_key][stats_type]
