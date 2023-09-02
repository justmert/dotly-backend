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
from widgets.rewards import (
    Rewards,
    StatsType,
)
from enum import Enum
import pandas as pd

router = APIRouter()

REWARDS_CONTEXT = Rewards()

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
    data =  REWARDS_CONTEXT.rewards(public_key=public_key)
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

    print(data)
    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Use interval_enum instead of interval for checks
    if interval_enum == HistoryInterval.DAY:
        df["grouped_date"] = df["timestamp"].dt.date
    elif interval_enum == HistoryInterval.WEEK:
        df["grouped_date"] = df["timestamp"].dt.to_period("W").apply(lambda r: r.start_time.date())
    elif interval_enum == HistoryInterval.MONTH:
        df["grouped_date"] = df["timestamp"].dt.to_period("M").apply(lambda r: r.start_time.date())
    elif interval_enum == HistoryInterval.YEAR:
        df["grouped_date"] = df["timestamp"].dt.to_period("Y").apply(lambda r: r.start_time.date())

    grouped_data = df.groupby("grouped_date").size().reset_index(name="counts")

    echarts_data = {
        "title": {"text": f"Activity for {interval.value}"},
        "xAxis": {
            "type": "category",
            "data": grouped_data["grouped_date"].tolist(),
        },
        "yAxis": {"type": "value"},
        "series": [
            {
                "data": grouped_data["counts"].tolist(),
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

