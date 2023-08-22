from fastapi import APIRouter
from fastapi import Path, HTTPException, Query
from ..api import db
from widgets.stats import Stats, StatsType

router = APIRouter()

STATS_CONTEXT = Stats()

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
def transaction_relationship(public_key: str = Query(..., title="Public Key", description="Public Key of the account to query")):
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
def recent_transfers(public_key: str = Query(..., title="Public Key", description="Public Key of the account to query")):
    return STATS_CONTEXT.recent_transfers(public_key=public_key)



@router.get(
    "/top-transfers",
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
def top_transfers(public_key: str = Query(..., title="Public Key", description="Public Key of the account to query")):
    return STATS_CONTEXT.top_transfers(public_key=public_key)



@router.get(
    "/transfer-direction",
    # dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "Transfer Direction",
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
def transaction_relationship(public_key: str = Query(..., title="Public Key", description="Public Key of the account to query")):
    return STATS_CONTEXT.transfer_direction(public_key=public_key)



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
def transaction_relationship(public_key: str = Query(..., title="Public Key", description="Public Key of the account to query")):
    return STATS_CONTEXT.total_transfers(public_key=public_key)


@router.get(
    "/transfer-success-rate",
    # dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "Transfer Success Rate",
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
def transfer_success_rate(public_key: str = Query(..., title="Public Key", description="Public Key of the account to query")):
    return STATS_CONTEXT.transfer_success_rate(public_key=public_key)



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
def total_rewards(public_key: str = Query(..., title="Public Key", description="Public Key of the account to query")):
    return STATS_CONTEXT.total_rewards(public_key=public_key)



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
def recent_rewards(public_key: str = Query(..., title="Public Key", description="Public Key of the account to query")):
    return STATS_CONTEXT.recent_rewards(public_key=public_key)



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
def reward_history(public_key: str = Query(..., title="Public Key", description="Public Key of the account to query")):
    return STATS_CONTEXT.reward_history(public_key=public_key)


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
def balance_history(public_key: str = Query(..., title="Public Key", description="Public Key of the account to query")):
    return STATS_CONTEXT.balance_history(public_key=public_key)