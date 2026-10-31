from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies import get_current_access_token, oauth2_scheme
from schemas import ProcedureOut
from src import get_procedures

router = APIRouter()


@router.get(
    "/cosmetology/procedures/{procedure_id}",
    response_model=ProcedureOut,
    status_code=status.HTTP_200_OK,
)
async def cosmetology_procedures(
    token: Annotated[str, Depends(oauth2_scheme)],
    procedure_id: int,
    db: AsyncSession = Depends(get_db),
):
    await get_current_access_token(token=token)

    procedure = await get_procedures(
        db=db,
        procedure_id=procedure_id,
    )

    return ProcedureOut(
        id=procedure["id"],
        name=procedure["name_procedure"],
        description=procedure["description"],
        price=procedure["price"],
    )
