from fastapi import (
    APIRouter,
)
from fastapi import Path, HTTPException, Query, Depends
from ..api import (
    db,
)

from enum import Enum
import pandas as pd
from datetime import date
from datetime import datetime
from api.api import REWARDS_CONTEXT, StatsType, get_current_user
import tools.log_config as log_config
import os
import logging

current_file_path = os.path.abspath(__file__)
base_dir = os.path.dirname(current_file_path)
logger = logging.getLogger(__name__)

router = APIRouter()


class HistoryInterval(
    str,
    Enum,
):
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    YEAR = "YEAR"


@router.get(
    "/total-rewards",
    dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "Total Rewards",
            "content": {"application/json": {"example": {"total_amount": 258107.09219796103, "total_count": 1185}}},
        },
        204: {
            "description": "No content found.",
            "content": {"application/json": {"example": None}},
        },
        404: {
            "description": "Not found",
            "content": {"application/json": {"example": {"error": "Error description"}}},
        },
    },
)
def total_rewards(
    public_key: str = Query(
        ...,
        title="Public Key",
        description="Public Key of the account to query",
    )
):
    data = REWARDS_CONTEXT.total_rewards(public_key=public_key)
    if data is None:
        raise HTTPException(status_code=204, detail="No content found.")
    return data


@router.get(
    "/recent-rewards",
    dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "Recent Rewards",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "amount": 396.0418857039,
                            "id": "0017159773-000602-5d32e",
                            "timestamp": "2023-09-05T15:46:24.000000Z",
                            "validatorId": "0x127a30e486492921e58f2564b36ab1ca21ff630672f0e76920edd601f8f2b89a",
                            "era": 1189,
                        }
                    ]
                }
            },
        },
        204: {
            "description": "No content found.",
            "content": {"application/json": {"example": None}},
        },
        404: {
            "description": "Not found",
            "content": {"application/json": {"example": {"error": "Error description"}}},
        },
    },
)
def recent_rewards(
    public_key: str = Query(
        ...,
        title="Public Key",
        description="Public Key of the account to query",
    )
):
    data = REWARDS_CONTEXT.recent_rewards(public_key=public_key)
    if data is None:
        raise HTTPException(status_code=204, detail="No content found.")
    return data


@router.get(
    "/reward-history",
    dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "Reward History",
            "content": {
                "application/json": {
                    "example": {
                        "title": {"text": "Activity for YEAR"},
                        "xAxis": {"type": "category", "data": ["2020", "2021", "2022", "2023"]},
                        "yAxis": {"type": "value"},
                        "series": [{"data": [212, 361, 362, 250], "type": "line"}],
                    }
                }
            },
        },
        204: {
            "description": "No content found.",
            "content": {"application/json": {"example": None}},
        },
        404: {
            "description": "Not found",
            "content": {"application/json": {"example": {"error": "Error description"}}},
        },
    },
)
def reward_history(
    public_key: str = Query(
        ...,
        title="Public Key",
        description="Public Key of the account to query",
    ),
    interval: HistoryInterval = Query(
        ...,
        title="Interval",
        description="Interval to group the data",
    ),
):
    data = REWARDS_CONTEXT.rewards(public_key=public_key)
    if not data:
        raise HTTPException(
            status_code=204,
            detail="No content found.",
        )

    try:
        interval_enum = HistoryInterval(interval.upper())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid interval: {interval}. Valid values are: {', '.join([e.value for e in HistoryInterval])}",
        )

    df = pd.DataFrame(data)
    # Extract date from the timestamp and set as index
    df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.date
    df.set_index(pd.DatetimeIndex(df["timestamp"]), inplace=True)

    # Determine resampling frequency
    freq_map = {
        HistoryInterval.DAY: "D",
        HistoryInterval.WEEK: "W-MON",
        HistoryInterval.MONTH: "M",
        HistoryInterval.YEAR: "Y",
    }
    freq = freq_map[interval_enum]

    # Group the data
    grouped_data = df.resample(freq).size()

    # For non-year intervals, reindex to fill missing dates up to today
    if interval_enum != HistoryInterval.YEAR:
        today = datetime.utcnow().date()
        full_date_range = pd.date_range(start=grouped_data.index.min(), end=today, freq=freq)
        grouped_data = grouped_data.reindex(full_date_range, fill_value=0)

    echarts_data = {
        "title": {"text": f"Activity for {interval.value}"},
        "xAxis": {
            "type": "category",
            "data": grouped_data.index.strftime("%Y-%m-%d" if interval_enum != HistoryInterval.YEAR else "%Y").tolist(),
        },
        "yAxis": {"type": "value"},
        "series": [
            {
                "data": grouped_data.tolist(),
                "type": "line",
            }
        ],
    }

    return echarts_data


@router.get(
    "/reward-relationship",
    dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "Reward Relationship",
            "content": {
                "application/json": {
                    "example": {
                        "count": [
                            {
                                "validator_id": "0x127a30e486492921e58f2564b36ab1ca21ff630672f0e76920edd601f8f2b89a",
                                "count": 965,
                            }
                        ],
                        "amount": [
                            {
                                "validator_id": "0x127a30e486492921e58f2564b36ab1ca21ff630672f0e76920edd601f8f2b89a",
                                "amount": 223307.71742065522,
                            }
                        ],
                    }
                }
            },
        },
        204: {
            "description": "No content found.",
            "content": {"application/json": {"example": None}},
        },
        404: {
            "description": "Not found",
            "content": {"application/json": {"example": {"error": "Error description"}}},
        },
    },
)
def reward_relationship(
    public_key: str = Query(
        ...,
        title="Public Key",
        description="Public Key of the account to query",
    )
):
    data = REWARDS_CONTEXT.reward_relationship(public_key=public_key)
    if data is None:
        raise HTTPException(status_code=204, detail="No content found.")
    return data
