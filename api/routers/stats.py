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
from api.api import STATS_CONTEXT

router = APIRouter()


class TransferInterval(
    str,
    Enum,
):
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    YEAR = "YEAR"


@router.get(
    "/transfer-relationship",
    # dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "Transcation Relationship",
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
def transaction_relationship(
    public_key: str = Query(
        ...,
        title="Public Key",
        description="Public Key of the account to query",
    )
):
    return STATS_CONTEXT.transfer_relationship(public_key=public_key)


@router.get(
    "/recent-transfers",
    # dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "Recent Transfers",
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
def recent_transfers(
    public_key: str = Query(
        ...,
        title="Public Key",
        description="Public Key of the account to query",
    )
):
    return STATS_CONTEXT.recent_transfers(public_key=public_key)


@router.get(
    "/top-transfers-by-count",
    # dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "Top Transfers",
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
def top_transfers_by_count(
    public_key: str = Query(
        ...,
        title="Public Key",
        description="Public Key of the account to query",
    )
):
    return STATS_CONTEXT.top_transfers_by_count(public_key=public_key)


@router.get(
    "/transfer-history",
    # dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "Transfer History",
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
def transfer_history(
    public_key: str = Query(
        ...,
        title="Public Key",
        description="Public Key of the account to query",
    ),
    interval: TransferInterval = Query(
        ...,
        title="Interval",
        description="Interval to group the data",
    ),
):
    data = STATS_CONTEXT.transfer_history(public_key=public_key)
    if not data:
        raise HTTPException(
            status_code=204,
            detail="No content found.",
        )

    try:
        interval_enum = TransferInterval(interval.upper())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid interval: {interval}. Valid values are: {', '.join([e.value for e in TransferInterval])}",
        )

    # Create a DataFrame directly from Series without having to convert or map
    df = pd.DataFrame(
        {
            "transfer_date": data["timestamps"],
            "Incoming Transfers": data["incoming_counts"],
            "Outgoing Transfers": data["outgoing_counts"],
        }
    )
    df["transfer_date"] = pd.to_datetime(df["transfer_date"])
    df.set_index("transfer_date", inplace=True)

    # Resample based on interval
    if interval_enum == TransferInterval.WEEK:
        df = df.resample("W-MON").sum()
    elif interval_enum == TransferInterval.MONTH:
        df = df.resample("M").sum()
    elif interval_enum == TransferInterval.YEAR:
        df = df.resample("Y").sum()

    chart_data = {
        "xAxis": {
            "type": "category",
            "data": df.index.strftime("%Y-%m-%d").tolist(),
        },
        "yAxis": {"type": "value"},
        "series": [
            {
                "name": "Incoming Transfers",
                "type": "line",
                "data": df["Incoming Transfers"].tolist(),
            },
            {
                "name": "Outgoing Transfers",
                "type": "line",
                "data": df["Outgoing Transfers"].tolist(),
            },
        ],
    }

    return chart_data


@router.get(
    "/total-transfers",
    # dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "Total Transfers",
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
def transaction_relationship(
    public_key: str = Query(
        ...,
        title="Public Key",
        description="Public Key of the account to query",
    )
):
    return STATS_CONTEXT.total_transfers(public_key=public_key)


# @router.get(
#     "/transfer-success-rate",
#     # dependencies=[Depends(get_current_user)],
#     responses={
#         200: {
#             "description": "Transfer Success Rate",
#             "content": {"application/json": {"example": None}},
#         },
#         204: {
#             "description": "No content found.",
#             "content": {"application/json": {"example": None}},
#         },
#         404: {
#             "description": "Not found",
#             "content": {"application/json": {"example": {"error": "Error description"}}},
#         },
#     },
# )
# def transfer_success_rate(
#     public_key: str = Query(
#         ...,
#         title="Public Key",
#         description="Public Key of the account to query",
#     )
# ):
#     return STATS_CONTEXT.transfer_success_rate(public_key=public_key)
