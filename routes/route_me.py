import logging.config
from typing import Annotated

from core import dict_config
from database import get_db
from dependencies import get_current_access_token, oauth2_scheme
from fastapi import APIRouter, Depends, status
from schemas import UserOut
from sqlalchemy.ext.asyncio import AsyncSession
from src import get_user_profile

router = APIRouter()

logging.config.dictConfig(dict_config)
main_log = logging.getLogger("route_logger")
main_log.setLevel(logging.DEBUG)


@router.get(
    "/cosmetology/me",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    summary="Получить профиль текущего пользователя.",
)
async def cosmetology_me(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Роут получения данных текущего авторизованного пользователя (включая роль).
    """
    main_log.debug("Роут /cosmetology/me получил запрос.")
    user_id = await get_current_access_token(token=token)
    user = await get_user_profile(db=db, user_id=user_id)

    return UserOut(
        id=user.id,
        name=user.name,
        surname=user.surname,
        phone=user.phone,
        email=user.email,
        role=user.role,
    )
