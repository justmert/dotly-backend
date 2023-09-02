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
from substrateinterface.utils.ss58 import ss58_encode
from api.api import OVERVIEW_CONTEXT, StatsType


router = APIRouter()


def encode(public_key):
    # Convert to address
    address = ss58_encode(public_key, 0)  # 0 is the SS58 format for Polkadot
    return address


@router.get(
    "/account",
    # dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "Account Info",
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
def account(
    public_key: str = Query(
        ...,
        title="Public Key",
        description="Public Key of the account to query",
    )
):
    # check if address is valid
    try:
        address = encode(public_key)
    except:
        raise HTTPException(status_code=404, detail="Invalid public key which cannot be encoded to address")

    return OVERVIEW_CONTEXT.account(public_key=public_key, address=address)


@router.get(
    "/balance-distribution",
    # dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "Balance Distribution",
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
def balance_distribution(
    public_key: str = Query(
        ...,
        title="Public Key",
        description="Public Key of the account to query",
    )
):
    # check if address is valid
    try:
        address = encode(public_key)
    except:
        raise HTTPException(status_code=404, detail="Invalid public key which cannot be encoded to address")

    return OVERVIEW_CONTEXT.balance_distribution(public_key=public_key, address=address)


@router.get(
    "/identity",
    # dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "Balance Distribution",
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
def identity(
    public_key: str = Query(
        ...,
        title="Public Key",
        description="Public Key of the account to query",
    )
):
    # check if address is valid
    try:
        address = encode(public_key)
    except:
        raise HTTPException(status_code=404, detail="Invalid public key which cannot be encoded to address")

    return OVERVIEW_CONTEXT.identity(public_key=public_key, address=address)


@router.get(
    "/balance-stats",
    # dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "Balance Stats",
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
def balance_stats(
    public_key: str = Query(
        ...,
        title="Public Key",
        description="Public Key of the account to query",
    )
):
    # check if address is valid
    try:
        address = encode(public_key)
    except:
        raise HTTPException(status_code=404, detail="Invalid public key which cannot be encoded to address")

    return OVERVIEW_CONTEXT.balance_stats(public_key=public_key, address=address)


@router.get(
    "/balance-history",
    # dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "Balance History",
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
def balance_history(
    public_key: str = Query(
        ...,
        title="Public Key",
        description="Public Key of the account to query",
    )
):
    # check if address is valid
    try:
        address = encode(public_key)
    except:
        raise HTTPException(status_code=404, detail="Invalid public key which cannot be encoded to address")

    return OVERVIEW_CONTEXT.balance_history(public_key=public_key, address=address)
