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
            "content": {
                "application/json": {
                    "example": {
                        "account_display": {
                            "account_index": "1Rs7u",
                            "address": "1REAJ1k691g5Eqqg9gL7vvZCBG7FCCZ8zgQkZWd4va5ESih",
                            "display": "Polkadot.pro - Realgar",
                            "identity": True,
                            "judgements": [{"index": 1, "judgement": "Reasonable"}],
                        },
                        "address": "1REAJ1k691g5Eqqg9gL7vvZCBG7FCCZ8zgQkZWd4va5ESih",
                        "assets_tag": ["Dolphin"],
                        "balance": "994504.7748730576",
                        "balance_lock": "765007.092197961",
                        "bonded": "7650070921979610",
                        "conviction_lock": "0",
                        "count_extrinsic": 171,
                        "delegate": None,
                        "democracy_lock": "0",
                        "display": "Polkadot.pro - Realgar",
                        "election_lock": "5941301477000000",
                        "email": "hello@polkadot.pro",
                        "evm_account": "",
                        "is_council_member": False,
                        "is_erc20": False,
                        "is_erc721": False,
                        "is_evm_contract": False,
                        "is_fellowship_member": False,
                        "is_module_account": False,
                        "is_registrar": False,
                        "is_techcomm_member": False,
                        "judgements": [{"index": 1, "judgement": "Reasonable"}],
                        "legal": "",
                        "lock": "765007.092197961",
                        "multisig": {},
                        "nonce": 171,
                        "proxy": {},
                        "registrar_info": None,
                        "reserved": "961730000000",
                        "riot": "@realgar:matrix.org",
                        "role": "validator",
                        "staking_info": {
                            "controller": "1ZMbuCR3QiatxRsQdNnJYgydn3CWV4PELcTzpH4TNoNjxno",
                            "controller_display": {
                                "account_index": "1bwSw",
                                "address": "1ZMbuCR3QiatxRsQdNnJYgydn3CWV4PELcTzpH4TNoNjxno",
                            },
                            "reward_account": "stash",
                        },
                        "stash": "1REAJ1k691g5Eqqg9gL7vvZCBG7FCCZ8zgQkZWd4va5ESih",
                        "substrate_account": None,
                        "twitter": "@propolkadot",
                        "unbonding": "0",
                        "vesting": None,
                        "web": "https://polkadot.pro",
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
            "content": {
                "application/json": {
                    "example": [
                        {
                            "network": "polkadot",
                            "symbol": "DOT",
                            "decimal": 10,
                            "price": "4.23",
                            "category": "native",
                            "balance": "9945047748730576",
                            "locked": "7650070921979610",
                            "reserved": "961730000000",
                            "bonded": "7650070921979610",
                            "unbonding": "0",
                            "democracy_lock": "0",
                            "conviction_lock": "0",
                            "election_lock": "5941301477000000",
                            "nomination_bonded": "0",
                            "token_unique_id": "DOT",
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
            "content": {
                "application/json": {
                    "example": [
                        {
                            "network": "polkadot",
                            "identity": True,
                            "display": "Polkadot.pro - Realgar",
                            "web": "https://polkadot.pro",
                            "riot": "@realgar:matrix.org",
                            "email": "hello@polkadot.pro",
                            "twitter": "@propolkadot",
                            "judgements": [{"index": 1, "judgement": "Reasonable"}],
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
            "content": {
                "application/json": {
                    "example": {
                        "max": "6499461.344248807452",
                        "min": "4181478.659808185101",
                        "prev24H": "4234921.41942042542",
                    }
                }
            },
        },
        204: {
            "description": "No content found.",
            "content": {
                "application/json": {
                    "example": [
                        {"value": "4234921.41942042542", "date": "2023-09-04"},
                        {"value": "4234921.638801681082", "date": "2023-09-05"},
                    ]
                }
            },
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
