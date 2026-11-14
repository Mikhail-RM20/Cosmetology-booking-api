import logging.config
from typing import Annotated

from core import dict_config
from database import get_db
from dependencies import get_current_access_token, oauth2_scheme
from fastapi import APIRouter, Depends, status
from schemas import EntryIn, EntryOut
from sqlalchemy.ext.asyncio import AsyncSession
from src import new_entry

router = APIRouter()

logging.config.dictConfig(dict_config)
main_log = logging.getLogger("route_logger")
main_log.setLevel(logging.DEBUG)


@router.post(
    "/cosmetology/new_entry",
    response_model=EntryOut,
    status_code=status.HTTP_201_CREATED,
)
async def cosmetology_new_entry(
    entry_data: EntryIn,
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Роут создания новой записи.

    Args:
        entry_data: EntryIn - Pydantic модель включающая в себя:
            procedure_id: int - ID процедуры.
            entry_date: date - Дата записи на процедуру.
            entry_time: time - Время записи на процедуру.

        token: str - Access - токен пользователя.
        db: AsyncSession - Асинхронная БД.

    Returns:
        EntryOut - Pydantic модель включающая в себя:
    """
    main_log.debug("Получен запрос на создание записи в косметологии")
    user_id = await get_current_access_token(token=token)
    create_entry = await new_entry(
        db=db, entry_data=entry_data, id_user=user_id
    )

    main_log.info(
        "Создана запись в косметологии",
        extra={
            "user_id": user_id,
            "entry_id": create_entry.get("id"),
            "procedure_id": create_entry.get("procedure_id"),
            "entry_date": create_entry["entry_date"].isoformat(),
            "entry_time": create_entry["entry_time"].isoformat(),
        },
    )

    return EntryOut(
        message=f"{create_entry['user_name']} {create_entry['user_surname']}, вы записаны."
        f"\nПроцедура: {create_entry['procedure_name']}."
        f"\nДата: {create_entry['entry_date'].strftime('%d.%m.%Y')}."
        f"\nВремя: {create_entry['entry_time'].strftime('%H:%M')}."
        f"\n"
        f"\nС Уважением, Иван Игоревич."
    )
