from fastapi import (
    APIRouter,
)
from fastapi import (
    Path,
    HTTPException,
    Query,
    Depends,
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
from api.api import BADGES_CONTEXT, StatsType, get_current_user
import tools.log_config as log_config
import os
import logging

current_file_path = os.path.abspath(__file__)
base_dir = os.path.dirname(current_file_path)
logger = logging.getLogger(__name__)


router = APIRouter()


@router.get(
    "/check-badges",
    dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "Check Badges",
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
def check_badges(
    public_key: str = Query(
        ...,
        title="Public Key",
        description="Public Key of the account to query",
    )
):
    return BADGES_CONTEXT.check_badges(public_key=public_key)
