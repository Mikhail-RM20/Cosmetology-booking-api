from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_role_person
from schemas import Entries

router = APIRouter()

@router.get("/cosmetology/get_entries", response_model=list[Entries], status_code=status.HTTP_200_OK)
async def cosmetology_get_entries(
        token: Annotated[str, Depends(get_role_person)],
        db: AsyncSession = Depends(get_db),
):
    pass