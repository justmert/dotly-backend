from fastapi import (
    APIRouter,
)
from fastapi import (
    Path,
    HTTPException,
    Query,
)
from ..api import (
    db,
)

from enum import Enum
import pandas as pd
from datetime import date
from datetime import datetime
from api.api import REWARDS_CONTEXT, StatsType

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
    # dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "Total Rewards",
            "content": {"application/json": {"example": None}},
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
    return REWARDS_CONTEXT.total_rewards(public_key=public_key)


@router.get(
    "/recent-rewards",
    # dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "Recent Rewards",
            "content": {"application/json": {"example": None}},
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
    return REWARDS_CONTEXT.recent_rewards(public_key=public_key)


@router.get(
    "/reward-history",
    # dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "Reward History",
            "content": {"application/json": {"example": None}},
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
    # dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "Reward Relationship",
            "content": {"application/json": {"example": None}},
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
    return REWARDS_CONTEXT.reward_relationship(public_key=public_key)
