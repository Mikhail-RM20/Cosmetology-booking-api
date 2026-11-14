import logging.config
import re

from core import dict_config, verify_password
from database import User
from fastapi import HTTPException, status
from schemas import LogIn
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

logging.config.dictConfig(dict_config)
main_log = logging.getLogger("services_logger")
main_log.setLevel(logging.DEBUG)


def mask_phone(phone: str) -> str:
    """
    Маскирует номер телефона для безопасного логирования.
    """
    digits = re.sub(r"\D", "", phone)

    if len(digits) < 4:
        return "***"

    return f"***{digits[-4:]}"


async def get_user_db(db: AsyncSession, user_info: LogIn) -> int:
    """
    Получает id пользователя по номеру телефона и проверяет пароль.

    Args:
        db: AsyncSession - Асинхронная сессия базы данных.
        user_info: LogIn - Pydantic модель, проверяет данные:
            phone: str - Номер телефона пользователя.
            password: str - Пароль пользователя.

    Returns:
        int - id пользователя, если аутентификация прошла успешно.

    Raises:
        HTTPException 401 - Пользователь не зарегистрирован.
        HTTPException 401 - Неверный пароль.
        HTTPException 500 - Ошибка базы данных.
    """
    phone_masked = mask_phone(user_info.phone)

    main_log.debug(
        "Функция get_user_db начала выполнение. "
        f"Получен запрос на аутентификацию. Телефон: {phone_masked}."
    )

    try:
        phone = user_info.phone
        password = user_info.password

        get_password = await db.execute(
            select(User).where(User.phone == phone)
        )
        result_get_password = get_password.scalar_one_or_none()

        if result_get_password is None:
            main_log.warning(
                "Функция get_user_db: пользователь не найден. "
                f"Телефон: {phone_masked}."
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не зарегистрирован.",
            )

        verify_check_password = verify_password(
            password, result_get_password.hash_password
        )

        if not verify_check_password:
            main_log.warning(
                "Функция get_user_db: введен неверный пароль. "
                f"Телефон: {phone_masked}."
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный пароль.",
            )

        main_log.debug(
            "Функция get_user_db успешно завершила свое выполнение. "
            f"Пользователь с id: {result_get_password.id} "
            f"успешно аутентифицирован. Телефон: {phone_masked}."
        )

        return result_get_password.id

    except SQLAlchemyError as error:
        main_log.exception(
            "Функция get_user_db: произошла ошибка базы данных "
            "при попытке аутентификации пользователя. "
            f"Телефон: {phone_masked}."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка базы данных.",
        ) from error
