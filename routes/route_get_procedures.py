from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas import ProcedureOut
from dependencies import oauth2_scheme, get_current_access_token
from typing import Annotated, Optional
from src import get_procedures

router = APIRouter()

@router.get("/cosmetology/procedures", response_model=ProcedureOut, status_code=status.HTTP_200_OK)
async def cosmetology_procedures(
        token: Annotated[str, Depends(oauth2_scheme)],
        price: Optional[int] = None,
        db: AsyncSession = Depends(get_db)
):
    await get_current_access_token(token=token)
    all_procedures = await get_procedures(db=db, price=price)

    return [
        ProcedureOut(
            id=procedure["id"],
            name=procedure["name_procedure"],
            description=procedure["description"],
            price=procedure["price"]

    )
        for procedure in all_procedures
        ]
