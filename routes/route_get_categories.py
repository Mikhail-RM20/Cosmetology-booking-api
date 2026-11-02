from typing import Annotated
import logging.config
from database import get_db
from dependencies import get_current_access_token, oauth2_scheme
from fastapi import APIRouter, Depends, HTTPException, Query, status
from schemas import CategoryOut, ProcedureOut
from sqlalchemy.ext.asyncio import AsyncSession
from src.function_get_categories import get_categories_data
from core import dict_config
router = APIRouter()

logging.config.dictConfig(dict_config)
main_log = logging.getLogger("route_logger")
main_log.setLevel(logging.DEBUG)

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
    """
    Роут получения категорий и процедур.

    Args:
        token: str - Access - токен пользователя.
        db: AsyncSession - Асинхронная БД.
        category_id: int - ID категории (опциональный параметр).

    Returns:

     list[CategoryOut]: Список категорий:
        Каждая категория содержит:
            - id: ID категории.
            - name: Название категории.
            - procedures: Список процедур категории.

        Каждая процедура содержит:
            - id: ID процедуры.
            - name: Название процедуры.
            - description: Описание процедуры.
            - price: Цена процедуры.

        Подробнее: /schemas/category.py
                   /schemas/schemas_procedure.py

      status_code: 200 - успешно выполненный запрос.

    """
    main_log.debug("Роут /cosmetology/categories получил запрос.")
    await get_current_access_token(token=token)

    categories = await get_categories_data(
        db=db,
        category_id=category_id,
    )

    if not categories:
        main_log.warning("Категории не найдены.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категории не найдены.",
        )

    main_log.debug("Роут /cosmetology/categories успешно завершил выполнение.")
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
