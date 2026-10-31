from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies import oauth2_scheme
from schemas import LogOut
from utils import WorkTokens

router = APIRouter()
work_tokens = WorkTokens()


@router.post(
    "/cosmetology/rotation", response_model=LogOut, status_code=status.HTTP_201_CREATED
)
async def cosmetology_rotation(
    token: Annotated[str, Depends(oauth2_scheme)], db: AsyncSession = Depends(get_db)
):
    access_token, refresh_token = await work_tokens.rotation_tokens(
        db=db, refresh_token=token
    )
    return LogOut(access_token=access_token, refresh_token=refresh_token)
