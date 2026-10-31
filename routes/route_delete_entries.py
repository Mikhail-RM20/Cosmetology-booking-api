from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies import get_role_person
from schemas import Entries
from src import delete_entries

router = APIRouter()


@router.delete("/cosmetology/delete_entries/{id_entry}", response_model=Entries)
async def cosmetology_delete_entries(
    token: Annotated[str, Depends(get_role_person)],
    id_entry: int,
    db: AsyncSession = Depends(get_db),
):
    result = await delete_entries(db=db, id_entry=id_entry)

    return Entries(
        id=result["id"],
        procedure_id=result["procedure_id"],
        entry_date=result["entry_date"],
        entry_time=result["entry_time"],
        name_user=result["name_user"],
        surname_user=result["surname_user"],
        name_procedures=result["name_procedures"],
        price=result["price"],
    )
