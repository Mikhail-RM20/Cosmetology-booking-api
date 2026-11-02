from typing import Annotated
import logging.config
from core import dict_config
from database import get_db
from dependencies import get_role_person
from fastapi import APIRouter, Depends
from schemas import Entries
from sqlalchemy.ext.asyncio import AsyncSession
from src import delete_entries

router = APIRouter()

logging.config.dictConfig(dict_config)
main_log = logging.getLogger("route_logger")
main_log.setLevel(logging.DEBUG)

@router.delete(
    "/cosmetology/delete_entries/{id_entry}", response_model=Entries
)
async def cosmetology_delete_entries(
    token: Annotated[str, Depends(get_role_person)],
    id_entry: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Роут удаления записи. Доступен только администратору.

    Args:
        token: str - Access - токен пользователя.
        id_entry: int - ID записи для удаления.
        db: AsyncSession - Асинхронная БД.

    Returns:
        Entries - Pydantic модель включающая в себя:
            id - ID записи.
            procedure_id - ID процедуры.
            entry_date - Дата записи процедуру.
            entry_time - Время записи на процедуру.
            name_user - Имя человека, записанного на процедуру.
            surname_user - Фамилия человека, записанного на процедуру.
            name_procedures - Название процедуры.
            price - Цена процедуры.

            Подробнее: /schemas/schemas_entry.py

    """
    main_log.debug(
        "Роут /cosmetology/delete_entries/%s получил запрос.",
        id_entry,
    )
    result = await delete_entries(db=db, id_entry=id_entry)

    main_log.debug(
        "Роут /cosmetology/delete_entries/%s"
        "успешно завершил свое выполнение.", id_entry
    )
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
