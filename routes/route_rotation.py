from typing import Annotated

from database import get_db
from fastapi import APIRouter, Depends, status
from schemas import LogOut, TokenRefreshIn
from sqlalchemy.ext.asyncio import AsyncSession
from utils import WorkTokens

router = APIRouter()
work_tokens = WorkTokens()


@router.post(
    "/cosmetology/rotation",
    response_model=LogOut,
    status_code=status.HTTP_201_CREATED,
)
async def cosmetology_rotation(
    token: TokenRefreshIn,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    access_token, refresh_token = await work_tokens.rotation_tokens(
        db=db, refresh_token=token.refresh_token
    )
    return LogOut(access_token=access_token, refresh_token=refresh_token)
