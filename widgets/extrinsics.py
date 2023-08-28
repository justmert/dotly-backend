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


class ExtrinsicsType(Enum):
    EXTRINSICS = "EXTRINSICS"
    DISTRIBUTION = "DISTRIBUTION"
    TOP_INTERACTED = "TOP_INTERACTED"


class Extrinsics:
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
        stats_type: ExtrinsicsType,
        data,
    ):
        self.cache[public_key][stats_type] = data

    def _check_cache(
        self,
        public_key,
        stats_type: ExtrinsicsType,
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

    def total_transfers(
        self,
        public_key,
    ):
        return self._transfers(
            public_key,
            ExtrinsicsType.TOTAL_TRANSFERS,
        )

    def _extrinsics(
        self,
        public_key,
        stats_type: ExtrinsicsType,
    ):
        if not self._check_cache(
            public_key,
            stats_type,
        ):
            extrinsics_limit = 1000

            extrinsics_query = """
            query MyQuery($public_key: String!, $extrinsics_limit: Int!) {
                extrinsics(limit: $extrinsics_limit, where: {signerPublicKey_eq: $public_key}) {
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

            data = (
                self.subsquid_actor.subscan_explorer_graphql(
                    extrinsics_query,
                    {
                        "public_key": public_key,
                        "extrinsics_limit": extrinsics_limit,
                    },
                )
                .get(
                    "data",
                    {},
                )
                .get(
                    "extrinsics",
                    [],
                )
            )

            self._save_to_cache(
                public_key,
                ExtrinsicsType.EXTRINSICS,
                data,
            )

            pallet_call_data = {}
            for entry in data:
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

            main_pie_data = [
                {
                    "name": pallet,
                    "value": details["total"],
                }
                for pallet, details in pallet_call_data.items()
            ]
            sub_pie_data = {
                pallet: [
                    {
                        "name": call,
                        "value": count,
                    }
                    for call, count in details["callNames"].items()
                ]
                for pallet, details in pallet_call_data.items()
            }

            # Getting the top interacted pallets with counts
            top_pallets = sorted(
                pallet_call_data.items(),
                key=lambda x: x[1]["total"],
                reverse=True,
            )[:5]
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
                )[:5]
                top_calls_counts[pallet] = dict(sorted_calls)

            echarts_data = {
                "mainPie": {
                    "legendData": list(pallet_call_data.keys()),
                    "seriesData": main_pie_data,
                },
                "subPie": sub_pie_data,
            }
            self._save_to_cache(
                public_key,
                ExtrinsicsType.DISTRIBUTION,
                echarts_data,
            )

            top_interacted = {
                "pallets": top_pallets_counts,
                "calls": top_calls_counts,
            }

            self._save_to_cache(
                public_key,
                ExtrinsicsType.TOP_INTERACTED,
                top_interacted,
            )

        return self.cache[public_key][stats_type]

    def transfer_success_rate(
        self,
        public_key,
    ):
        return self._transfers(
            public_key,
            ExtrinsicsType.TRANSFER_SUCCESS_RATE,
        )
