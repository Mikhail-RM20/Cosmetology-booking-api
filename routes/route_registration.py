import logging.config
from typing import Annotated

from core import dict_config
from database import get_db
from fastapi import APIRouter, Depends, status
from schemas import RegistrationIn, RegistrationOut
from sqlalchemy.ext.asyncio import AsyncSession
from src import create_new_user

router = APIRouter()


logging.config.dictConfig(dict_config)
main_log = logging.getLogger("route_logger")
main_log.setLevel(logging.DEBUG)


@router.post(
    "/cosmetology/registration",
    response_model=RegistrationOut,
    status_code=status.HTTP_201_CREATED,
)
async def cosmetology_registration(
    user_info: RegistrationIn,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Роут регистрации пользователя.

    Args:
        user_info: RegistrationIn - Pydantic модель включающая в себя:
            name: str - Имя пользователя.
            surname: str - Фамилия пользователя.
            phone: str - Телефон пользователя.
            password: str - Пароль пользователя.
            email: str - Email пользователя.

        db: AsyncSession - Асинхронная БД.

     Returns:
         RegistrationOut - Pydantic модель включающая в себя:
            1. Наследование модели RegistrationIn.
            2. message: str - сообщение о регистрации.

        Подробнее: /schemas/schemas_registration.py

        status_code: 201 - успешное создание.



    """
    main_log.debug("Роут /cosmetology/registration принял данные на вход.")
    new_user = await create_new_user(db=db, user_info=user_info)

    main_log.info(
        "Роут /cosmetology/registration успешно завершил свое выполнение. "
        f"Создан пользователь с id: {new_user}."
    )
    return RegistrationOut(
        message="Вы успешно зарегистрировались.", id_user=new_user
    )
