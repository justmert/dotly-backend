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
import threading
import tools.log_config as log_config
import os
import logging

current_file_path = os.path.abspath(__file__)
base_dir = os.path.dirname(current_file_path)
logger = logging.getLogger(__name__)


class RewardsType(Enum):
    REWARDS = "REWARDS"
    REWARD_RELATIONSHIP = "REWARD_RELATIONSHIP"
    RECENT_REWARDS = "RECENT_REWARDS"
    REWARD_HISTORY = "REWARD_HISTORY"
    TOTAL_REWARDS = "TOTAL_REWARDS"


class Rewards:
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

    def _save_to_cache(self, public_key, stats_type: RewardsType, data):
        self.cache[public_key][stats_type] = data

    def _check_cache(self, public_key, stats_type: RewardsType):
        if public_key in self.cache and stats_type in self.cache[public_key]:
            return True
        return False

    def total_rewards(
        self,
        public_key,
    ):
        return self._rewards(
            public_key,
            RewardsType.TOTAL_REWARDS,
        )

    def recent_rewards(
        self,
        public_key,
    ):
        all_rewards = self._rewards(
            public_key,
            RewardsType.REWARDS,
        )
        if all_rewards:
            latest_10_rewards = []
            if len(all_rewards) > 10:
                latest_10_rewards = all_rewards[-10:][::-1]

            else:
                latest_10_rewards = all_rewards[::-1]
            return latest_10_rewards

    def rewards(
        self,
        public_key,
    ):
        return self._rewards(
            public_key,
            RewardsType.REWARDS,
        )

    def reward_relationship(
        self,
        public_key,
    ):
        return self._rewards(
            public_key,
            RewardsType.REWARD_RELATIONSHIP,
        )

    def _rewards(
        self,
        public_key,
        stats_type: RewardsType,
    ):
        # Get the lock associated with the public_key
        key_lock = self._get_lock_for_key(public_key)

        with key_lock:
            if not self._check_cache(
                public_key,
                stats_type,
            ):
                all_rewards = []
                reward_limit = 10000
                max_fetch = 3

                # Fetch total count
                total_count_query = """
                    query ($public_key: String!) {
                    stakingRewardsConnection(orderBy: id_ASC, where: {account: {id_eq: $public_key}}) {
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
                        "stakingRewardsConnection",
                        {},
                    )
                    .get(
                        "totalCount",
                        0,
                    )
                )

                if total_count == 0:
                    return self.cache[public_key].get(stats_type,None)

                # Calculate starting offset
                reward_offset = max(
                    0,
                    total_count - (max_fetch * reward_limit),
                )

                pages_fetched = 0
                while pages_fetched < max_fetch:
                    variables = {
                        "public_key": public_key,
                        "reward_limit": reward_limit,
                        "reward_offset": reward_offset,
                    }

                    query = """
                    query ($public_key: String! $reward_limit: Int!, $reward_offset: Int!) {
                    stakingRewards(orderBy:timestamp_DESC limit: $reward_limit, offset: $reward_offset, where: {account: {publicKey_eq: $public_key}})
                    {
                        id
                        timestamp
                        amount
                        validatorId
                        era

                    }
                    }
                    """

                    result = self.subsquid_actor.subscan_main_graphql(
                        query,
                        variables,
                    )
                    rewards = result.get("data", {}).get(
                        "stakingRewards",
                        [],
                    )
                    if not rewards:
                        break

                    all_rewards.extend(rewards)

                    pages_fetched += 1
                    reward_offset += reward_limit

                    all_rewards = [
                        {
                            "amount": dot_string_to_float(reward["amount"]),
                            **{k: v for k, v in reward.items() if k != "amount"},
                        }
                        for reward in all_rewards
                    ]

                self._save_to_cache(
                    public_key,
                    RewardsType.REWARDS,
                    all_rewards,
                )

                self._save_to_cache(
                    public_key,
                    RewardsType.TOTAL_REWARDS,
                    {"total_amount": sum([reward["amount"] for reward in all_rewards]), "total_count": total_count},
                )
                # -----------------------------------------------------------

                validators = [reward["validatorId"] for reward in all_rewards]

                # Count occurrences
                validator_counts = Counter(validators)

                top_5_validators_by_count = [
                    {
                        "validator_id": public_id,
                        "count": count,
                    }
                    for public_id, count in validator_counts.most_common(10)
                ]

                # -----------------------------------------------------------
                # Dictionaries to hold total amount for each sender and receiver
                validator_amount = defaultdict(float)

                for reward in all_rewards:
                    validator_id = reward["validatorId"]
                    validator_amount[validator_id] += reward["amount"]

                # Sort and extract top 5 senders and receivers by amount
                top_5_rewards_by_amount = sorted(
                    validator_amount.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )[:5]

                # Convert to desired format
                top_5_validators_by_amount = [
                    {
                        "validator_id": validator_id,
                        "amount": amount,
                    }
                    for validator_id, amount in top_5_rewards_by_amount
                ]

                self._save_to_cache(
                    public_key,
                    RewardsType.REWARD_RELATIONSHIP,
                    data={"count": top_5_validators_by_count, "amount": top_5_validators_by_amount},
                )

            return self.cache[public_key].get(stats_type,None)
