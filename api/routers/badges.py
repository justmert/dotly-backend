from fastapi import (
    APIRouter,
)
from fastapi import (
    Path,
    HTTPException,
)
from ..api import (
    db,
)

router = APIRouter()


@router.get(
    "/template",
    # dependencies=[Depends(get_current_user)],
    responses={
        200: {
            "description": "Full Time",
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
def template():
    """
    Template

    """

    return None
