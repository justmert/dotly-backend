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
from api.routers import rewards, stats, overview, extrinsics
from tools.helpers import encode
import tools.log_config as log_config
import os
import logging

current_file_path = os.path.abspath(__file__)
base_dir = os.path.dirname(current_file_path)
logger = logging.getLogger(__name__)


class BadgesType(Enum):
    CHECK_BADGES = "CHECK_BADGES"


class Badges:
    def __init__(
        self,
    ):
        self.subscan_actor = SubscanActor()
        self.subsquid_actor = SubSquidActor()

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

    def _check_call_master_300(self, public_key):
        tatal_extrinsics = EXTRINSICS_CONTEXT.total_extrinsics(public_key)
        if tatal_extrinsics["total_count"] > 300:
            return True
        else:
            return False

    def _check_hat_trick_hero(self, public_key):
        try:
            reward_history = rewards.reward_history(public_key=public_key, interval=rewards.HistoryInterval.MONTH)
        except:
            return False
        consecutive_months = 0
        for reward in reward_history["series"][0]["data"]:
            if reward > 0:
                consecutive_months += 1
                if consecutive_months >= 3:
                    return True
            else:
                consecutive_months = 0
        return False

    def _check_first_dip_in_the_gold(self, public_key):
        total_reward = rewards.total_rewards(public_key=public_key)
        if total_reward.get("total_count", 0) > 0:
            return True
        return False

    def _check_trailblazer(self, public_key):
        interacted_modules = EXTRINSICS_CONTEXT.top_interacted(public_key)
        if interacted_modules:
            number_of_modules_interacted_with = len(interacted_modules.get("pallets", []))
            if number_of_modules_interacted_with >= 5:
                return True
        return False

    def _check_multiverse_traveler(self, public_key, address):
        balances = OVERVIEW_CONTEXT.balance_distribution(public_key, address)
        if balances:
            networks_with_balance = [entry["network"] for entry in balances if float(entry["balance"]) > 0]

            if len(networks_with_balance) > 1:
                return True
        return False

    def _check_locked_and_loaded(self, public_key, address):
        balances = OVERVIEW_CONTEXT.balance_distribution(public_key, address)
        if balances:
            for entry in balances:
                if float(entry.get("locked", 0)) > 0:
                    return True
        return False

    def _check_democracy_defender(self, public_key, address):
        balances = OVERVIEW_CONTEXT.balance_distribution(public_key, address)
        if balances:
            for entry in balances:
                if float(entry.get("democracy_lock", 0)) > 0:
                    return True
        return False

    def _check_reliable_rainmaker(self, public_key, address):
        try:
            data = OVERVIEW_CONTEXT.balance_history(public_key, address)
        except:
            return False
        last_three_months_data = self._filter_last_three_months(data)

        for i in range(1, len(last_three_months_data)):
            if float(last_three_months_data[i]["value"]) <= float(last_three_months_data[i - 1]["value"]):
                return False
        return True

    def _check_equilibrium_expert(self, public_key, address):
        try:
            data = OVERVIEW_CONTEXT.balance_history(public_key, address)
        except:
            return False

        last_three_months_data = self._filter_last_three_months(data)

        min_balance = float("inf")
        max_balance = float("-inf")

        for entry in last_three_months_data:
            balance = float(entry["value"])
            min_balance = min(min_balance, balance)
            max_balance = max(max_balance, balance)

        return max_balance <= 1.1 * min_balance

    def _filter_last_three_months(self, data):
        today = datetime.date.today()
        three_months_ago = today - datetime.timedelta(days=90)
        return [entry for entry in data if datetime.date.fromisoformat(entry["date"]) >= three_months_ago]

    def _check_nomination_knight(self, public_key, address):
        balances = OVERVIEW_CONTEXT.balance_distribution(public_key, address)
        if balances:
            for entry in balances:
                if float(entry.get("nomination_bonded", 0)) > 0:
                    return True
        return False

    def _safe_get_identity(self, public_key, address):
        try:
            identities = OVERVIEW_CONTEXT.identity(public_key, address)
            if not identities:
                return []
            return identities
        except:
            return []

    def _check_identity_pioneer(self, public_key, address):
        identities = self._safe_get_identity(public_key, address)
        for entry in identities:
            if entry.get("identity"):
                return True
        return False

    def _check_webmaster(self, public_key, address):
        identities = self._safe_get_identity(public_key, address)
        for entry in identities:
            if entry.get("web"):
                return True
        return False

    def _check_tweetheart(self, public_key, address):
        identities = self._safe_get_identity(public_key, address)
        for entry in identities:
            if entry.get("twitter"):
                return True
        return False

    def _check_judgement_joker(self, public_key, address):
        identities = self._safe_get_identity(public_key, address)
        for entry in identities:
            if entry.get("judgements"):
                return True
        return False

    def _safe_get_total_transfers(self, public_key):
        try:
            return STATS_CONTEXT.total_transfers(public_key)
        except:
            return None

    def _check_chatterbox_chieftain(self, public_key):
        data = self._safe_get_total_transfers(public_key)
        if data and data.get("sent", 0) > 50:
            return True
        return False

    def _safe_get_extrinsics_activity(self, public_key, interval):
        try:
            return extrinsics.extrinsics_activity(public_key, interval)
        except:
            return None

    def _check_consistent_conductor(self, public_key):
        data = self._safe_get_extrinsics_activity(public_key, extrinsics.ActivityInterval.MONTH)
        if not data:
            return False
        activity_data = data.get("series", [{}])[0].get("data", [])

        for i in range(len(activity_data) - 2):
            if activity_data[i] > 0 and activity_data[i + 1] > 0 and activity_data[i + 2] > 0:
                return True
        return False

    def _check_consistent_creator(self, public_key):
        THRESHOLD = 5
        data = self._safe_get_extrinsics_activity(public_key, extrinsics.ActivityInterval.MONTH)
        if not data:
            return False
        last_three_months = data.get("series", [{}])[0].get("data", [])[-3:]

        if all(value >= THRESHOLD for value in last_three_months):
            return True
        return False

    def _safe_get_data(self, func, public_key, key):
        try:
            data = func(public_key)
        except:
            return None
        return data.get(key, None)

    def _check_magnet_mogul(self, public_key):
        data_received = self._safe_get_data(STATS_CONTEXT.total_transfers, public_key, "received")
        return data_received is not None and data_received > 100

    def _check_transfer_titan(self, public_key):
        data = self._safe_get_data(STATS_CONTEXT.total_transfers, public_key, None)
        total_transactions = (data.get("received", 0) if data else 0) + (data.get("sent", 0) if data else 0)
        return total_transactions > 150

    def _check_extrinsics_explorer(self, public_key):
        total_count = self._safe_get_data(EXTRINSICS_CONTEXT.total_extrinsics, public_key, "total_count")
        return total_count is not None and total_count > 10

    def _check_extrinsics_enthusiast(self, public_key):
        total_count = self._safe_get_data(EXTRINSICS_CONTEXT.total_extrinsics, public_key, "total_count")
        return total_count is not None and total_count > 50

    def _check_extrinsics_expert(self, public_key):
        total_count = self._safe_get_data(EXTRINSICS_CONTEXT.total_extrinsics, public_key, "total_count")
        return total_count is not None and total_count > 100

    def _check_extrinsics_emperor(self, public_key):
        total_count = self._safe_get_data(EXTRINSICS_CONTEXT.total_extrinsics, public_key, "total_count")
        return total_count is not None and total_count > 200

    def _check_golden_gatherer(self, public_key):
        total_count = self._safe_get_data(REWARDS_CONTEXT.total_rewards, public_key, "total_count")
        return total_count is not None and total_count > 100

    def _check_thousand_thrills(self, public_key):
        total_count = self._safe_get_data(REWARDS_CONTEXT.total_rewards, public_key, "total_count")
        return total_count is not None and total_count > 1000

    def _check_elite_earner(self, public_key):
        total_amount = self._safe_get_data(REWARDS_CONTEXT.total_rewards, public_key, "total_amount")
        return total_amount is not None and total_amount > 10000

    def _check_one_tap_wonder(self, public_key):
        total_count = self._safe_get_data(EXTRINSICS_CONTEXT.total_extrinsics, public_key, "total_count")
        return total_count is not None and total_count > 0

    def _check_lavish_legend(self, public_key):
        total_amount = self._safe_get_data(REWARDS_CONTEXT.total_rewards, public_key, "total_amount")
        return total_amount is not None and total_amount > 1000

    def check_badges(self, public_key):
        address = encode(public_key)

        badges = [
            {
                "name": "Join the party!",
                "description": "Sent a token transfer.",
                "success": False,
                "function": self._check_join_party_badge,
                "args": {
                    "public_key": public_key,
                },
            },
            {
                "name": "Is this gift for me?",
                "description": "Receive a token transfer.",
                "success": False,
                "function": self._check_is_this_gift_for_me,
                "args": {
                    "public_key": public_key,
                },
            },
            {
                "name": "First Dip in the Gold!",
                "description": "Received your first reward.",
                "success": False,
                "function": self._check_first_dip_in_the_gold,
                "args": {
                    "public_key": public_key,
                },
            },
            {
                "name": "Call Master 300!",
                "description": "More than 300 extrinsic calls made.",
                "success": False,
                "function": self._check_call_master_300,
                "args": {
                    "public_key": public_key,
                },
            },
            {
                "name": "Hat Trick Hero!",
                "description": "Received rewards for 3 consecutive months.",
                "success": False,
                "function": self._check_hat_trick_hero,
                "args": {
                    "public_key": public_key,
                },
            },
            {
                "name": "Trailblazer!",
                "description": "Interacted with 5 or more different extrinsic modules.",
                "success": False,
                "function": self._check_trailblazer,
                "args": {
                    "public_key": public_key,
                },
            },
            {
                "name": "Golden Gatherer",
                "description": "Collected over 100 rewards. Keep it up!",
                "success": False,
                "function": self._check_golden_gatherer,
                "args": {
                    "public_key": public_key,
                },
            },
            {
                "name": "Thousand Thrills",
                "description": "A thrill for every reward, and you've hit 1000 of them!",
                "success": False,
                "function": self._check_thousand_thrills,
                "args": {
                    "public_key": public_key,
                },
            },
            {
                "name": "Elite Earner",
                "description": "You've accumulated over 10,000 in rewards. Elite status achieved!",
                "success": False,
                "function": self._check_elite_earner,
                "args": {
                    "public_key": public_key,
                },
            },
            {
                "name": "Lavish Legend",
                "description": "You've accumulated over 1,000 in rewards. Truly legendary!",
                "success": False,
                "function": self._check_lavish_legend,
                "args": {
                    "public_key": public_key,
                },
            },
            {
                "name": "Multiverse Traveler",
                "description": "Have balances in more than one network.",
                "success": False,
                "function": self._check_multiverse_traveler,
                "args": {
                    "public_key": public_key,
                    "address": address,
                },
            },
            {
                "name": "Locked & Loaded",
                "description": "Have locked funds in any network.",
                "success": False,
                "function": self._check_locked_and_loaded,
                "args": {
                    "public_key": public_key,
                    "address": address,
                },
            },
            {
                "name": "Democracy Defender",
                "description": "Have funds locked in democratic processes.",
                "success": False,
                "function": self._check_democracy_defender,
                "args": {
                    "public_key": public_key,
                    "address": address,
                },
            },
            {
                "name": "Nomination Knight",
                "description": "Have nomination bonded funds in any network.",
                "success": False,
                "function": self._check_nomination_knight,
                "args": {
                    "public_key": public_key,
                    "address": address,
                },
            },
            {
                "name": "Identity Pioneer",
                "description": "Established an identity on any network.",
                "success": False,
                "function": self._check_identity_pioneer,
                "args": {
                    "public_key": public_key,
                    "address": address,
                },
            },
            {
                "name": "Webmaster",
                "description": "Provided a website in the identity details.",
                "success": False,
                "function": self._check_webmaster,
                "args": {"public_key": public_key, "address": address},
            },
            {
                "name": "TweetHeart",
                "description": "Linked a Twitter handle in identity details.",
                "success": False,
                "function": self._check_tweetheart,
                "args": {
                    "public_key": public_key,
                    "address": address,
                },
            },
            {
                "name": "Judgement Joker",
                "description": "Received at least one judgement.",
                "success": False,
                "function": self._check_judgement_joker,
                "args": {
                    "public_key": public_key,
                    "address": address,
                },
            },
            {
                "name": "Consistent Growth",
                "description": "Your balance has grown consistently over the past three months.",
                "success": False,
                "function": self._check_reliable_rainmaker,
                "args": {
                    "public_key": public_key,
                    "address": address,
                },
            },
            {
                "name": "Magnet Mogul",
                "description": "Receive a total of more than 100 transactions.",
                "success": False,
                "function": self._check_magnet_mogul,
                "args": {
                    "public_key": public_key,
                },
            },
            {
                "name": "Equilibrium Expert",
                "description": "You've maintained your balance within a 10% range over the past three months.",
                "success": False,
                "function": self._check_equilibrium_expert,
                "args": {
                    "public_key": public_key,
                    "address": address,
                },
            },
            {
                "name": "Chatterbox Chieftain",
                "description": "Send a total of more than 50 transactions.",
                "success": False,
                "function": self._check_chatterbox_chieftain,
                "args": {
                    "public_key": public_key,
                },
            },
            {
                "name": "Transfer Titan",
                "description": "Participate in a total of more than 150 transactions, combining both sent and received.",
                "success": False,
                "function": self._check_transfer_titan,
                "args": {
                    "public_key": public_key,
                },
            },
            {
                "name": "Consistent Conductor",
                "description": "Had activity for at least three consecutive months.",
                "success": False,
                "function": self._check_consistent_conductor,
                "args": {
                    "public_key": public_key,
                },
            },
            {
                "name": "Consistent Creator",
                "description": "Had a minimum of 5 extrinsic activities every month for the past three months.",
                "success": False,
                "function": self._check_consistent_creator,
                "args": {
                    "public_key": public_key,
                },
            },
            {
                "name": "One-Tap Wonder",
                "description": "Kudos for executing your first extrinsic! Every blockchain saga starts with a single tap.",
                "success": False,
                "function": self._check_one_tap_wonder,
                "args": {
                    "public_key": public_key,
                },
            },
            {
                "name": "Extrinsics Explorer",
                "description": "Dive deep with over 10 extrinsics!",
                "success": False,
                "function": self._check_extrinsics_explorer,
                "args": {
                    "public_key": public_key,
                },
            },
            {
                "name": "Extrinsics Enthusiast",
                "description": "Show your passion with over 50 extrinsics!",
                "success": False,
                "function": self._check_extrinsics_enthusiast,
                "args": {
                    "public_key": public_key,
                },
            },
            {
                "name": "Extrinsics Expert",
                "description": "Elevate your status with over 100 extrinsics!",
                "success": False,
                "function": self._check_extrinsics_expert,
                "args": {
                    "public_key": public_key,
                },
            },
            {
                "name": "Extrinsics Emperor",
                "description": "Rule the extrinsics world with over 200 actions!",
                "success": False,
                "function": self._check_extrinsics_emperor,
                "args": {
                    "public_key": public_key,
                },
            },
        ]

        for badge in badges:
            try:
                badge["success"] = badge["function"](**badge["args"])
            except Exception as e:
                logger.error(f"Error while checking badge {badge['name']}: {e}")
                badge["success"] = False

        # return without args and function
        user_badges = [
            {
                "name": badge["name"],
                "description": badge["description"],
                "success": badge["success"],
            }
            for badge in badges
        ]
        return user_badges
