from fastapi import (
    APIRouter,
)
from fastapi import Path, HTTPException, Query, Depends
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
import pandas as pd
from api.api import EXTRINSICS_CONTEXT, ExtrinsicsType, get_current_user
import tools.log_config as log_config
import os
import logging

current_file_path = os.path.abspath(__file__)
base_dir = os.path.dirname(current_file_path)
logger = logging.getLogger(__name__)


router = APIRouter()


class ActivityInterval(
    str,
    Enum,
):
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    YEAR = "YEAR"


class CallActivityInterval(
    str,
    Enum,
):
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    YEAR = "YEAR"


@router.get(
    "/activity",
    dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "Extrinsics Activity",
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
            "description": "Extrinsics Distribution",
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
    public_key: str = Query(
        ...,
        title="Public Key",
        description="Public Key of the account to query",
    )
):
    data = EXTRINSICS_CONTEXT.distribution(public_key)
    if data is None:
        raise HTTPException(status_code=204, detail="No content found.")
    return data


@router.get(
    "/success-rate",
    dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "The success rate of the extrinsics",
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
    public_key: str = Query(
        ...,
        title="Public Key",
        description="Public Key of the account to query",
    )
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


@router.get(
    "/call-activity",
    # dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "Extrinsics call activity",
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
def extrinsics_call_activity(
    public_key: str = Query(..., title="Public Key", description="Public Key of the account to query"),
    call_name: str = Query(..., title="Call Name", description="Call name to filter the data"),
    interval: CallActivityInterval = Query(..., title="Interval", description="Interval to group the data"),
):
    data = EXTRINSICS_CONTEXT.extrinsics(public_key)

    if not data:
        raise HTTPException(
            status_code=204,
            detail="No content found.",
        )
    # Filtering data by the specified call name
    filtered_data = [entry for entry in data if entry["mainCall"]["callName"] == call_name]
    if len(filtered_data) == 0:
        raise HTTPException(
            status_code=204,
            detail=f"No content found for call name: {call_name}",
        )
    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.date
    df.set_index(pd.DatetimeIndex(df["timestamp"]), inplace=True)

    # Determine resampling frequency
    freq_map = {
        CallActivityInterval.DAY: "D",
        CallActivityInterval.WEEK: "W-MON",
        CallActivityInterval.MONTH: "M",
        CallActivityInterval.YEAR: "Y",
    }
    freq = freq_map[interval]

    # Group the data
    grouped_data = df.resample(freq).size()

    # For non-year intervals, reindex to fill missing dates up to today
    if interval != CallActivityInterval.YEAR:
        today = datetime.utcnow().date()
        full_date_range = pd.date_range(start=grouped_data.index.min(), end=today, freq=freq)
        grouped_data = grouped_data.reindex(full_date_range, fill_value=0)

    echarts_data = {
        "title": {"text": f"Activity for {interval.value}"},
        "xAxis": {
            "type": "category",
            "data": grouped_data.index.strftime("%Y-%m-%d" if interval != CallActivityInterval.YEAR else "%Y").tolist(),
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
    "/weekly-transaction-rate",
    dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "Extrinsics transaction rate",
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
    data = EXTRINSICS_CONTEXT.weekly_transaction_rate(public_key=public_key)
    if data is None:
        raise HTTPException(status_code=204, detail="No content found.")
    return data


@router.get(
    "/total-extrinsics",
    dependencies=[Depends(get_current_user)],
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
    data = EXTRINSICS_CONTEXT.total_extrinsics(public_key=public_key)
    if data is None:
        raise HTTPException(status_code=204, detail="No content found.")
    return data


@router.get(
    "/recent-extrinsics",
    dependencies=[Depends(get_current_user)],
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
    data = EXTRINSICS_CONTEXT.recent_extrinsics(public_key=public_key)
    if data is None:
        raise HTTPException(status_code=204, detail="No content found.")
    return data
