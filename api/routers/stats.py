from fastapi import (
    APIRouter,
)
from fastapi import Path, HTTPException, Query, Depends
from ..api import (
    db,
)

from enum import Enum
import pandas as pd
from api.api import STATS_CONTEXT, get_current_user
import tools.log_config as log_config
import os
import logging

current_file_path = os.path.abspath(__file__)
base_dir = os.path.dirname(current_file_path)
logger = logging.getLogger(__name__)

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
    dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "Transcation Relationship",
            "content": {
                "application/json": {
                    "example": {
                        "count": {
                            "senders": [
                                {
                                    "public_id": "0xd236a34f9153c72cce0f15683e6df4ce460b4bb802cf48befedc642335282231",
                                    "count": 2,
                                }
                            ],
                            "receivers": [
                                {
                                    "public_id": "0x6863783ba4351f8d949367832133632076c72a52aeec70eb6df7267cacf2c705",
                                    "count": 2,
                                }
                            ],
                        },
                        "amount": {
                            "senders": [
                                {
                                    "public_id": "0x6863783ba4351f8d949367832133632076c72a52aeec70eb6df7267cacf2c705",
                                    "amount": 4270000000000000,
                                }
                            ],
                            "receivers": [
                                {
                                    "public_id": "0x08f71d85d975397c55f57ab0b0198430a19d70a2306201f32da44ddf0174396b",
                                    "amount": 199890000000000,
                                }
                            ],
                        },
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
def transfer_relationship(
    public_key: str = Query(
        ...,
        title="Public Key",
        description="Public Key of the account to query",
    )
):
    data = STATS_CONTEXT.transfer_relationship(public_key=public_key)
    if data is None:
        raise HTTPException(status_code=204, detail="No content found.")
    return data


@router.get(
    "/recent-transfers",
    dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "Recent Transfers",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "0016794062-000042-d197a-from",
                            "transfer": {
                                "blockNumber": 16794062,
                                "timestamp": "2023-08-11T05:24:54.000000Z",
                                "extrinsicHash": "0x9f3482be21101eee9a7c1079ad9c81956255b3df133f37acc3b1905c3808fe9e",
                                "from": {
                                    "publicKey": "0x127a30e486492921e58f2564b36ab1ca21ff630672f0e76920edd601f8f2b89a"
                                },
                                "amount": "80000000000",
                                "success": True,
                                "to": {
                                    "publicKey": "0x447089372735261a916f7ad586fa24be192a40f2e0cf28a619ffa90806a63750"
                                },
                            },
                            "direction": "From",
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
def recent_transfers(
    public_key: str = Query(
        ...,
        title="Public Key",
        description="Public Key of the account to query",
    )
):
    data = STATS_CONTEXT.recent_transfers(public_key=public_key)
    if data is None:
        raise HTTPException(status_code=204, detail="No content found.")
    return data


@router.get(
    "/transfer-history",
    dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "Transfer History",
            "content": {
                "application/json": {
                    "example": {
                        "xAxis": {"type": "category", "data": ["2020-12-31", "2021-12-31", "2022-12-31", "2023-12-31"]},
                        "yAxis": {"type": "value"},
                        "series": [
                            {"name": "Incoming Transfers", "type": "line", "data": [32, 66, 17, 9]},
                            {"name": "Outgoing Transfers", "type": "line", "data": [10, 62, 9, 9]},
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
    dependencies=[Depends(get_current_user)],
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
def total_transfers(
    public_key: str = Query(
        ...,
        title="Public Key",
        description="Public Key of the account to query",
    )
):
    data = STATS_CONTEXT.total_transfers(public_key=public_key)
    if data is None:
        raise HTTPException(status_code=204, detail="No content found.")
    return data
