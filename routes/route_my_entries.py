import logging.config
from typing import Annotated

from core import dict_config
from database import get_db
from dependencies import get_current_access_token, oauth2_scheme
from fastapi import APIRouter, Depends, status
from schemas import MyEntryOut
from sqlalchemy.ext.asyncio import AsyncSession
from src import cancel_user_entry, get_user_entries

router = APIRouter()

logging.config.dictConfig(dict_config)
main_log = logging.getLogger("route_logger")
main_log.setLevel(logging.DEBUG)


@router.get(
    "/cosmetology/my_entries",
    response_model=list[MyEntryOut],
    status_code=status.HTTP_200_OK,
    summary="Получить записи текущего пользователя.",
)
async def cosmetology_my_entries(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Роут получения всех записей текущего пользователя.
    """
    main_log.debug("Роут /cosmetology/my_entries получил запрос.")
    user_id = await get_current_access_token(token=token)
    entries = await get_user_entries(db=db, user_id=user_id)

    return [
        MyEntryOut(
            id=entry.id,
            procedure_id=entry.procedure_id,
            name_procedures=entry.procedure.name_procedures,
            price=entry.procedure.price,
            entry_date=entry.entry_date,
            entry_time=entry.entry_time,
        )
        for entry in entries
    ]


@router.delete(
    "/cosmetology/my_entries/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Отменить свою запись.",
)
async def cosmetology_cancel_my_entry(
    entry_id: int,
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Роут отмены собственной записи пользователем.
    """
    main_log.debug(
        "Роут /cosmetology/my_entries/%s получил запрос на отмену.", entry_id
    )
    user_id = await get_current_access_token(token=token)
    await cancel_user_entry(db=db, user_id=user_id, entry_id=entry_id)
