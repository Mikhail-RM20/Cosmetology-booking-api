from datetime import datetime
from typing import Annotated
import logging.config
from database import get_db
from dependencies import get_role_person
from fastapi import APIRouter, Depends, Query, status
from schemas import Entries
from sqlalchemy.ext.asyncio import AsyncSession
from src import get_entries
from core import dict_config
router = APIRouter()

logging.config.dictConfig(dict_config)
main_log = logging.getLogger("route_logger")
main_log.setLevel(logging.DEBUG)

@router.get(
    "/cosmetology/get_entries",
    response_model=list[Entries],
    status_code=status.HTTP_200_OK,
)
async def cosmetology_get_entries(
    token: Annotated[str, Depends(get_role_person)],
    db: Annotated[AsyncSession, Depends(get_db)],
    date: Annotated[datetime | None, Query(examples=["2026-09-10"])] = None,
):
    """
    Роут получения всех записей. Доступен только администратору.

    Args:
        token: str - Access - токен пользователя.
        db: AsyncSession - Асинхронная БД.
        date: datetime - Дата (опциональный параметр выборки).

    Returns:
        list[Entries] - Pydantic модель включающая в себя список записей:
            id - ID записи.
            procedure_id - ID процедуры.
            entry_date - Дата записи процедуру.
            entry_time - Время записи на процедуру.
            name_user - Имя человека, записанного на процедуру.
            surname_user - Фамилия человека, записанного на процедуру.
            name_procedures - Название процедуры.
            price - Цена процедуры.

            Подробнее: /schemas/schemas_entry.py

        status_code: 200 - успешно выполненный запрос.

    """
    main_log.debug("Роут /cosmetology/get_entries получил запрос.")
    results = await get_entries(db=db, entries_date=date)
    main_log.debug("Роут /cosmetology/get_entries успешно завершил работу.")
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
