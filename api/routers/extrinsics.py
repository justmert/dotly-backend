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

from enum import (
    Enum,
)
from datetime import (
    datetime,
    timedelta,
)
from collections import (
    defaultdict,
)
import pandas as pd
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
from api.api import EXTRINSICS_CONTEXT, ExtrinsicsType


router = APIRouter()


class ActivityInterval(
    str,
    Enum,
):
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    YEAR = "YEAR"


@router.get(
    "/activity",
    # dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "",
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
def extrinsics_activity(
    public_key: str = Query(
        ...,
        title="Public Key",
        description="Public Key of the account to query",
    ),
    interval: ActivityInterval = Query(
        ...,
        title="Interval",
        description="Interval to group the data",
    ),
):
    data = EXTRINSICS_CONTEXT.extrinsics(public_key)
    if not data:
        raise HTTPException(
            status_code=204,
            detail="No content found.",
        )

    try:
        interval_enum = ActivityInterval(interval.upper())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid interval: {interval}. Valid values are: {', '.join([e.value for e in ActivityInterval])}",
        )

    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.date
    df.set_index(pd.DatetimeIndex(df["timestamp"]), inplace=True)

    # Determine resampling frequency
    freq_map = {
        ActivityInterval.DAY: "D",
        ActivityInterval.WEEK: "W-MON",
        ActivityInterval.MONTH: "M",
        ActivityInterval.YEAR: "Y",
    }
    freq = freq_map[interval_enum]

    # Group the data
    grouped_data = df.resample(freq).size()

    # For non-year intervals, reindex to fill missing dates up to today
    if interval_enum != ActivityInterval.YEAR:
        today = datetime.utcnow().date()
        full_date_range = pd.date_range(start=grouped_data.index.min(), end=today, freq=freq)
        grouped_data = grouped_data.reindex(full_date_range, fill_value=0)

    echarts_data = {
        "title": {"text": f"Activity for {interval_enum.value}"},
        "xAxis": {
            "type": "category",
            "data": grouped_data.index.strftime(
                "%Y-%m-%d" if interval_enum != ActivityInterval.YEAR else "%Y"
            ).tolist(),
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
    "/distribution",
    # dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "Distribution data.",
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
def extrinsics_distribution(
    public_key: str,
):
    return EXTRINSICS_CONTEXT.distribution(public_key)


@router.get(
    "/top-interacted",
    # dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "Distribution data.",
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
def extrinsics_top_interacted_modules(
    public_key: str,
):
    return EXTRINSICS_CONTEXT.top_interacted(public_key)


@router.get(
    "/success-rate",
    # dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "The success rate of the extrinsics in pie chart format.",
            "content": {
                "application/json": {
                    "example": {
                        "legendData": [
                            "Successful",
                            "Failed",
                        ],
                        "seriesData": [
                            {
                                "name": "Successful",
                                "value": 1000,
                            },
                            {
                                "name": "Failed",
                                "value": 200,
                            },
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
def extrinsics_success_rate(
    public_key: str,
):
    data = EXTRINSICS_CONTEXT.extrinsics(public_key)

    if not data:
        raise HTTPException(
            status_code=204,
            detail="No content found.",
        )

    # Counting the number of successful and failed extrinsics
    successful_extrinsics = sum(1 for entry in data if entry["success"])
    failed_extrinsics = len(data) - successful_extrinsics

    # Preparing data for pie chart
    echarts_data = {
        "legendData": [
            "Successful",
            "Failed",
        ],
        "seriesData": [
            {
                "name": "Successful",
                "value": successful_extrinsics,
            },
            {
                "name": "Failed",
                "value": failed_extrinsics,
            },
        ],
    }

    return echarts_data


def group_by_interval(
    data,
    interval,
):
    result = defaultdict(int)

    for entry in data:
        timestamp = entry["timestamp"]
        dt = datetime.strptime(
            timestamp,
            "%Y-%m-%dT%H:%M:%S.%fZ",
        )
        if interval == ActivityInterval.DAY:
            key = dt.strftime("%Y-%m-%d")
        elif interval == ActivityInterval.WEEK:
            start = dt - timedelta(days=dt.weekday())
            end = start + timedelta(days=6)
            key = f"{start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}"
        elif interval == ActivityInterval.MONTH:
            key = dt.strftime("%Y-%m")
        elif interval == ActivityInterval.YEAR:
            key = dt.strftime("%Y")
        else:
            key = "unknown"

        result[key] += 1

    return [
        {
            "date": key,
            "count": value,
        }
        for key, value in result.items()
    ]


@router.get(
    "/call-activity",
    # dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "Call activity data.",
            "content": {
                "application/json": {
                    "example": {
                        "callActivity": [
                            {
                                "date": "2022-08",
                                "count": 10,
                            },
                            {
                                "date": "2022-09",
                                "count": 5,
                            },
                        ]
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
def extrinsics_call_activity(
    public_key: str,
    call_name: str,
    interval: ActivityInterval,
):
    data = EXTRINSICS_CONTEXT.extrinsics(public_key)

    if not data:
        raise HTTPException(
            status_code=204,
            detail="No content found.",
        )

    # Filtering data by the specified call name
    filtered_data = [entry for entry in data if entry["mainCall"]["callName"] == call_name]

    # Grouping data by the specified interval
    call_activity_data = group_by_interval(
        filtered_data,
        interval,
    )

    return {"callActivity": call_activity_data}


@router.get(
    "/transaction-rate",
    # dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "Transaction Rate",
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
def weekly_transaction_rate(
    public_key: str = Query(
        ...,
        title="Public Key",
        description="Public Key of the account to query",
    )
):
    return EXTRINSICS_CONTEXT.weekly_transaction_rate(public_key=public_key)


@router.get(
    "/total-extrinsics",
    # dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "Total Extrinsics",
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
def total_extrinsics(
    public_key: str = Query(
        ...,
        title="Public Key",
        description="Public Key of the account to query",
    )
):
    return EXTRINSICS_CONTEXT.total_extrinsics(public_key=public_key)


@router.get(
    "/recent-extrinsics",
    # dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "Recent Extrinsics",
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
def recent_extrinsics(
    public_key: str = Query(
        ...,
        title="Public Key",
        description="Public Key of the account to query",
    )
):
    return EXTRINSICS_CONTEXT.recent_extrinsics(public_key=public_key)
