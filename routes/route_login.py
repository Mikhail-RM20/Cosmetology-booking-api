from typing import Annotated
from core import dict_config
from database import get_db
from fastapi import APIRouter, Depends, status
from schemas import LogIn, LogOut
from sqlalchemy.ext.asyncio import AsyncSession
from src import login_user
import logging.config

router = APIRouter()

logging.config.dictConfig(dict_config)
main_log = logging.getLogger("route_logger")
main_log.setLevel(logging.DEBUG)

@router.post(
    "/cosmetology/login",
    response_model=LogOut,
    status_code=status.HTTP_201_CREATED,
)
async def cosmetology_login(
    login_user_info: LogIn,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Роут аутентификации.

    Args:
        login_user_info: LogIn - Pydantic модель, проверяет данные:
            phone: str - Номер телефона.
            password: str - Пароль пользователя.
        db: AsyncSession: Асинхронная БД.


    Returns:
        LogOut - Pydantic модель включающая в себя:
            access_token: str - Access - токен пользователя.
            refresh_token: str - Refresh - токен пользователя.

        status_code: 201 - успешное создание.

     Подробнее: /schemas/schemas_login.py
    """
    main_log.debug("Роут /cosmetology/login принял данные на вход.")
    access_token, refresh_token = await login_user(
        db=db, user_info=login_user_info
    )
    main_log.debug("Роут /cosmetology/login успешно завершил свое выполнение.")
    return LogOut(
        access_token=access_token,
        refresh_token=refresh_token
    )
