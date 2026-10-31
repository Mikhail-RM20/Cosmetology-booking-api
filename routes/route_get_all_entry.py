from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies import get_role_person
from schemas import Entries
from src import get_entries

router = APIRouter()


@router.get(
    "/cosmetology/get_entries",
    response_model=list[Entries],
    status_code=status.HTTP_200_OK,
)
async def cosmetology_get_entries(
    token: Annotated[str, Depends(get_role_person)],
    date: datetime | None = Query(
        default=None,
        examples=["2026-09-10"],
    ),
    db: AsyncSession = Depends(get_db),
):
    results = await get_entries(db=db, entries_date=date)
    return [
        Entries(
            id=entry.id,
            procedure_id=entry.procedure_id,
            entry_date=entry.entry_date,
            entry_time=entry.entry_time,
            name_user=entry.user.name,
            surname_user=entry.user.surname,
            name_procedures=entry.procedure.name_procedures,
            price=entry.procedure.price,
        )
        for entry in results
    ]
