from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import  oauth2_scheme
from schemas import CategoryOut, ProcedureOut
from src.function_get_categories import get_categories_data
from dependencies import get_current_access_token
from database import get_db

router = APIRouter()


@router.get(
    "/cosmetology/categories",
    response_model=list[CategoryOut],
    status_code=status.HTTP_200_OK,
    summary="Получить категории с процедурами.",
)
async def get_categories(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
    category_id: Annotated[int | None, Query()] = None,
):
    await get_current_access_token(token=token)

    categories = await get_categories_data(
        db=db,
        category_id=category_id,
    )

    if not categories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категории не найдены.",
        )

    return [
        CategoryOut(
            id=category["id"],
            name=category["name"],
            procedures=[
                ProcedureOut(
                    id=procedure["id"],
                    name=procedure["name"],
                    description=procedure["description"],
                    price=procedure["price"],
                )
                for procedure in category["procedures"]
            ],
        )
        for category in categories
    ]