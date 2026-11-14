import logging.config
from typing import Annotated

from core import dict_config
from database import get_db
from fastapi import APIRouter, Depends, status
from schemas import LogOut, TokenRefreshIn
from sqlalchemy.ext.asyncio import AsyncSession
from utils import WorkTokens

router = APIRouter()
work_tokens = WorkTokens()

logging.config.dictConfig(dict_config)
main_log = logging.getLogger("route_logger")
main_log.setLevel(logging.DEBUG)


@router.post(
    "/cosmetology/rotation",
    response_model=LogOut,
    status_code=status.HTTP_201_CREATED,
)
async def cosmetology_rotation(
    token: TokenRefreshIn,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Роут обновления токенов пользователя.

    Args:
        token: TokenRefreshIn - Pydantic модель, проверяет данные:
            refresh_token: str - Refresh-токен пользователя.
        db: AsyncSession - Асинхронная БД.

    Returns:
        LogOut - Pydantic модель включающая в себя:
            access_token: str - Новый access-токен пользователя.
            refresh_token: str - Новый refresh-токен пользователя.

        status_code: 201 - успешное обновление токенов.

    Подробнее: /schemas/schemas_login.py
               /schemas/schemas_token.py
    """
    main_log.debug("Роут /cosmetology/rotation принял данные на вход.")
    access_token, refresh_token = await work_tokens.rotation_tokens(
        db=db, refresh_token=token.refresh_token
    )
    main_log.debug(
        "Роут /cosmetology/rotation успешно завершил свое выполнение."
    )
    return LogOut(access_token=access_token, refresh_token=refresh_token)
