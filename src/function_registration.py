import logging.config

from core import dict_config, hash_password
from database import User
from fastapi import HTTPException, status
from schemas import RegistrationIn
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

logging.config.dictConfig(dict_config)
main_log = logging.getLogger("services_logger")
main_log.setLevel(logging.DEBUG)


async def create_new_user(db: AsyncSession, user_info: RegistrationIn) -> int:
    """
    Создает нового пользователя в базе данных.

    Args:
        db: AsyncSession - Асинхронная сессия базы данных.
        user_info: RegistrationIn - Pydantic модель, проверяет данные:
            name: str - Имя пользователя.
            surname: str - Фамилия пользователя.
            phone: str - Номер телефона пользователя.
            password: str - Пароль пользователя.
            email: str - Email пользователя.

    Returns:
        int - id созданного пользователя.

    Raises:
        HTTPException 409 - Пользователь с таким номером телефона
            уже зарегистрирован.
        HTTPException 500 - Ошибка базы данных.
    """
    main_log.debug(
        "Функция create_new_user начала выполнение. "
        "Получен запрос на регистрацию нового пользователя."
    )

    try:
        name = user_info.name.title()
        surname = user_info.surname.title()
        phone = user_info.phone
        password = user_info.password
        email = user_info.email

        database_query = await db.execute(
            select(User).where(User.phone == user_info.phone)
        )
        result_check_user = database_query.scalar_one_or_none()

        if result_check_user is not None:
            main_log.warning(
                "Функция create_new_user: пользователь с таким номером "
                "телефона уже зарегистрирован."
            )

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь с таким номером уже зарегистрирован.",
            )

        hashed_password = hash_password(password)

        new_user = User(
            name=name,
            surname=surname,
            phone=phone,
            role="user",
            hash_password=hashed_password,
            email=email,
        )

        db.add(new_user)
        await db.commit()

        main_log.debug(
            "Функция create_new_user успешно завершила свое выполнение. "
            f"Создан новый пользователь с id: {new_user.id}. "
            "Роль пользователя: user."
        )

        return new_user.id

    except SQLAlchemyError:
        await db.rollback()

        main_log.exception(
            "Функция create_new_user: произошла ошибка базы данных "
            "при регистрации нового пользователя."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка БД. / Database error.",
        )
