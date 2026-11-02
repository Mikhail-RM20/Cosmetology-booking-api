from typing import Annotated
from core import dict_config
from database import get_db
from dependencies import get_current_access_token, oauth2_scheme
from fastapi import APIRouter, Depends, status
from schemas import ProcedureOut
from sqlalchemy.ext.asyncio import AsyncSession
from src import get_procedures
import logging.config

router = APIRouter()

logging.config.dictConfig(dict_config)
main_log = logging.getLogger("route_logger")
main_log.setLevel(logging.DEBUG)

@router.get(
    "/cosmetology/procedures/{procedure_id}",
    response_model=ProcedureOut,
    status_code=status.HTTP_200_OK,
)
async def cosmetology_procedures(
    token: Annotated[str, Depends(oauth2_scheme)],
    procedure_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Роут получения процедуры по ID.

    Args:
        token: str - Access - токен пользователя.
        procedure_id: int - ID категории (опциональный параметр)
        db: AsyncSession - Асинхронная БД.

    Returns:
        ProcedureOut - Pydantic модель включающая в себя:
            id - ID процедуры.
            name - Название процедуры.
            description - Описание процедуры.
            price - Цена за процедуру.

        Подробнее: /schemas/category.py
                   /schemas/schemas_procedure.py

      status_code: 200 - успешно выполненный запрос.

    """
    main_log.debug("Роут /cosmetology/procedures/%s получил запрос.", procedure_id)
    await get_current_access_token(token=token)

    procedure = await get_procedures(
        db=db,
        procedure_id=procedure_id,
    )

    main_log.debug("Роут /cosmetology/procedures/%s успешно завершил выполнение.", procedure_id)
    return ProcedureOut(
        id=procedure["id"],
        name=procedure["name_procedure"],
        description=procedure["description"],
        price=procedure["price"],
    )
