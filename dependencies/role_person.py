from typing import Annotated
import logging.config
from core import dict_config
from database import User, get_db
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_current_access_token, oauth2_scheme

# Настройка логирования в файле.
logging.config.dictConfig(dict_config)
main_log = logging.getLogger("services_logger")
main_log.setLevel(logging.DEBUG)

async def get_role_person(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """
    Функция получения роли пользователя по токену.
    Необходима, чтобы обычный пользователь не смог выполнять действия админа.

    Args:
        token: str - Access - токен пользователя.
        db: AsyncSession - Асинхронная БД

    Returns:
        Функция ничего не возвращает, а лишь проводит проверку.
        В случае если роль пользователя не равна admin,
        то сервис выбросит исключение, иначе проверка пройдет.

    Raises:
        HTTPException - 401: Если роль не администратора.
        HTTPException - 500: При внутренней ошибке сервере или ошибки БД.

    """
    try:
        main_log.debug("Начало проверки переданного токена.")
        user_id = await get_current_access_token(token=token)

        main_log.debug("Успешная проверка на актуальность токена."
                       "Выполняется запрос к БД.")
        check_role = await db.execute(
            select(User).where(User.id == user_id, User.role == "admin")
        )
        result = check_role.scalar_one_or_none()

        if result is None:
            main_log.warning(
                "Пользователь с ID %s не является администратором.",
                user_id,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Это действие может выполнить только администратор.",
            )
    except SQLAlchemyError as error:
        main_log.error("Ошибка сервиса: %s", error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка БД.",
        ) from error
