from fastapi import (
    APIRouter,
)
from fastapi import Path, HTTPException, Query, Depends
from ..api import (
    db,
)

from enum import Enum
import pandas as pd
from api.api import OVERVIEW_CONTEXT, StatsType, get_current_user
from tools.helpers import encode
import tools.log_config as log_config
import os
import logging

current_file_path = os.path.abspath(__file__)
base_dir = os.path.dirname(current_file_path)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/account",
    dependencies=[Depends(get_current_user)],
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

    data = OVERVIEW_CONTEXT.account(public_key=public_key, address=address)
    if data is None:
        raise HTTPException(status_code=204, detail="No content found.")

    return data


@router.get(
    "/balance-distribution",
    dependencies=[Depends(get_current_user)],
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

    data = OVERVIEW_CONTEXT.balance_distribution(public_key=public_key, address=address)
    if data is None:
        raise HTTPException(status_code=204, detail="No content found.")
    return data


@router.get(
    "/identity",
    dependencies=[Depends(get_current_user)],
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

    data = OVERVIEW_CONTEXT.identity(public_key=public_key, address=address)
    if data is None:
        raise HTTPException(status_code=204, detail="No content found.")
    return data


@router.get(
    "/balance-stats",
    dependencies=[Depends(get_current_user)],
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

    data = OVERVIEW_CONTEXT.balance_stats(public_key=public_key, address=address)
    if data is None:
        raise HTTPException(status_code=204, detail="No content found.")
    return data


@router.get(
    "/balance-history",
    dependencies=[Depends(get_current_user)],
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

    data = OVERVIEW_CONTEXT.balance_history(public_key=public_key, address=address)
    if data is None:
        raise HTTPException(status_code=204, detail="No content found.")
    return data
