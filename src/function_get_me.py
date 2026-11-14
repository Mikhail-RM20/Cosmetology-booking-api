import logging.config

from core import dict_config
from database import User
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

logging.config.dictConfig(dict_config)
main_log = logging.getLogger("services_logger")
main_log.setLevel(logging.DEBUG)


async def get_user_profile(db: AsyncSession, user_id: int) -> User:
    """
    Получает профиль пользователя по его ID.
    """
    main_log.debug(
        "Функция get_user_profile начала выполнение. user_id: %s.", user_id
    )
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user is None:
            main_log.warning(
                "Функция get_user_profile: пользователь с id %s не найден.",
                user_id,
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден.",
            )

        return user

    except SQLAlchemyError as error:
        main_log.exception(
            "Функция get_user_profile: ошибка БД при получении профиля."
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка базы данных.",
        ) from error
